from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.orm import Session

from tactical_analyst.db.models import ReportClaimModel, TacticalReportModel
from tactical_analyst.llm.schemas import FinalReport, TacticalInterpretation
from tactical_analyst.schemas.evidence import EvidencePacket


def persist_tactical_report(
    session: Session,
    *,
    match_id: str,
    evidence_packet: EvidencePacket,
    interpretation: TacticalInterpretation,
    final_report: FinalReport,
    llm_provider: str,
    llm_model: str,
    prompt_version: str,
    verification_status: str = "passed",
) -> TacticalReportModel:
    """Persist a verified report and its evidence-linked claims idempotently."""

    report_id = _stable_id(
        "report",
        match_id,
        evidence_packet.evidence_hash,
        prompt_version,
        llm_provider,
        llm_model,
    )
    report_json = {
        **final_report.model_dump(),
        "interpretation": interpretation.model_dump(),
        "evidence": evidence_packet.model_dump(),
    }
    values = {
        "match_id": match_id,
        "report_version": "v1",
        "evidence_hash": evidence_packet.evidence_hash,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "prompt_version": prompt_version,
        "report_json": report_json,
        "report_markdown": final_report.markdown,
        "verification_status": verification_status,
    }

    db_report = session.get(TacticalReportModel, report_id)
    if db_report is None:
        db_report = TacticalReportModel(id=report_id, **values)
        session.add(db_report)
    else:
        for key, value in values.items():
            setattr(db_report, key, value)

    session.query(ReportClaimModel).filter(ReportClaimModel.report_id == report_id).delete()
    for claim_type, claims in [
        ("claim", interpretation.claims),
        ("turning_point", interpretation.turning_points),
        ("player_finding", interpretation.player_findings),
    ]:
        for claim in claims:
            session.add(
                ReportClaimModel(
                    id=_stable_id("claim", report_id, claim.claim_id),
                    report_id=report_id,
                    claim_text=claim.claim,
                    claim_type=claim_type,
                    strength=claim.strength,
                    verification_status=verification_status,
                    evidence_ids=claim.evidence_ids,
                    caveats=claim.caveats,
                )
            )

    session.commit()
    return db_report


def _stable_id(prefix: str, *parts: str) -> str:
    return f"{prefix}:{uuid5(NAMESPACE_URL, ':'.join(parts))}"
