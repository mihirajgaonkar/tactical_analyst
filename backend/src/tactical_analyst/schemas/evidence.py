from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    metric: str
    entity_type: str
    entity_id: str | None = None
    value: float | dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    source_event_ids: list[str] = Field(default_factory=list)
    definition_version: str


class EvidencePacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match: dict[str, Any]
    metrics: list[EvidenceMetric]
    key_sequences: list[dict[str, Any]] = Field(default_factory=list)
    key_events: list[dict[str, Any]] = Field(default_factory=list)
    substitution_windows: list[dict[str, Any]] = Field(default_factory=list)
    visualization_assets: list[dict[str, Any]] = Field(default_factory=list)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    evidence_hash: str
