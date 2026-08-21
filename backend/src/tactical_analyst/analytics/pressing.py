from __future__ import annotations

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    BUILDUP_ZONE_X_MAX,
    DEFENSIVE_ACTION_TYPES,
    HIGH_TURNOVER_X,
    REGAIN_TYPES,
    event_ids,
    is_completed_action,
    is_pass,
    median_x,
)


class PressingMetrics:
    """PPDA, high turnovers, and defensive action height v1."""

    name = "pressing"
    version = "pressing_v1"
    ppda_version = "ppda_v1"
    high_turnover_version = "high_turnover_v1"
    defensive_action_height_version = "defensive_action_height_v1"

    def calculate(self, context: MatchContext):
        results = []
        for team_id in context.team_ids:
            opponent_ids = [candidate for candidate in context.team_ids if candidate != team_id]
            opponent_passes = [
                event
                for event in context.events
                if event.team_id in opponent_ids
                and is_pass(event)
                and is_completed_action(event)
                and event.x is not None
                and event.x <= BUILDUP_ZONE_X_MAX
            ]
            defensive_actions = [
                event
                for event in context.events
                if event.team_id == team_id
                and event.event_type in DEFENSIVE_ACTION_TYPES
                and event.x is not None
                and event.x <= BUILDUP_ZONE_X_MAX
            ]
            all_defensive_actions = [
                event
                for event in context.events
                if event.team_id == team_id and event.event_type in DEFENSIVE_ACTION_TYPES
            ]
            ppda = len(opponent_passes) / len(defensive_actions) if defensive_actions else None
            high_turnovers = [
                event
                for event in context.events
                if event.team_id == team_id
                and event.event_type in REGAIN_TYPES
                and event.x is not None
                and event.x >= HIGH_TURNOVER_X
            ]
            high_turnover_details = [
                _high_turnover_detail(event, context.events) for event in high_turnovers
            ]
            results.extend(
                [
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="ppda",
                        metric_version=self.ppda_version,
                        value_numeric=round(ppda, 4) if ppda is not None else None,
                        value_json={
                            "opponent_completed_passes_in_build_up_zone": len(opponent_passes),
                            "defensive_actions_in_build_up_zone": len(defensive_actions),
                            "build_up_zone_x_max": BUILDUP_ZONE_X_MAX,
                        },
                        sample_size=len(opponent_passes) + len(defensive_actions),
                        source_event_ids=event_ids(opponent_passes + defensive_actions),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="high_turnovers",
                        metric_version=self.high_turnover_version,
                        value_numeric=len(high_turnovers),
                        value_json={
                            "turnovers": high_turnover_details,
                            "leading_to_shot": sum(
                                1 for item in high_turnover_details if item["led_to_shot"]
                            ),
                            "leading_to_goal": sum(
                                1 for item in high_turnover_details if item["led_to_goal"]
                            ),
                            "high_zone_x_min": HIGH_TURNOVER_X,
                        },
                        sample_size=len(high_turnovers),
                        source_event_ids=event_ids(high_turnovers),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="defensive_action_height",
                        metric_version=self.defensive_action_height_version,
                        value_numeric=median_x(all_defensive_actions),
                        sample_size=len(all_defensive_actions),
                        source_event_ids=event_ids(all_defensive_actions),
                    ),
                ]
            )
        return results


def _high_turnover_detail(regain_event, events) -> dict:
    possession_events = [
        event
        for event in events
        if (
            event.possession_id == regain_event.possession_id
            and event.timestamp_ms >= regain_event.timestamp_ms
        )
    ]
    return {
        "event_id": regain_event.id,
        "x": regain_event.x,
        "y": regain_event.y,
        "possession_id": regain_event.possession_id,
        "led_to_shot": any(event.event_type == "Shot" for event in possession_events),
        "led_to_goal": any(
            event.event_type == "Shot" and event.outcome == "Goal" for event in possession_events
        ),
    }
