from tactical_analyst.analytics.players import PlayerMetrics
from tactical_analyst.analytics.substitutions import SubstitutionMetrics
from tests.fixtures.analytics_sample import PLAYER_A1, sample_context


def test_player_metrics_emit_transparent_influence_features() -> None:
    result = next(
        item
        for item in PlayerMetrics().calculate(sample_context())
        if item.entity_id == PLAYER_A1
    )

    assert result.value_json["pass_involvement"] >= 2
    assert result.value_json["progressive_passes"] == 1
    assert result.value_json["shot_involvement"] == 1
    assert "on_ball_centrality" in result.value_json


def test_substitution_metrics_compare_pre_post_windows() -> None:
    results = SubstitutionMetrics().calculate(sample_context())

    assert len(results) == 1
    assert results[0].value_json["before"]["shots"] == 0
    assert results[0].value_json["after"]["shots"] == 1
