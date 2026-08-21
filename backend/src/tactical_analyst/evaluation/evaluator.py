from __future__ import annotations

from pydantic import BaseModel, Field

from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket
from tactical_analyst.verification.claim_verifier import verify_claim_evidence
from tactical_analyst.verification.coverage_verifier import verify_capability_coverage
from tactical_analyst.verification.numeric_verifier import (
    verify_interpretation_numbers,
    verify_report_numbers,
)


class EvaluationResult(BaseModel):
    unsupported_numeric_claims: int = 0
    unknown_evidence_references: int = 0
    unavailable_metric_claims: int = 0
    errors: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.unsupported_numeric_claims == 0
            and self.unknown_evidence_references == 0
            and self.unavailable_metric_claims == 0
        )


def evaluate_interpretation(
    interpretation: TacticalInterpretation,
    evidence_packet: EvidencePacket,
) -> EvaluationResult:
    evidence_errors = verify_claim_evidence(interpretation, evidence_packet)
    numeric_errors = verify_interpretation_numbers(interpretation, evidence_packet)
    capability_errors = verify_capability_coverage(interpretation, evidence_packet)
    return EvaluationResult(
        unsupported_numeric_claims=len(numeric_errors),
        unknown_evidence_references=len(evidence_errors),
        unavailable_metric_claims=len(capability_errors),
        errors=[*evidence_errors, *numeric_errors, *capability_errors],
    )


def evaluate_final_report(report: FinalReport, evidence_packet: EvidencePacket) -> EvaluationResult:
    numeric_errors = verify_report_numbers(report, evidence_packet)
    return EvaluationResult(
        unsupported_numeric_claims=len(numeric_errors),
        errors=numeric_errors,
    )
