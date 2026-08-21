from tactical_analyst.analytics.passing import PassingMetrics
from tests.fixtures.analytics_sample import PLAYER_A1, PLAYER_A2, TEAM_A, sample_context


def test_passing_network_counts_edges_and_degree() -> None:
    result = next(
        item
        for item in PassingMetrics().calculate(sample_context())
        if item.entity_id == TEAM_A
    )

    edges = result.value_json["edges"]
    assert {"passer_id": PLAYER_A1, "receiver_id": PLAYER_A2, "completed_passes": 1} in edges
    assert result.value_json["pass_volume"][PLAYER_A1] == 1
    assert result.value_json["weighted_degree"][PLAYER_A1] == 2
