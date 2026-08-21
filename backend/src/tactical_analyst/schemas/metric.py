from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricResult(BaseModel):
    """Versioned deterministic metric output ready for persistence/evidence building."""

    model_config = ConfigDict(extra="forbid")

    id: str
    match_id: str
    entity_type: Literal["match", "team", "player", "possession", "substitution"]
    entity_id: str | None = None
    metric_name: str
    metric_version: str
    value_numeric: float | None = None
    value_json: dict[str, Any] | None = None
    sample_size: int | None = None
    source_event_ids: list[str] = Field(default_factory=list)
    window_start_ms: int | None = None
    window_end_ms: int | None = None
    input_hash: str
