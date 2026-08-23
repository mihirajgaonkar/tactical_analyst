from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from tactical_analyst.analytics.registry import calculate_all_metrics
from tactical_analyst.analytics.service import persist_metric_results
from tactical_analyst.config.settings import Settings, get_settings
from tactical_analyst.db.models import MatchModel, TeamModel
from tactical_analyst.db.repositories.context import load_match_context
from tactical_analyst.db.repositories.read import find_existing_report, list_metrics
from tactical_analyst.db.repositories.write import persist_tactical_report
from tactical_analyst.db.session import SessionLocal
from tactical_analyst.evidence.builder import build_evidence_packet
from tactical_analyst.graph.nodes import (
    final_numeric_verification_node,
    final_report_node,
    tactical_interpretation_node,
    verify_claims_node,
)
from tactical_analyst.graph.routing import route_after_verification
from tactical_analyst.ingestion.service import MatchIngestionService
from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.llm.service import LLMService
from tactical_analyst.providers.llm.factory import get_llm
from tactical_analyst.providers.soccer.statsbomb_open import StatsBombOpenDataProvider
from tactical_analyst.reliability.retry import RetryConfig
from tactical_analyst.schemas.evidence import EvidencePacket
from tactical_analyst.schemas.metric import MetricResult
from tactical_analyst.storage.local import LocalObjectStorage
from tactical_analyst.visualization.registry import render_all_visualizations


def ingest_match_pipeline(
    match_id: str,
    *,
    settings: Settings | None = None,
    session_factory=SessionLocal,
) -> dict[str, Any]:
    settings = settings or get_settings()
    with session_factory() as session:
        provider_match_id = _resolve_provider_match_id(session, match_id)
        provider = StatsBombOpenDataProvider(str(settings.statsbomb_open_data_base_url))
        storage = LocalObjectStorage(settings.object_storage_path)
        service = MatchIngestionService(provider, storage, session)
        result = asyncio.run(service.ingest_match(provider_match_id))
        return {"status": "completed", **asdict(result)}


def calculate_match_metrics_pipeline(
    match_id: str,
    *,
    settings: Settings | None = None,
    session_factory=SessionLocal,
) -> dict[str, Any]:
    settings = settings or get_settings()
    provider = StatsBombOpenDataProvider(str(settings.statsbomb_open_data_base_url))
    with session_factory() as session:
        context = load_match_context(session, match_id, capabilities=provider.capabilities())
        results = calculate_all_metrics(context)
        persist_metric_results(session, results)
        return {
            "match_id": match_id,
            "status": "completed",
            "metrics_calculated": len(results),
            "input_hash": context.resolved_input_hash(),
        }


def generate_match_visualizations_pipeline(
    match_id: str,
    *,
    settings: Settings | None = None,
    session_factory=SessionLocal,
) -> dict[str, Any]:
    settings = settings or get_settings()
    provider = StatsBombOpenDataProvider(str(settings.statsbomb_open_data_base_url))
    with session_factory() as session:
        context = load_match_context(session, match_id, capabilities=provider.capabilities())
        output_dir = Path(settings.object_storage_path) / "visualizations" / match_id
        assets = render_all_visualizations(context, output_dir)
        return {
            "match_id": match_id,
            "status": "completed",
            "visualizations_generated": len(assets),
            "assets": [asset.__dict__ for asset in assets],
        }


