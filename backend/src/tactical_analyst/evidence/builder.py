from __future__ import annotations

import hashlib
import json
from typing import Any

from tactical_analyst.providers.soccer.capabilities import ProviderCapabilities
from tactical_analyst.schemas.evidence import EvidenceMetric, EvidencePacket
from tactical_analyst.schemas.metric import MetricResult
from tactical_analyst.visualization.base import VisualizationAsset


def build_evidence_packet(
    *,
    match: dict[str, Any],
    metrics: list[MetricResult],
    capabilities: ProviderCapabilities | dict[str, Any],
    visualization_assets: list[VisualizationAsset] | None = None,
) -> EvidencePacket:
    """Create compact evidence from deterministic metrics and asset metadata."""

    capability_dict = (
        capabilities.model_dump()
        if isinstance(capabilities, ProviderCapabilities)
        else capabilities
    )
    evidence_metrics = [_metric_to_evidence(metric) for metric in metrics]
    key_sequences = [
        metric.value_json
        for metric in metrics
        if metric.metric_name == "possession_sequences" and metric.entity_type == "possession"
    ]
    substitution_windows = [
        metric.value_json for metric in metrics if metric.metric_name == "substitution_impact"
    ]
    assets = [asset.__dict__ for asset in visualization_assets or []]
    packet_body = {
        "match": match,
        "metrics": [metric.model_dump() for metric in evidence_metrics],
        "key_sequences": key_sequences,
        "key_events": [],
        "substitution_windows": substitution_windows,
        "visualization_assets": assets,
        "capabilities": capability_dict,
    }
    evidence_hash = hashlib.sha256(
        json.dumps(packet_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return EvidencePacket(**packet_body, evidence_hash=evidence_hash)


def _metric_to_evidence(metric: MetricResult) -> EvidenceMetric:
    value: float | dict[str, Any] | None
    value = metric.value_numeric if metric.value_numeric is not None else metric.value_json
    return EvidenceMetric(
        evidence_id=_evidence_id(metric),
        metric=metric.metric_name,
        entity_type=metric.entity_type,
        entity_id=metric.entity_id,
        value=value,
        comparison=None,
        source_event_ids=metric.source_event_ids,
        definition_version=metric.metric_version,
    )


def _evidence_id(metric: MetricResult) -> str:
    entity = (metric.entity_id or metric.entity_type).upper().replace(":", "_")
    return f"METRIC_{metric.metric_name.upper()}_{entity}"
