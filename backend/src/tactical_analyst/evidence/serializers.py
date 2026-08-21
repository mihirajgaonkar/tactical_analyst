from tactical_analyst.schemas.evidence import EvidencePacket


def evidence_to_json(packet: EvidencePacket) -> str:
    """Serialize evidence deterministically for storage or LLM input."""

    return packet.model_dump_json(indent=2)
