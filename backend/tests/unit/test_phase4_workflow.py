from tactical_analyst.analytics.registry import calculate_all_metrics
from tactical_analyst.graph.workflow import TacticalAnalysisWorkflow
from tactical_analyst.llm.schemas import FinalReport, TacticalClaim, TacticalInterpretation
from tactical_analyst.providers.soccer.capabilities import STATSBOMB_OPEN_DATA_CAPABILITIES
from tests.fixtures.analytics_sample import sample_context


class FakeLLMService:
    def __init__(self, interpretations: list[TacticalInterpretation]) -> None:
        self.interpretations = interpretations
        self.calls = 0

    def interpret(self, evidence_packet):
        value = self.interpretations[min(self.calls, len(self.interpretations) - 1)]
        self.calls += 1
        return value

    def final_report(self, evidence_packet, interpretation):
        return FinalReport(
            title="Verified report",
            sections=[],
            markdown="Verified report with 3 shots.",
        )


def _state():
    context = sample_context()
    return {
        "job_id": "job-1",
        "match_id": context.match_id,
        "match": {"match_id": context.match_id},
        "provider": "statsbomb_open",
        "provider_capabilities": STATSBOMB_OPEN_DATA_CAPABILITIES.model_dump(),
        "metric_results": [metric.model_dump() for metric in calculate_all_metrics(context)],
        "visualization_assets": [],
        "verification_attempts": 0,
        "errors": [],
    }


def test_workflow_happy_path_persists_verified_report() -> None:
    state = _state()
    evidence_id = state["metric_results"][0]["id"]
    # Workflow evidence IDs are rebuilt from metric rows.
    valid_claim = TacticalClaim(
        claim_id="c1",
        topic="shots",
        claim="The match evidence includes shot output.",
        evidence_ids=["METRIC_SHOTS_TEAM_A"],
        strength="weak",
    )
    llm = FakeLLMService([TacticalInterpretation(match_summary="Summary", claims=[valid_claim])])

    result = TacticalAnalysisWorkflow(llm).run(state)

    assert evidence_id
    assert result["report_persisted"] is True
    assert result["report_markdown"] == "Verified report with 3 shots."
    assert result["verification_errors"] == []


def test_workflow_repairs_unknown_evidence_claim() -> None:
    bad = TacticalClaim(
        claim_id="bad",
        topic="shots",
        claim="Unsupported.",
        evidence_ids=["UNKNOWN"],
        strength="weak",
    )
    good = TacticalClaim(
        claim_id="good",
        topic="shots",
        claim="Supported.",
        evidence_ids=["METRIC_SHOTS_TEAM_A"],
        strength="weak",
    )
    llm = FakeLLMService(
        [
            TacticalInterpretation(match_summary="Bad", claims=[bad]),
            TacticalInterpretation(match_summary="Good", claims=[good]),
        ]
    )

    result = TacticalAnalysisWorkflow(llm).run(_state())

    assert result["report_persisted"] is True
    assert llm.calls == 2


def test_workflow_stops_after_repair_limit() -> None:
    bad = TacticalClaim(
        claim_id="bad",
        topic="shots",
        claim="Unsupported.",
        evidence_ids=["UNKNOWN"],
        strength="weak",
    )
    llm = FakeLLMService([TacticalInterpretation(match_summary="Bad", claims=[bad])])

    result = TacticalAnalysisWorkflow(llm, max_repair_attempts=1).run(_state())

    assert "report_persisted" not in result
    assert result["verification_errors"]
