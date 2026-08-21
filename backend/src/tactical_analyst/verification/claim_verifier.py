from tactical_analyst.llm.schemas import TacticalClaim, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket


def verify_claim_evidence(
    interpretation: TacticalInterpretation,
    evidence_packet: EvidencePacket,
) -> list[str]:
    """Ensure all claim evidence IDs exist and strong claims have enough support."""

    known_ids = {metric.evidence_id for metric in evidence_packet.metrics}
    errors: list[str] = []
    for claim in _all_claims(interpretation):
        missing = [
            evidence_id for evidence_id in claim.evidence_ids if evidence_id not in known_ids
        ]
        if missing:
            errors.append(f"{claim.claim_id}: unknown evidence IDs {missing}")
        if not claim.evidence_ids:
            errors.append(f"{claim.claim_id}: missing evidence IDs")
        if claim.strength == "strong" and len(set(claim.evidence_ids)) < 2:
            errors.append(f"{claim.claim_id}: strong claims require at least two evidence IDs")
    return errors


def _all_claims(interpretation: TacticalInterpretation) -> list[TacticalClaim]:
    return [
        *interpretation.claims,
        *interpretation.turning_points,
        *interpretation.player_findings,
    ]
