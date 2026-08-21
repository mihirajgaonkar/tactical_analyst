from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from tactical_analyst.db.session import build_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    try:
        engine = build_engine()
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except SQLAlchemyError:
        return {"status": "degraded", "database": "unavailable"}
    return {"status": "ready", "database": "ok"}
