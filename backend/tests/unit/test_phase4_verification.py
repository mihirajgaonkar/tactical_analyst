from tactical_analyst.analytics.registry import calculate_all_metrics
from tactical_analyst.evidence.builder import build_evidence_packet
from tactical_analyst.llm.schemas import FinalReport, TacticalClaim, TacticalInterpretation
from tactical_analyst.providers.soccer.capabilities import STATSBOMB_OPEN_DATA_CAPABILITIES
from tactical_analyst.verification.claim_verifier import verify_claim_evidence
from tactical_analyst.verification.coverage_verifier import verify_capability_coverage
from tactical_analyst.verification.numeric_verifier import verify_report_numbers
from tests.fixtures.analytics_sample import sample_context


def _packet():
    context = sample_context()
    return build_evidence_packet(
        match={"match_id": context.match_id},
        metrics=calculate_all_metrics(context),
        capabilities=STATSBOMB_OPEN_DATA_CAPABILITIES,
    )


def test_claim_verifier_rejects_unknown_evidence_id() -> None:
    interpretation = TacticalInterpretation(
        match_summary="Summary",
        claims=[
            TacticalClaim(
                claim_id="c1",
                topic="pressing",
                claim="Team pressed well.",
                evidence_ids=["DOES_NOT_EXIST"],
                strength="moderate",
            )
        ],
    )

    assert verify_claim_evidence(interpretation, _packet())


def test_numeric_verifier_rejects_invented_number() -> None:
    report = FinalReport(
        title="Report",
        sections=[],
        markdown="Team A produced 999 xG.",
    )

    errors = verify_report_numbers(report, _packet())

    assert errors == ["Unsupported numeric value: 999"]


def test_numeric_verifier_ignores_identifiers_and_understands_score_separator() -> None:
    packet = _packet()
    packet.match.update({"home_score": 3, "away_score": 3})
    report = FinalReport(
        title="Report",
        sections=[],
        markdown=(
            "Argentina (statsbomb:779) drew 3-3. "
            "Evidence METRIC_SHOTS_TEAM_779 and event "
            "6e81c350-5788-4f84-891a-92db9bfbf0db support the claim. "
            "METRIC_SUBSTITUTION_IMPACT_6E81C350-5788-4F84-891A-92DB9BFBF0DB "
            "is also an identifier."
        ),
    )

    assert verify_report_numbers(report, packet) == []


def test_coverage_verifier_rejects_tracking_only_language_without_tracking() -> None:
    packet = _packet()
    interpretation = TacticalInterpretation(
        match_summary="Summary",
        claims=[
            TacticalClaim(
                claim_id="c1",
                topic="defending",
                claim="The team held a compactness advantage.",
                evidence_ids=[packet.metrics[0].evidence_id],
                strength="weak",
            )
        ],
    )

    assert verify_capability_coverage(interpretation, packet)
