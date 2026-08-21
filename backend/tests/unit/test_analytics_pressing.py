from tactical_analyst.analytics.pressing import PressingMetrics
from tests.fixtures.analytics_sample import TEAM_A, sample_context


def test_pressing_calculates_ppda_high_turnovers_and_action_height() -> None:
    results = PressingMetrics().calculate(sample_context())

    ppda = next(item for item in results if item.entity_id == TEAM_A and item.metric_name == "ppda")
    high_turnovers = next(
        item
        for item in results
        if item.entity_id == TEAM_A and item.metric_name == "high_turnovers"
    )
    defensive_height = next(
        item
        for item in results
        if item.entity_id == TEAM_A and item.metric_name == "defensive_action_height"
    )

    assert ppda.value_numeric == 2.0
    assert high_turnovers.value_numeric == 1
    assert high_turnovers.value_json["leading_to_shot"] == 1
    assert defensive_height.value_numeric == 58.0
