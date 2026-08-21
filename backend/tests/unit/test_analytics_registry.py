from tactical_analyst.analytics.registry import calculate_all_metrics
from tests.fixtures.analytics_sample import sample_context


def test_registry_calculates_all_metric_groups() -> None:
    results = calculate_all_metrics(sample_context())
    metric_names = {result.metric_name for result in results}

    assert "shots" in metric_names
    assert "passing_network" in metric_names
    assert "progressive_passes" in metric_names
    assert "field_tilt" in metric_names
    assert "ppda" in metric_names
    assert "possession_sequences" in metric_names
    assert "build_up_patterns" in metric_names
    assert "attacking_zones" in metric_names
    assert "player_influence_features" in metric_names
    assert "substitution_impact" in metric_names
