from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from tactical_analyst.api.serializers import metric_to_dict
from tactical_analyst.db.repositories.read import get_match, list_metrics
from tactical_analyst.db.session import get_db_session

router = APIRouter(prefix="/matches/{match_id}/metrics", tags=["metrics"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("")
def get_match_metrics(match_id: str, session: DbSession) -> list[dict]:
    if get_match(session, match_id) is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return [metric_to_dict(metric) for metric in list_metrics(session, match_id)]
