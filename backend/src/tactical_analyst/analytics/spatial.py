from __future__ import annotations

from collections import Counter

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    crosses_final_third,
    enters_box,
    event_ids,
    five_zone_for_y,
    is_progressive,
)


class SpatialMetrics:
    """Attacking zone counts from event locations."""

    name = "attacking_zones"
    version = "attacking_zones_v1"

    def calculate(self, context: MatchContext):
        results = []
        for team_id in context.team_ids:
            team_events = [
                event
                for event in context.events
                if event.team_id == team_id and event.x is not None and event.y is not None
            ]
            actions = Counter(five_zone_for_y(event.y) for event in team_events)
            progressive = Counter(
                five_zone_for_y(event.y) for event in team_events if is_progressive(event)
            )
            final_third = Counter(
                five_zone_for_y(event.end_y)
                for event in team_events
                if crosses_final_third(event)
            )
            box_entries = Counter(
                five_zone_for_y(event.end_y) for event in team_events if enters_box(event)
            )
            shots = Counter(
                five_zone_for_y(event.y) for event in team_events if event.event_type == "Shot"
            )
            results.append(
                metric_result(
                    context,
                    entity_type="team",
                    entity_id=team_id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json={
                        "actions_by_zone": dict(actions),
                        "progressive_actions_by_zone": dict(progressive),
                        "final_third_entries_by_zone": dict(final_third),
                        "box_entries_by_zone": dict(box_entries),
                        "shots_by_zone": dict(shots),
                    },
                    sample_size=len(team_events),
                    source_event_ids=event_ids(team_events),
                )
            )
        return results
