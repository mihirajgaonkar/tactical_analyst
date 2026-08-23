from __future__ import annotations

import json
from typing import Any

from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.reliability.retry import RetryConfig, retry_call
from tactical_analyst.schemas.evidence import EvidencePacket


class LLMService:
    """Structured-output LLM service wrapper."""

    def __init__(self, chat_model, retry_config: RetryConfig | None = None) -> None:
        self.chat_model = chat_model
        self.retry_config = retry_config or RetryConfig(max_attempts=1, backoff_seconds=0)

    def interpret(self, evidence_packet: EvidencePacket) -> TacticalInterpretation:
        prompt = _load_prompt("tactical_interpreter.md").format(
            evidence_packet=_compact_evidence_json(evidence_packet)
        )
        model = self.chat_model.with_structured_output(TacticalInterpretation)
        return retry_call(lambda: model.invoke(prompt), self.retry_config)

    def final_report(
        self,
        evidence_packet: EvidencePacket,
        interpretation: TacticalInterpretation,
    ) -> FinalReport:
        prompt = _load_prompt("final_report.md").format(
            evidence_packet=_compact_evidence_json(evidence_packet),
            interpretation=interpretation.model_dump_json(indent=2),
        )
        model = self.chat_model.with_structured_output(FinalReport)
        return retry_call(lambda: model.invoke(prompt), self.retry_config)


def _load_prompt(filename: str) -> str:
    from importlib.resources import files

    return (
        files("tactical_analyst.llm.prompts")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )


def _compact_evidence_json(evidence_packet: EvidencePacket) -> str:
    """Serialize evidence without repeating raw event IDs in the model prompt.

    The full IDs remain in the persisted evidence packet for auditability. The model cites
    stable evidence IDs, so sending every underlying event UUID only wastes context and quota.
    """

    model_evidence = evidence_packet.model_dump(mode="json")
    model_evidence["metrics"] = [
        metric
        for metric in model_evidence["metrics"]
        if _include_metric_in_prompt(metric)
    ]
    # These collections duplicate the possession and substitution metrics retained above.
    model_evidence["key_sequences"] = []
    model_evidence["substitution_windows"] = []
    compact = _replace_source_event_ids(model_evidence)
    return json.dumps(compact, indent=2)


def _include_metric_in_prompt(metric: dict[str, Any]) -> bool:
    if metric.get("metric") != "possession_sequences":
        return True
    if metric.get("entity_type") != "possession":
        return False
    value = metric.get("value")
    return isinstance(value, dict) and bool(value.get("shot") or value.get("goal"))


def _replace_source_event_ids(value: Any) -> Any:
    if isinstance(value, dict):
        compact: dict[str, Any] = {}
        for key, item in value.items():
            if key == "source_event_ids" and isinstance(item, list):
                compact["source_event_count"] = len(item)
            else:
                compact[key] = _replace_source_event_ids(item)
        return compact
    if isinstance(value, list):
        return [_replace_source_event_ids(item) for item in value]
    return value
