from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from tactical_analyst.api.serializers import competition_to_dict, season_to_dict
from tactical_analyst.db.repositories.read import list_competitions, list_seasons
from tactical_analyst.db.session import get_db_session

router = APIRouter(prefix="/competitions", tags=["competitions"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("")
def get_competitions(session: DbSession) -> list[dict]:
    return [competition_to_dict(item) for item in list_competitions(session)]


@router.get("/{competition_id}/seasons")
def get_competition_seasons(
    competition_id: str,
    session: DbSession,
) -> list[dict]:
    return [season_to_dict(item) for item in list_seasons(session, competition_id)]
