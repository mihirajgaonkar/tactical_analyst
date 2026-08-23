from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from tactical_analyst.db.models import Base, LineupModel, MatchEventModel, MatchModel
from tactical_analyst.ingestion.service import MatchIngestionService
from tests.fixtures.statsbomb_sample import SAMPLE_EVENTS, SAMPLE_LINEUPS, SAMPLE_MATCH


class FakeProvider:
    async def list_competitions(self):
        return []

    async def list_matches(self, competition_id: str, season_id: str):
        return []

    async def get_match(self, match_id: str):
        return SAMPLE_MATCH

    async def get_lineups(self, match_id: str):
        return SAMPLE_LINEUPS

    async def get_events(self, match_id: str):
        return SAMPLE_EVENTS

    async def get_frames(self, match_id: str):
        return []

    def capabilities(self):
        return None


class FakeStorage:
    def put_json_gz(self, key: str, payload: object) -> tuple[str, str]:
        return f"memory://{key}", "fake-sha256"


async def test_ingestion_service_is_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = MatchIngestionService(
            provider=FakeProvider(),
            storage=FakeStorage(),
            session=session,
        )

        first = await service.ingest_match("1")
        second = await service.ingest_match("1")

        assert first.match_id == second.match_id == "statsbomb:1"
        assert session.scalar(select(MatchModel).where(MatchModel.id == "statsbomb:1")) is not None
        assert len(session.scalars(select(LineupModel)).all()) == 2
        assert len(session.scalars(select(MatchEventModel)).all()) == 2
