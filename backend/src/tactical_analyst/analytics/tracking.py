from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from tactical_analyst.schemas.metric import MetricResult
from tactical_analyst.schemas.tracking import TrackingFrame, TrackingProviderCapabilities

DEFENSIVE_LINE_WINDOW_M = 52.5


@dataclass(frozen=True)
class TrackingContext:
    """Canonical bundle for true tracking analytics."""

    match_id: str
    frames: Sequence[TrackingFrame]
    team_ids: tuple[str, ...]
    capabilities: TrackingProviderCapabilities
    input_hash: str | None = None

    def resolved_input_hash(self) -> str:
        if self.input_hash:
            return self.input_hash
        encoded = json.dumps(
            {
                "match_id": self.match_id,
                "frames": [
                    {"frame_id": frame.frame_id, "timestamp_ms": frame.timestamp_ms}
                    for frame in self.frames
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class TrackingShapeMetrics:
    """Deterministic true-position metrics from tracking frames."""

    name = "tracking_shape"
    version = "tracking_shape_v1"

    def calculate(self, context: TrackingContext) -> list[MetricResult]:
        if not context.capabilities.true_player_positions:
            return []
        return [
            *self._team_shape_metrics(context),
            *self._player_average_positions(context),
        ]

    def _team_shape_metrics(self, context: TrackingContext) -> list[MetricResult]:
        results: list[MetricResult] = []
        for team_id in context.team_ids:
            widths: list[float] = []
            depths: list[float] = []
            compactness_values: list[float] = []
            defensive_line_x_values: list[float] = []
            source_frame_ids: list[str] = []
            for frame in context.frames:
                players = [player for player in frame.players if player.team_id == team_id]
                if len(players) < 2:
                    continue
                xs = [player.x for player in players]
                ys = [player.y for player in players]
                widths.append(max(ys) - min(ys))
                depths.append(max(xs) - min(xs))
                compactness_values.append((max(xs) - min(xs)) * (max(ys) - min(ys)))
                defensive_players = [
                    player.x for player in players if player.x <= DEFENSIVE_LINE_WINDOW_M
                ]
                if defensive_players:
                    defensive_line_x_values.append(max(defensive_players))
                source_frame_ids.append(frame.frame_id)

            if not source_frame_ids:
                continue
            results.extend(
                [
                    _tracking_metric(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="team_width",
                        value_numeric=_mean(widths),
                        sample_size=len(widths),
                        source_frame_ids=source_frame_ids,
                    ),
                    _tracking_metric(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="team_depth",
                        value_numeric=_mean(depths),
                        sample_size=len(depths),
                        source_frame_ids=source_frame_ids,
                    ),
                    _tracking_metric(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="compactness_area",
                        value_numeric=_mean(compactness_values),
                        sample_size=len(compactness_values),
                        source_frame_ids=source_frame_ids,
                    ),
                    _tracking_metric(
                        context,
                        entity_type="team",
                        entity_id=team_id,
                        metric_name="defensive_line_height",
                        value_numeric=_mean(defensive_line_x_values),
                        sample_size=len(defensive_line_x_values),
                        source_frame_ids=source_frame_ids,
                    ),
                ]
            )
        return results

    def _player_average_positions(self, context: TrackingContext) -> list[MetricResult]:
        by_player: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
        for frame in context.frames:
            for player in frame.players:
                by_player[player.player_id].append((player.x, player.y, frame.frame_id))

        results: list[MetricResult] = []
        for player_id, points in by_player.items():
            results.append(
                _tracking_metric(
                    context,
                    entity_type="player",
                    entity_id=player_id,
                    metric_name="true_average_position",
                    value_json={
                        "x": _mean([point[0] for point in points]),
                        "y": _mean([point[1] for point in points]),
                    },
                    sample_size=len(points),
                    source_frame_ids=[point[2] for point in points],
                )
            )
        return results


TRACKING_METRIC_REGISTRY = {"tracking_shape": TrackingShapeMetrics()}


def calculate_all_tracking_metrics(
    context: TrackingContext,
    registry: dict[str, TrackingShapeMetrics] | None = None,
) -> list[MetricResult]:
    """Calculate all registered true tracking metrics."""

    calculators = registry or TRACKING_METRIC_REGISTRY
    results: list[MetricResult] = []
    for calculator in calculators.values():
        results.extend(calculator.calculate(context))
    return results


def _tracking_metric(
    context: TrackingContext,
    *,
    entity_type: str,
    entity_id: str,
    metric_name: str,
    value_numeric: float | None = None,
    value_json: dict | None = None,
    sample_size: int,
    source_frame_ids: list[str],
) -> MetricResult:
    metric_id = ":".join(
        [
            context.match_id,
            entity_type,
            entity_id,
            metric_name,
            TrackingShapeMetrics.version,
        ]
    )
    return MetricResult(
        id=metric_id,
        match_id=context.match_id,
        entity_type=entity_type,
        entity_id=entity_id,
        metric_name=metric_name,
        metric_version=TrackingShapeMetrics.version,
        value_numeric=value_numeric,
        value_json=value_json,
        sample_size=sample_size,
        source_event_ids=source_frame_ids,
        input_hash=context.resolved_input_hash(),
    )


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)
