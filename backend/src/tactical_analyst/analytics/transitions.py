from __future__ import annotations

from collections import Counter, defaultdict

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import event_ids, is_pass


class TransitionMetrics:
    """Deterministic build-up pattern labels for possession sequences."""

    name = "build_up_patterns"
    version = "build_up_patterns_v1"

    def calculate(self, context: MatchContext):
        grouped = defaultdict(list)
        for event in context.events:
            if event.possession_id is not None:
                grouped[event.possession_id].append(event)
        labels_by_team: dict[str, Counter] = {team_id: Counter() for team_id in context.team_ids}
        details = []
        for possession_id, events in grouped.items():
            events = sorted(events, key=lambda event: event.timestamp_ms)
            label = _label_sequence(events)
            team_id = events[0].team_id
            labels_by_team.setdefault(team_id, Counter())[label] += 1
            details.append({"possession_id": possession_id, "team_id": team_id, "label": label})
        return [
            metric_result(
                context,
                entity_type="team",
                entity_id=team_id,
                metric_name=self.name,
                metric_version=self.version,
                value_json={
                    "distribution": dict(counter),
                    "details": [item for item in details if item["team_id"] == team_id],
                },
                sample_size=sum(counter.values()),
                source_event_ids=event_ids(
                    event for event in context.events if event.team_id == team_id
                ),
            )
            for team_id, counter in labels_by_team.items()
        ]


def _label_sequence(events) -> str:
    first = events[0]
    last = events[-1]
    duration_ms = last.timestamp_ms - first.timestamp_ms
    passes = sum(1 for event in events if is_pass(event))
    vertical_gain = (last.x or 0) - (first.x or 0)
    lateral_delta = abs((last.y or 0) - (first.y or 0))
    if first.play_pattern == "From Counter":
        return "COUNTERATTACK"
    if any(event.event_type == "Shot" for event in events):
        return "DIRECT_BUILDUP" if duration_ms <= 10000 and passes <= 3 else "SHORT_BUILDUP"
    if vertical_gain < 5 and duration_ms > 15000:
        return "FAILED_BUILDUP"
    if lateral_delta >= 34:
        return "SWITCH_OF_PLAY"
    if first.y is not None and first.y < 68 / 3:
        return "LEFT_BUILDUP"
    if first.y is not None and first.y > 68 * 2 / 3:
        return "RIGHT_BUILDUP"
    if passes <= 3 and vertical_gain >= 25:
        return "DIRECT_BUILDUP"
    return "CENTRAL_BUILDUP"
