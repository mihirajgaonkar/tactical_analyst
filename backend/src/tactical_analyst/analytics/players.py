from __future__ import annotations

from collections import Counter, defaultdict

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    DEFENSIVE_ACTION_TYPES,
    crosses_final_third,
    enters_box,
    event_ids,
    is_carry,
    is_pass,
    is_progressive,
)


class PlayerMetrics:
    """Transparent player influence feature metrics without an opaque composite score."""

    name = "player_influence_features"
    version = "player_influence_features_v1"

    def calculate(self, context: MatchContext):
        players = sorted({event.player_id for event in context.events if event.player_id})
        pass_edges = Counter(
            (event.player_id, event.receiver_player_id)
            for event in context.events
            if (
                is_pass(event)
                and event.player_id
                and event.receiver_player_id
                and event.outcome is None
            )
        )
        degree: dict[str, int] = defaultdict(int)
        for (passer, receiver), weight in pass_edges.items():
            degree[passer] += weight
            degree[receiver] += weight
        results = []
        for player_id in players:
            player_events = [event for event in context.events if event.player_id == player_id]
            received_passes = [
                event for event in context.events if event.receiver_player_id == player_id
            ]
            value = {
                "team_id": player_events[0].team_id if player_events else None,
                "pass_involvement": sum(1 for event in player_events if is_pass(event))
                + len(received_passes),
                "progressive_passes": sum(
                    1 for event in player_events if is_pass(event) and is_progressive(event)
                ),
                "progressive_carries": sum(
                    1 for event in player_events if is_carry(event) and is_progressive(event)
                ),
                "final_third_entries": sum(
                    1 for event in player_events if crosses_final_third(event)
                ),
                "box_entries": sum(1 for event in player_events if enters_box(event)),
                "shot_involvement": sum(1 for event in player_events if event.event_type == "Shot"),
                "xg": round(sum(event.xg or 0 for event in player_events), 4),
                "pressures": sum(1 for event in player_events if event.event_type == "Pressure"),
                "recoveries": sum(
                    1 for event in player_events if event.event_type == "Ball Recovery"
                ),
                "defensive_actions": sum(
                    1 for event in player_events if event.event_type in DEFENSIVE_ACTION_TYPES
                ),
                "passing_network_degree": degree.get(player_id, 0),
                "on_ball_centrality": round(
                    degree.get(player_id, 0) / max(sum(degree.values()), 1),
                    4,
                ),
            }
            results.append(
                metric_result(
                    context,
                    entity_type="player",
                    entity_id=player_id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json=value,
                    sample_size=len(player_events),
                    source_event_ids=event_ids(player_events),
                )
            )
        return results
