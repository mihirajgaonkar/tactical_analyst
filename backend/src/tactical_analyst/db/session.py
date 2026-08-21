from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tactical_analyst.config.settings import Settings, get_settings


def build_engine(settings: Settings | None = None):
    """Create a SQLAlchemy engine from application settings."""

    settings = settings or get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def build_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    """Create the application session factory."""

    return sessionmaker(bind=build_engine(settings), expire_on_commit=False)


SessionLocal = build_session_factory()


def get_db_session() -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""

    with SessionLocal() as session:
        yield session
