from __future__ import annotations

from tactical_analyst.analytics.base import MatchContext, metric_result
from tactical_analyst.analytics.helpers import (
    event_ids,
    is_carry,
    is_completed_action,
    is_pass,
    is_progressive,
)


class ProgressionMetrics:
    """Progressive pass and carry metrics using documented v1 distance thresholds."""

    name = "progression"
    version = "progression_v1"
    progressive_pass_version = "progressive_pass_v1"
    progressive_carry_version = "progressive_carry_v1"

    def calculate(self, context: MatchContext):
        results = []
        for team_id in context.team_ids:
            progressive_passes = [
                event
                for event in context.events
                if event.team_id == team_id
                and is_pass(event)
                and is_completed_action(event)
                and is_progressive(event)
            ]
            progressive_carries = [
                event
                for event in context.events
                if event.team_id == team_id and is_carry(event) and is_progressive(event)
            ]
            results.extend(
                [
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="progressive_passes",
                        metric_version=self.progressive_pass_version,
                        value_numeric=len(progressive_passes),
                        sample_size=len(progressive_passes),
                        source_event_ids=event_ids(progressive_passes),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="progressive_carries",
                        metric_version=self.progressive_carry_version,
                        value_numeric=len(progressive_carries),
                        sample_size=len(progressive_carries),
                        source_event_ids=event_ids(progressive_carries),
                    ),
                    metric_result(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name=self.name,
                        metric_version=self.version,
                        value_json={
                            "progressive_passes": len(progressive_passes),
                            "progressive_carries": len(progressive_carries),
                        },
                        sample_size=len(progressive_passes) + len(progressive_carries),
                        source_event_ids=event_ids(progressive_passes + progressive_carries),
                    ),
                ]
            )
        return results