def run_tactical_analysis_pipeline(
    match_id: str,
    *,
    settings: Settings | None = None,
    session_factory=SessionLocal,
) -> dict[str, Any]:
    settings = settings or get_settings()
    provider = StatsBombOpenDataProvider(str(settings.statsbomb_open_data_base_url))
    with session_factory() as session:
        context = load_match_context(session, match_id, capabilities=provider.capabilities())
        metrics = _ensure_metrics(session, context)
        assets = render_all_visualizations(
            context,
            Path(settings.object_storage_path) / "visualizations" / match_id,
        )
        evidence_packet = build_evidence_packet(
            match=_match_metadata(session, match_id),
            metrics=metrics,
            capabilities=provider.capabilities(),
            visualization_assets=assets,
        )
        existing = find_existing_report(
            session,
            match_id=match_id,
            evidence_hash=evidence_packet.evidence_hash,
            prompt_version=settings.report_prompt_version,
            llm_provider=settings.llm_provider,
            llm_model=_configured_llm_model(settings),
        )
        if existing is not None:
            return {
                "match_id": match_id,
                "status": "completed",
                "report_id": existing.id,
                "reused_existing_report": True,
            }

        llm_service = _build_llm_service(settings)
        state = _run_verified_report_state(match_id, evidence_packet, llm_service, settings)
        if state.get("verification_errors"):
            return {
                "match_id": match_id,
                "status": "failed_verification",
                "errors": state["verification_errors"],
            }
        report = persist_tactical_report(
            session,
            match_id=match_id,
            evidence_packet=evidence_packet,
            interpretation=TacticalInterpretation.model_validate(state["interpretation"]),
            final_report=FinalReport.model_validate(state["report"]),
            llm_provider=settings.llm_provider,
            llm_model=_configured_llm_model(settings),
            prompt_version=settings.report_prompt_version,
        )
        return {
            "match_id": match_id,
            "status": "completed",
            "report_id": report.id,
            "evidence_hash": evidence_packet.evidence_hash,
        }


def _ensure_metrics(session: Session, context) -> list[MetricResult]:
    existing = list_metrics(session, context.match_id)
    if existing:
        return [
            MetricResult(
                id=row.id,
                match_id=row.match_id,
                entity_type=row.entity_type,
                entity_id=row.entity_id,
                metric_name=row.metric_name,
                metric_version=row.metric_version,
                value_numeric=row.value_numeric,
                value_json=row.value_json,
                sample_size=row.sample_size,
                source_event_ids=list(row.source_event_ids or []),
                window_start_ms=row.window_start_ms,
                window_end_ms=row.window_end_ms,
                input_hash=row.input_hash,
            )
            for row in existing
        ]
    results = calculate_all_metrics(context)
    persist_metric_results(session, results)
    return results


def _run_verified_report_state(
    match_id: str,
    evidence_packet: EvidencePacket,
    llm_service: LLMService,
    settings: Settings,
) -> dict[str, Any]:
    state: dict[str, Any] = {
        "match_id": match_id,
        "evidence_packet": evidence_packet.model_dump(),
        "verification_attempts": 0,
        "verification_errors": [],
    }
    state = tactical_interpretation_node(state, llm_service)
    while True:
        state = verify_claims_node(state)
        route = route_after_verification(state)
        if route == "valid":
            break
        if route == "invalid":
            return state
        state["verification_attempts"] = int(state.get("verification_attempts", 0)) + 1
        if state["verification_attempts"] > settings.max_claim_repair_attempts:
            return state
        state = tactical_interpretation_node(state, llm_service)
    state = final_report_node(state, llm_service)
    return final_numeric_verification_node(state)


def _build_llm_service(settings: Settings) -> LLMService:
    return LLMService(
        get_llm(settings),
        RetryConfig(
            max_attempts=settings.llm_max_retries,
            backoff_seconds=settings.llm_retry_backoff_seconds,
        ),
    )


def _match_metadata(session: Session, match_id: str) -> dict[str, Any]:
    match = session.get(MatchModel, match_id)
    if match is None:
        return {"match_id": match_id}
    home_team = session.get(TeamModel, match.home_team_id)
    away_team = session.get(TeamModel, match.away_team_id)
    return {
        "match_id": match.id,
        "home_team": {"id": match.home_team_id, "name": home_team.name if home_team else None},
        "away_team": {"id": match.away_team_id, "name": away_team.name if away_team else None},
        "home_score": match.home_score,
        "away_score": match.away_score,
        "score": f"{match.home_score}-{match.away_score}",
        "kickoff_at": match.kickoff_at.isoformat() if match.kickoff_at else None,
    }


def _resolve_provider_match_id(session: Session, match_id: str) -> str:
    match = session.get(MatchModel, match_id)
    if match is not None:
        return match.provider_match_id
    return match_id.rsplit(":", 1)[-1]


def _configured_llm_model(settings: Settings) -> str:
    if settings.llm_provider == "gemini":
        return settings.gemini_model
    return settings.llm_provider
