from __future__ import annotations

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
            evidence_packet=evidence_packet.model_dump_json(indent=2)
        )
        model = self.chat_model.with_structured_output(TacticalInterpretation)
        return retry_call(lambda: model.invoke(prompt), self.retry_config)

    def final_report(
        self,
        evidence_packet: EvidencePacket,
        interpretation: TacticalInterpretation,
    ) -> FinalReport:
        prompt = _load_prompt("final_report.md").format(
            evidence_packet=evidence_packet.model_dump_json(indent=2),
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
