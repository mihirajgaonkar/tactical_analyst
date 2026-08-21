from __future__ import annotations

from tactical_analyst.evidence.builder import build_evidence_packet
from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket
from tactical_analyst.schemas.metric import MetricResult
from tactical_analyst.verification.claim_verifier import verify_claim_evidence
from tactical_analyst.verification.coverage_verifier import verify_capability_coverage
from tactical_analyst.verification.numeric_verifier import (
    verify_interpretation_numbers,
    verify_report_numbers,
)


def validate_match_node(state: dict) -> dict:
    if not state.get("match_id"):
        return _append_error(state, "match_id is required")
    state["match_loaded"] = True
    return state


def build_evidence_packet_node(state: dict) -> dict:
    metrics = [MetricResult.model_validate(item) for item in state.get("metric_results", [])]
    packet = build_evidence_packet(
        match=state.get("match", {"match_id": state["match_id"]}),
        metrics=metrics,
        capabilities=state.get("provider_capabilities", {}),
        visualization_assets=[],
    )
    state["evidence_packet"] = packet.model_dump()
    return state


def tactical_interpretation_node(state: dict, llm_service) -> dict:
    packet = EvidencePacket.model_validate(state["evidence_packet"])
    interpretation = llm_service.interpret(packet)
    state["interpretation"] = interpretation.model_dump()
    return state


def verify_claims_node(state: dict) -> dict:
    packet = EvidencePacket.model_validate(state["evidence_packet"])
    interpretation = TacticalInterpretation.model_validate(state["interpretation"])
    errors = [
        *verify_claim_evidence(interpretation, packet),
        *verify_interpretation_numbers(interpretation, packet),
        *verify_capability_coverage(interpretation, packet),
    ]
    state["verification_errors"] = errors
    state["verification_attempts"] = int(state.get("verification_attempts", 0))
    return state


def repair_claims_node(state: dict, llm_service, max_attempts: int = 1) -> dict:
    state["verification_attempts"] = int(state.get("verification_attempts", 0)) + 1
    if state["verification_attempts"] > max_attempts:
        return state
    packet = EvidencePacket.model_validate(state["evidence_packet"])
    interpretation = llm_service.interpret(packet)
    state["interpretation"] = interpretation.model_dump()
    return state


def final_report_node(state: dict, llm_service) -> dict:
    packet = EvidencePacket.model_validate(state["evidence_packet"])
    interpretation = TacticalInterpretation.model_validate(state["interpretation"])
    report = llm_service.final_report(packet, interpretation)
    state["report"] = report.model_dump()
    state["report_markdown"] = report.markdown
    return state


def final_numeric_verification_node(state: dict) -> dict:
    packet = EvidencePacket.model_validate(state["evidence_packet"])
    report = FinalReport.model_validate(state["report"])
    errors = verify_report_numbers(report, packet)
    state["verification_errors"] = [*state.get("verification_errors", []), *errors]
    return state


def persist_report_node(state: dict) -> dict:
    state["report_persisted"] = True
    return state


def _append_error(state: dict, error: str) -> dict:
    state["errors"] = [*state.get("errors", []), error]
    return state
