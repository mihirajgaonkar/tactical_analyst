from __future__ import annotations

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    GOAL_CENTER,
    SHOT_ON_TARGET_OUTCOMES,
    by_team,
    event_ids,
)


class ShotMetrics:
    """Shot and xG metrics v1."""

    name = "shots"
    version = "shots_xg_v1"
    BIG_CHANCE_XG = 0.30

    def calculate(self, context: MatchContext):
        results = []
        shots = [event for event in context.events if event.event_type == "Shot"]
        for team_id, team_events in by_team(shots).items():
            total_xg = sum(event.xg or 0 for event in team_events)
            goals = sum(1 for event in team_events if event.outcome == "Goal")
            on_target = sum(1 for event in team_events if event.outcome in SHOT_ON_TARGET_OUTCOMES)
            distances = [
                ((event.x - GOAL_CENTER[0]) ** 2 + (event.y - GOAL_CENTER[1]) ** 2) ** 0.5
                for event in team_events
                if event.x is not None and event.y is not None
            ]
            open_play_xg = sum(
                event.xg or 0 for event in team_events if event.play_pattern == "Regular Play"
            )
            set_piece_xg = total_xg - open_play_xg
            value = {
                "shots": len(team_events),
                "shots_on_target": on_target,
                "goals": goals,
                "xg": round(total_xg, 4),
                "xg_per_shot": round(total_xg / len(team_events), 4) if team_events else None,
                "open_play_xg": round(open_play_xg, 4),
                "set_piece_xg": round(set_piece_xg, 4),
                "average_shot_distance": round(sum(distances) / len(distances), 4)
                if distances
                else None,
                "big_chances": sum(
                    1 for event in team_events if (event.xg or 0) >= self.BIG_CHANCE_XG
                ),
            }
            results.append(
                metric_result(
                    context,
                    entity_type="team",
                    entity_id=team_id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json=value,
                    sample_size=len(team_events),
                    source_event_ids=event_ids(team_events),
                )
            )
            results.append(
                metric_result(
                    context,
                    entity_type="team",
                    entity_id=team_id,
                    metric_name="xg",
                    metric_version=self.version,
                    value_numeric=round(total_xg, 4),
                    sample_size=len(team_events),
                    source_event_ids=event_ids(team_events),
                )
            )
        return results
