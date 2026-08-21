from tactical_analyst.analytics.territory import TerritoryMetrics
from tests.fixtures.analytics_sample import TEAM_A, TEAM_B, sample_context


def test_territory_counts_field_tilt_entries_and_box_entries() -> None:
    results = TerritoryMetrics().calculate(sample_context())

    field_tilt_a = next(
        item for item in results if item.entity_id == TEAM_A and item.metric_name == "field_tilt"
    )
    field_tilt_b = next(
        item for item in results if item.entity_id == TEAM_B and item.metric_name == "field_tilt"
    )
    entries = next(
        item
        for item in results
        if item.entity_id == TEAM_A and item.metric_name == "final_third_entries"
    )
    box_entries = next(
        item for item in results if item.entity_id == TEAM_A and item.metric_name == "box_entries"
    )

    assert field_tilt_a.value_numeric == 1.0
    assert field_tilt_b.value_numeric == 0.0
    assert entries.value_numeric == 2
    assert box_entries.value_numeric == 2
