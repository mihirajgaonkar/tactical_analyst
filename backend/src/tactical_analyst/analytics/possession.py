from __future__ import annotations

from collections import defaultdict

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    crosses_final_third,
    enters_box,
    event_ids,
    is_carry,
    is_pass,
    is_progressive,
    lane_for_y,
)


class PossessionMetrics:
    """Possession sequence metrics based on provider possession IDs."""

    name = "possession_sequences"
    version = "possession_sequences_v1"

    def calculate(self, context: MatchContext):
        grouped = defaultdict(list)
        for event in context.events:
            if event.possession_id is not None:
                grouped[event.possession_id].append(event)
        sequences = []
        results = []
        for possession_id, events in sorted(grouped.items(), key=lambda item: int(item[0])):
            events = sorted(events, key=lambda event: event.timestamp_ms)
            first = events[0]
            last = events[-1]
            players = sorted({event.player_id for event in events if event.player_id})
            sequence = {
                "possession_id": possession_id,
                "team_id": first.team_id,
                "start_time_ms": first.timestamp_ms,
                "end_time_ms": last.timestamp_ms,
                "duration_ms": last.timestamp_ms - first.timestamp_ms,
                "starting_zone": lane_for_y(first.y),
                "ending_zone": lane_for_y(last.y),
                "passes": sum(1 for event in events if is_pass(event)),
                "carries": sum(1 for event in events if is_carry(event)),
                "progressive_actions": sum(1 for event in events if is_progressive(event)),
                "final_third_entry": any(crosses_final_third(event) for event in events),
                "box_entry": any(enters_box(event) for event in events),
                "shot": any(event.event_type == "Shot" for event in events),
                "goal": any(
                    event.event_type == "Shot" and event.outcome == "Goal" for event in events
                ),
                "players_involved": players,
                "source_event_ids": event_ids(events),
            }
            sequences.append(sequence)
            results.append(
                metric_result(
                    context,
                    entity_type="possession",
                    entity_id=possession_id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json=sequence,
                    sample_size=len(events),
                    source_event_ids=event_ids(events),
                    window_start_ms=first.timestamp_ms,
                    window_end_ms=last.timestamp_ms,
                )
            )
        results.append(
            metric_result(
                context,
                entity_type="match",
                entity_id=context.match_id,
                metric_name=self.name,
                metric_version=self.version,
                value_json={"sequences": sequences},
                sample_size=len(sequences),
                source_event_ids=event_ids(context.events),
            )
        )
        return results
