from tactical_analyst.analytics.tracking import (
    TrackingContext,
    calculate_all_tracking_metrics,
)
from tactical_analyst.schemas.tracking import (
    TrackingFrame,
    TrackingPlayerFrame,
    TrackingProviderCapabilities,
)


def test_tracking_shape_metrics_use_true_player_locations() -> None:
    context = TrackingContext(
        match_id="match:tracking",
        team_ids=("team:a", "team:b"),
        capabilities=TrackingProviderCapabilities(true_player_positions=True),
        input_hash="tracking-hash",
        frames=[
            TrackingFrame(
                match_id="match:tracking",
                frame_id="frame-1",
                period=1,
                timestamp_ms=1000,
                players=[
                    TrackingPlayerFrame(player_id="a1", team_id="team:a", x=20, y=20),
                    TrackingPlayerFrame(player_id="a2", team_id="team:a", x=40, y=50),
                    TrackingPlayerFrame(player_id="b1", team_id="team:b", x=65, y=25),
                    TrackingPlayerFrame(player_id="b2", team_id="team:b", x=80, y=45),
                ],
            ),
            TrackingFrame(
                match_id="match:tracking",
                frame_id="frame-2",
                period=1,
                timestamp_ms=2000,
                players=[
                    TrackingPlayerFrame(player_id="a1", team_id="team:a", x=25, y=22),
                    TrackingPlayerFrame(player_id="a2", team_id="team:a", x=45, y=52),
                    TrackingPlayerFrame(player_id="b1", team_id="team:b", x=60, y=20),
                    TrackingPlayerFrame(player_id="b2", team_id="team:b", x=85, y=48),
                ],
            ),
        ],
    )

    metrics = {metric.id: metric for metric in calculate_all_tracking_metrics(context)}

    assert metrics[
        "match:tracking:team:team:a:team_width:tracking_shape_v1"
    ].value_numeric == 30
    assert metrics[
        "match:tracking:team:team:a:team_depth:tracking_shape_v1"
    ].value_numeric == 20
    assert metrics[
        "match:tracking:team:team:a:compactness_area:tracking_shape_v1"
    ].value_numeric == 600
    assert metrics[
        "match:tracking:team:team:a:defensive_line_height:tracking_shape_v1"
    ].value_numeric == 42.5
    assert metrics[
        "match:tracking:player:a1:true_average_position:tracking_shape_v1"
    ].value_json == {"x": 22.5, "y": 21}


def test_tracking_metrics_skip_when_true_positions_are_unavailable() -> None:
    context = TrackingContext(
        match_id="match:tracking",
        team_ids=("team:a",),
        capabilities=TrackingProviderCapabilities(true_player_positions=False),
        frames=[],
    )

    assert calculate_all_tracking_metrics(context) == []
