from __future__ import annotations

from collections import Counter

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    FINAL_THIRD_X,
    crosses_final_third,
    enters_box,
    event_ids,
    is_carry,
    is_completed_action,
    is_pass,
    lane_for_y,
)


class TerritoryMetrics:
    """Field tilt, final-third entries, and box entries v1."""

    name = "territory"
    version = "territory_entries_v1"
    field_tilt_version = "field_tilt_passes_v1"
    final_third_entries_version = "final_third_entries_v1"
    box_entries_version = "box_entries_v1"

    def calculate(self, context: MatchContext):
        results = []
        completed_attacking_third_passes = {
            team_id: [
                event
                for event in context.events
                if event.team_id == team_id
                and is_pass(event)
                and is_completed_action(event)
                and event.end_x is not None
                and event.end_x >= FINAL_THIRD_X
            ]
            for team_id in context.team_ids
        }
        denominator = sum(len(events) for events in completed_attacking_third_passes.values())
        for team_id in context.team_ids:
            final_third_entries = [
                event
                for event in context.events
                if event.team_id == team_id
                and (is_pass(event) or is_carry(event))
                and (not is_pass(event) or is_completed_action(event))
                and crosses_final_third(event)
            ]
            box_entries = [
                event
                for event in context.events
                if event.team_id == team_id
                and (is_pass(event) or is_carry(event))
                and (not is_pass(event) or is_completed_action(event))
                and enters_box(event)
            ]
            final_third_by_lane = Counter(lane_for_y(event.end_y) for event in final_third_entries)
            box_by_lane = Counter(lane_for_y(event.end_y) for event in box_entries)
            pass_entries = [event for event in final_third_entries if is_pass(event)]
            carry_entries = [event for event in final_third_entries if is_carry(event)]
            box_pass_entries = [event for event in box_entries if is_pass(event)]
            box_carry_entries = [event for event in box_entries if is_carry(event)]
            team_attacking_third = completed_attacking_third_passes[team_id]
            results.extend(
                [
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="field_tilt",
                        metric_version=self.field_tilt_version,
                        value_numeric=round(len(team_attacking_third) / denominator, 4)
                        if denominator
                        else None,
                        value_json={
                            "numerator": len(team_attacking_third),
                            "denominator": denominator,
                        },
                        sample_size=denominator,
                        source_event_ids=event_ids(team_attacking_third),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="final_third_entries",
                        metric_version=self.final_third_entries_version,
                        value_numeric=len(final_third_entries),
                        value_json={
                            "passes": len(pass_entries),
                            "carries": len(carry_entries),
                            "by_lane": dict(final_third_by_lane),
                        },
                        sample_size=len(final_third_entries),
                        source_event_ids=event_ids(final_third_entries),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="box_entries",
                        metric_version=self.box_entries_version,
                        value_numeric=len(box_entries),
                        value_json={
                            "passes": len(box_pass_entries),
                            "carries": len(box_carry_entries),
                            "by_lane": dict(box_by_lane),
                        },
                        sample_size=len(box_entries),
                        source_event_ids=event_ids(box_entries),
                    ),
                ]
            )
        return results
