from tactical_analyst.evaluation.dataset import load_evaluation_matches
from tactical_analyst.evaluation.evaluator import evaluate_final_report, evaluate_interpretation
from tactical_analyst.llm.schemas import FinalReport, TacticalClaim, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidenceMetric, EvidencePacket


def test_evaluation_manifest_has_at_least_ten_matches() -> None:
    matches = load_evaluation_matches()

    assert len(matches) >= 10
    assert all(item["provider"] == "statsbomb_open" for item in matches)


def test_evaluator_acceptance_criteria_pass_for_grounded_claims() -> None:
    packet = _packet()
    interpretation = TacticalInterpretation(
        match_summary="Team A had 1.2 xG.",
        claims=[
            TacticalClaim(
                claim_id="c1",
                topic="shots",
                claim="Team A had 1.2 xG.",
                evidence_ids=["METRIC_XG_TEAM_A"],
                strength="weak",
            )
        ],
    )
    report = FinalReport(title="Report", sections=[], markdown="Team A had 1.2 xG.")

    interpretation_result = evaluate_interpretation(interpretation, packet)
    report_result = evaluate_final_report(report, packet)

    assert interpretation_result.passed is True
    assert report_result.passed is True


def test_evaluator_counts_release_blockers() -> None:
    packet = _packet()
    interpretation = TacticalInterpretation(
        match_summary="Team A had 9.9 xG and compactness.",
        claims=[
            TacticalClaim(
                claim_id="c1",
                topic="shots",
                claim="Team A had 9.9 xG and compactness.",
                evidence_ids=["UNKNOWN"],
                strength="moderate",
            )
        ],
    )

    result = evaluate_interpretation(interpretation, packet)

    assert result.passed is False
    assert result.unsupported_numeric_claims >= 1
    assert result.unknown_evidence_references >= 1
    assert result.unavailable_metric_claims >= 1


def _packet() -> EvidencePacket:
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
