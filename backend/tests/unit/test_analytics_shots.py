from tactical_analyst.analytics.shots import ShotMetrics
from tests.fixtures.analytics_sample import TEAM_A, sample_context


def test_shot_metrics_calculate_known_team_values() -> None:
    result = next(
        item
        for item in ShotMetrics().calculate(sample_context())
        if item.entity_id == TEAM_A and item.metric_name == "shots"
    )

    assert result.value_json["shots"] == 3
    assert result.value_json["goals"] == 1
    assert result.value_json["shots_on_target"] == 3
    assert result.value_json["xg"] == 0.7
    assert result.value_json["xg_per_shot"] == 0.2333
    assert result.value_json["big_chances"] == 1
