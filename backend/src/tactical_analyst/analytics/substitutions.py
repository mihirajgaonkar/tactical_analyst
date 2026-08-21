from __future__ import annotations

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    crosses_final_third,
    enters_box,
    event_ids,
    is_pass,
)


class SubstitutionMetrics:
    """Pre/post substitution impact windows with correlation-only metric outputs."""

    name = "substitution_impact"
    version = "substitution_impact_v1"

    def __init__(self, window_ms: int = 10 * 60 * 1000) -> None:
        self.window_ms = window_ms

    def calculate(self, context: MatchContext):
        substitutions = [
            event
            for event in context.events
            if event.event_type == "Substitution" and event.player_id is not None
        ]
        results = []
        for substitution in substitutions:
            before_start = max(0, substitution.timestamp_ms - self.window_ms)
            before_events = [
                event
                for event in context.events
                if event.team_id == substitution.team_id
                and before_start <= event.timestamp_ms < substitution.timestamp_ms
            ]
            after_end = substitution.timestamp_ms + self.window_ms
            after_events = [
                event
                for event in context.events
                if event.team_id == substitution.team_id
                and substitution.timestamp_ms < event.timestamp_ms <= after_end
            ]
            value = {
                "substitution_event_id": substitution.id,
                "team_id": substitution.team_id,
                "player_off_id": substitution.player_id,
                "player_on_id": substitution.provider_payload.get("substitution", {})
                .get("replacement", {})
                .get("id"),
                "window_ms": self.window_ms,
                "before": _window_summary(before_events),
                "after": _window_summary(after_events),
            }
            results.append(
                metric_result(
                    context,
                    entity_type="substitution",
                    entity_id=substitution.id,
                    metric_name=self.name,
                    metric_version=self.version,
                    value_json=value,
                    sample_size=len(before_events) + len(after_events),
                    source_event_ids=event_ids([substitution] + before_events + after_events),
                    window_start_ms=before_start,
                    window_end_ms=after_end,
                )
            )
        return results


def _window_summary(events) -> dict:
    shots = [event for event in events if event.event_type == "Shot"]
    completed_attacking_third_passes = [
        event
        for event in events
        if is_pass(event) and event.outcome is None and event.end_x and event.end_x >= 70
    ]
    return {
        "xg": round(sum(event.xg or 0 for event in shots), 4),
        "shots": len(shots),
        "field_tilt_sample": len(completed_attacking_third_passes),
        "final_third_entries": sum(1 for event in events if crosses_final_third(event)),
        "box_entries": sum(1 for event in events if enters_box(event)),
    }
