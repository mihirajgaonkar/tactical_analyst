from tactical_analyst.analytics.registry import calculate_all_metrics
from tactical_analyst.evidence.builder import build_evidence_packet
from tactical_analyst.providers.soccer.capabilities import STATSBOMB_OPEN_DATA_CAPABILITIES
from tests.fixtures.analytics_sample import sample_context


def test_evidence_packet_contains_metrics_and_stable_hash() -> None:
    context = sample_context()
    metrics = calculate_all_metrics(context)

    first = build_evidence_packet(
        match={"match_id": context.match_id, "score": "2-1"},
        metrics=metrics,
        capabilities=STATSBOMB_OPEN_DATA_CAPABILITIES,
    )
    second = build_evidence_packet(
        match={"match_id": context.match_id, "score": "2-1"},
        metrics=metrics,
        capabilities=STATSBOMB_OPEN_DATA_CAPABILITIES,
    )

    assert first.evidence_hash == second.evidence_hash
    assert len(first.metrics) == len(metrics)
    assert any(metric.evidence_id.startswith("METRIC_XG_") for metric in first.metrics)
    assert first.capabilities["tracking"] is False
