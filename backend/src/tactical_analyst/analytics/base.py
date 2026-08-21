from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from tactical_analyst.providers.soccer.capabilities import ProviderCapabilities
from tactical_analyst.schemas.event import MatchEvent
from tactical_analyst.schemas.lineup import LineupPlayer
from tactical_analyst.schemas.metric import MetricResult


@dataclass(frozen=True)
class MatchContext:
    """Canonical data bundle used by deterministic metric calculators."""

    match_id: str
    events: Sequence[MatchEvent]
    team_ids: tuple[str, ...]
    lineups: Sequence[LineupPlayer] = ()
    capabilities: ProviderCapabilities | None = None
    input_hash: str | None = None

    def resolved_input_hash(self) -> str:
        if self.input_hash:
            return self.input_hash
        event_ids = [event.id for event in self.events]
        encoded = json.dumps(
            {"match_id": self.match_id, "event_ids": event_ids},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class MetricCalculator(Protocol):
    """Common interface for all deterministic analytics calculators."""

    name: str
    version: str

    def calculate(self, context: MatchContext) -> list[MetricResult]:
        """Calculate metric results from canonical match context."""


def metric_result(
    context: MatchContext,
    *,
    entity_type: str,
    entity_id: str | None,
    metric_name: str,
    metric_version: str,
    value_numeric: float | None = None,
    value_json: dict | None = None,
    sample_size: int | None = None,
    source_event_ids: list[str] | None = None,
    window_start_ms: int | None = None,
    window_end_ms: int | None = None,
) -> MetricResult:
    metric_id = ":".join(
        part
        for part in [
            context.match_id,
            entity_type,
            entity_id,
            metric_name,
            metric_version,
            str(window_start_ms) if window_start_ms is not None else None,
            str(window_end_ms) if window_end_ms is not None else None,
        ]
        if part
    )
    return MetricResult(
        id=metric_id,
        match_id=context.match_id,
        entity_type=entity_type,  # type: ignore[arg-type]
        entity_id=entity_id,
        metric_name=metric_name,
        metric_version=metric_version,
        value_numeric=value_numeric,
        value_json=value_json,
        sample_size=sample_size,
        source_event_ids=source_event_ids or [],
        window_start_ms=window_start_ms,
        window_end_ms=window_end_ms,
        input_hash=context.resolved_input_hash(),
    )
