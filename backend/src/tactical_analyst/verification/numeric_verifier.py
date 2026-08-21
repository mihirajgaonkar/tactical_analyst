from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket

NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])-?\d+(?:\.\d+)?%?")


def verify_interpretation_numbers(
    interpretation: TacticalInterpretation,
    evidence_packet: EvidencePacket,
) -> list[str]:
    text = interpretation.model_dump_json()
    return _verify_numbers(text, evidence_packet)


def verify_report_numbers(report: FinalReport, evidence_packet: EvidencePacket) -> list[str]:
    return _verify_numbers(report.model_dump_json(), evidence_packet)


def _verify_numbers(text: str, evidence_packet: EvidencePacket) -> list[str]:
    allowed = _evidence_numbers(evidence_packet)
    errors = []
    for raw in NUMBER_PATTERN.findall(text):
        number = raw.rstrip("%")
        try:
            decimal = Decimal(number)
        except InvalidOperation:
            continue
        if decimal not in allowed:
            errors.append(f"Unsupported numeric value: {raw}")
    return errors


def _evidence_numbers(packet: EvidencePacket) -> set[Decimal]:
    values: set[Decimal] = set()
    for metric in packet.metrics:
        _collect_numbers(metric.model_dump(), values)
    _collect_numbers(packet.match, values)
    return values


def _collect_numbers(value, values: set[Decimal]) -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, int | float | Decimal):
        values.add(Decimal(str(value)))
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_numbers(item, values)
    elif isinstance(value, list):
        for item in value:
            _collect_numbers(item, values)
