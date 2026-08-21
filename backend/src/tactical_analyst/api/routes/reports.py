from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from tactical_analyst.api.serializers import claim_to_dict, report_to_dict
from tactical_analyst.db.repositories.read import (
    get_report,
    get_report_claim,
    list_report_claims,
)
from tactical_analyst.db.session import get_db_session

router = APIRouter(prefix="/reports", tags=["reports"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{report_id}")
def get_report_detail(report_id: str, session: DbSession) -> dict:
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    response = report_to_dict(report)
    response["claims"] = [claim_to_dict(claim) for claim in list_report_claims(session, report_id)]
    return response


@router.get("/{report_id}/evidence")
def get_report_evidence(report_id: str, session: DbSession) -> dict:
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.report_json.get("evidence", {"evidence_hash": report.evidence_hash})


@router.get("/{report_id}/claims/{claim_id}/evidence")
def get_claim_evidence(
    report_id: str,
    claim_id: str,
    session: DbSession,
) -> dict:
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    claim = get_report_claim(session, report_id, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    evidence = report.report_json.get("evidence", {})
    metrics = evidence.get("metrics", [])
    matching = [item for item in metrics if item.get("evidence_id") in claim.evidence_ids]
    return {"claim": claim_to_dict(claim), "evidence": matching}
