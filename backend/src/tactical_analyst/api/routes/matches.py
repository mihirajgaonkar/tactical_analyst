from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from tactical_analyst.api.dependencies import get_job_client
from tactical_analyst.api.serializers import match_to_dict
from tactical_analyst.db.repositories.read import get_match, get_team, list_matches
from tactical_analyst.db.session import get_db_session
from tactical_analyst.workers.jobs import JobClient

router = APIRouter(prefix="/matches", tags=["matches"])
DbSession = Annotated[Session, Depends(get_db_session)]
JobDependency = Annotated[JobClient, Depends(get_job_client)]


@router.get("")
def get_matches(
    session: DbSession,
    competition_id: str | None = Query(default=None),
    season_id: str | None = Query(default=None),
) -> list[dict]:
    matches = list_matches(session, competition_id, season_id)
    return [_match_response(session, match) for match in matches]


@router.get("/{match_id}")
def get_match_detail(match_id: str, session: DbSession) -> dict:
    match = get_match(session, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return _match_response(session, match)


@router.post("/{match_id}/ingest")
def ingest_match(match_id: str, job_client: JobDependency) -> dict:
    job = job_client.enqueue(
        "tactical_analyst.ingest_match",
        match_id,
        idempotency_key=f"ingest:{match_id}",
    )
    return {"job_id": job.job_id, "status": job.status}


@router.post("/{match_id}/analyze")
def analyze_match(match_id: str, job_client: JobDependency) -> dict:
    job = job_client.enqueue(
        "tactical_analyst.run_tactical_analysis",
        match_id,
        idempotency_key=f"analysis:{match_id}",
    )
    return {"job_id": job.job_id, "status": job.status}


def _match_response(session: Session, match) -> dict:
    return match_to_dict(
        match,
        get_team(session, match.home_team_id),
        get_team(session, match.away_team_id),
    )
