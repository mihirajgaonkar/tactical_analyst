import json
import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tactical_analyst.cache.keys import (
    match_metrics_key,
    report_cache_key,
    stable_payload_hash,
)
from tactical_analyst.cache.local import InMemoryCache
from tactical_analyst.db.models import Base, TacticalReportModel
from tactical_analyst.db.repositories.read import find_existing_report
from tactical_analyst.llm.schemas import TacticalInterpretation
from tactical_analyst.llm.service import LLMService
from tactical_analyst.reliability.logging import log_analysis_event
from tactical_analyst.reliability.retry import RetryConfig, retry_call
from tactical_analyst.workers.jobs import CeleryJobClient, LocalJobClient


def test_cache_keys_and_payload_hash_are_stable() -> None:
    assert match_metrics_key("match:1", "analytics_v1") == "match:match:1:metrics:analytics_v1"
    assert (
        report_cache_key("match:1", "hash", "v1", "gemini")
        == "report:match:1:hash:v1:gemini"
    )
    assert stable_payload_hash({"b": 2, "a": 1}) == stable_payload_hash({"a": 1, "b": 2})


def test_in_memory_cache_respects_ttl() -> None:
    cache = InMemoryCache()
    cache.set("a", 1)
    assert cache.get("a") == 1
    cache.set("b", 2, ttl_seconds=0)
    assert cache.get("b") is None


def test_retry_call_retries_transient_failures() -> None:
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("temporary")
        return "ok"

    assert retry_call(flaky, RetryConfig(max_attempts=2, backoff_seconds=0)) == "ok"
    assert calls["count"] == 2


def test_local_job_client_uses_idempotency_key() -> None:
    client = LocalJobClient()
    first = client.enqueue("task", "match:1", idempotency_key="analysis:match:1")
    second = client.enqueue("task", "match:1", idempotency_key="analysis:match:1")

    assert first.job_id == second.job_id


def test_celery_job_client_does_not_forward_idempotency_metadata() -> None:
    celery_app = RecordingCeleryApp()
    client = CeleryJobClient(celery_app)

    queued = client.enqueue("task", "match:1", idempotency_key="analysis:match:1")

    assert queued.job_id == "job:1"
    assert celery_app.sent == ("task", ("match:1",), {})


def test_llm_service_retries_structured_output_calls() -> None:
    model = FlakyStructuredModel()
    service = LLMService(FlakyChatModel(model), RetryConfig(max_attempts=2, backoff_seconds=0))

    result = service.interpret(_evidence_packet())

    assert result.match_summary == "Recovered"
    assert model.calls == 2


def test_llm_service_compacts_raw_event_ids_in_prompt() -> None:
    model = CapturingStructuredModel()
    service = LLMService(FlakyChatModel(model))
    packet = _evidence_packet()
    packet.metrics[0].source_event_ids = ["event:1", "event:2"]

    service.interpret(packet)

    assert '"source_event_count": 2' in model.prompt
    assert "event:1" not in model.prompt


def test_llm_service_keeps_only_shot_possessions_in_prompt() -> None:
    from tactical_analyst.schemas.evidence import EvidenceMetric

    model = CapturingStructuredModel()
    service = LLMService(FlakyChatModel(model))
    packet = _evidence_packet()
    packet.metrics.extend(
        [
            EvidenceMetric(
                evidence_id="ROUTINE_POSSESSION",
                metric="possession_sequences",
                entity_type="possession",
                entity_id="1",
                value={"shot": False},
                definition_version="v1",
            ),
            EvidenceMetric(
                evidence_id="SHOT_POSSESSION",
                metric="possession_sequences",
                entity_type="possession",
                entity_id="2",
                value={"shot": True},
                definition_version="v1",
            ),
        ]
    )

    service.interpret(packet)

    assert "SHOT_POSSESSION" in model.prompt
    assert "ROUTINE_POSSESSION" not in model.prompt


def test_duplicate_report_lookup_by_evidence_hash() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            TacticalReportModel(
                id="report:1",
                match_id="match:1",
                report_version="v1",
                evidence_hash="hash",
                llm_provider="gemini",
                llm_model="gemini-2.5-flash",
                prompt_version="v1",
                report_json={},
                report_markdown="Report",
                verification_status="passed",
            )
        )
        session.commit()

        report = find_existing_report(
            session,
            match_id="match:1",
            evidence_hash="hash",
            prompt_version="v1",
            llm_provider="gemini",
            llm_model="gemini-2.5-flash",
        )

    assert report is not None
    assert report.id == "report:1"


def test_structured_analysis_log(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.analysis")
    caplog.set_level(logging.INFO, logger="test.analysis")

    log_analysis_event(
        logger,
        "analysis_completed",
        job_id="job:1",
        match_id="match:1",
        evidence_hash="hash",
    )

    payload = json.loads(caplog.records[0].message)
    assert payload["event"] == "analysis_completed"
    assert payload["job_id"] == "job:1"


class FlakyStructuredModel:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, prompt: str) -> TacticalInterpretation:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary")
        return TacticalInterpretation(match_summary="Recovered", claims=[])


class FlakyChatModel:
    def __init__(self, model: FlakyStructuredModel) -> None:
        self.model = model

    def with_structured_output(self, schema):
        return self.model


class CapturingStructuredModel:
    def __init__(self) -> None:
        self.prompt = ""

    def invoke(self, prompt: str) -> TacticalInterpretation:
        self.prompt = prompt
        return TacticalInterpretation(match_summary="Captured", claims=[])


class RecordingCeleryApp:
    def __init__(self) -> None:
        self.sent = None

    def send_task(self, task_name, *, args, kwargs):
        self.sent = (task_name, args, kwargs)
        return type("Result", (), {"id": "job:1"})()


def _evidence_packet():
    from tactical_analyst.schemas.evidence import EvidenceMetric, EvidencePacket

    return EvidencePacket(
        match={"match_id": "match:1"},
        metrics=[
            EvidenceMetric(
                evidence_id="METRIC_XG_TEAM_A",
                metric="xg",
                entity_type="team",
                entity_id="team:a",
                value=1.2,
                definition_version="xg_v1",
            )
        ],
        capabilities={"tracking": False, "freeze_frames_360": False},
        evidence_hash="hash",
    )
