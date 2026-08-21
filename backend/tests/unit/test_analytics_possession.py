from tactical_analyst.analytics.possession import PossessionMetrics
from tactical_analyst.analytics.transitions import TransitionMetrics
from tests.fixtures.analytics_sample import sample_context


def test_possession_sequences_group_provider_possession_ids() -> None:
    match_result = next(
        item
        for item in PossessionMetrics().calculate(sample_context())
        if item.entity_type == "match"
    )

    assert len(match_result.value_json["sequences"]) == 4
    first = match_result.value_json["sequences"][0]
    assert first["passes"] == 2
    assert first["shot"] is True
    assert first["goal"] is True


def test_transition_metrics_label_build_up_patterns() -> None:
    result = TransitionMetrics().calculate(sample_context())[0]

    assert sum(result.value_json["distribution"].values()) > 0
