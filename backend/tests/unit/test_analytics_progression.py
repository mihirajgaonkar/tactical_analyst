from tactical_analyst.analytics.progression import ProgressionMetrics
from tests.fixtures.analytics_sample import TEAM_A, sample_context


def test_progression_counts_progressive_passes_and_carries() -> None:
    results = ProgressionMetrics().calculate(sample_context())

    progressive_passes = next(
        item
        for item in results
        if item.entity_id == TEAM_A and item.metric_name == "progressive_passes"
    )
    progressive_carries = next(
        item
        for item in results
        if item.entity_id == TEAM_A and item.metric_name == "progressive_carries"
    )
    assert progressive_passes.value_numeric == 2
    assert progressive_carries.value_numeric == 1
