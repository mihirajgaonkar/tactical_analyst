from __future__ import annotations

from collections import Counter, defaultdict

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import event_ids, is_completed_action, is_pass


class PassingMetrics:
    """Passing network metrics v1 using completed passes only."""

    name = "passing_network"
    version = "passing_network_v1"

    def __init__(self, minimum_edge_count: int = 1) -> None:
        self.minimum_edge_count = minimum_edge_count

    def calculate(self, context: MatchContext):
        results = []
        for team_id in context.team_ids:
            passes = [
                event
                for event in context.events
                if event.team_id == team_id
                and is_pass(event)
                and is_completed_action(event)
                and event.player_id
                and event.receiver_player_id
            ]
            edges = Counter((event.player_id, event.receiver_player_id) for event in passes)
            pass_volume = Counter(event.player_id for event in passes)
            weighted_degree: dict[str, int] = defaultdict(int)
            for (passer, receiver), weight in edges.items():
                weighted_degree[passer] += weight
                weighted_degree[receiver] += weight
            average_action_locations = {}
            for player_id in set(pass_volume):
                player_events = [event for event in passes if event.player_id == player_id]
                xs = [event.x for event in player_events if event.x is not None]
                ys = [event.y for event in player_events if event.y is not None]
                average_action_locations[player_id] = {
                    "x": round(sum(xs) / len(xs), 4) if xs else None,
                    "y": round(sum(ys) / len(ys), 4) if ys else None,
                }
            value = {
                "minimum_edge_count": self.minimum_edge_count,
                "edges": [
                    {"passer_id": passer, "receiver_id": receiver, "completed_passes": weight}
                    for (passer, receiver), weight in sorted(edges.items())
                    if weight >= self.minimum_edge_count
                ],
                "pass_volume": dict(sorted(pass_volume.items())),
                "weighted_degree": dict(sorted(weighted_degree.items())),
                "average_action_locations": average_action_locations,
            }
            results.append(
                metric_result(
                    context,
                    entity_type="team",
                    entity_id=team_id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json=value,
                    sample_size=len(passes),
                    source_event_ids=event_ids(passes),
                )
            )
        return results
