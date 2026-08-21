from tactical_analyst.llm.schemas import TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket

TRACKING_ONLY_TERMS = {
    "compactness",
    "defensive line height",
    "line height",
    "team width",
    "team depth",
    "inter-line distance",
}


def verify_capability_coverage(
    interpretation: TacticalInterpretation,
    evidence_packet: EvidencePacket,
) -> list[str]:
    """Reject claims that require unavailable tracking or 360 capabilities."""

    text = interpretation.model_dump_json().lower()
    has_tracking = bool(evidence_packet.capabilities.get("tracking"))
    has_360 = bool(evidence_packet.capabilities.get("freeze_frames_360"))
    if has_tracking or has_360:
        return []
    return [
        f"Unavailable tracking/360 claim term: {term}"
        for term in TRACKING_ONLY_TERMS
        if term in text
    ]
