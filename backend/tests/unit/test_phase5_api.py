from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from tactical_analyst.api.app import create_app
from tactical_analyst.api.dependencies import get_job_client
from tactical_analyst.db.models import (
    Base,
    CalculatedMetricModel,
    CompetitionModel,
    MatchModel,
    ReportClaimModel,
    SeasonModel,
    TacticalReportModel,
    TeamModel,
)
from tactical_analyst.db.session import get_db_session
from tactical_analyst.workers.jobs import LocalJobClient


def test_phase5_api_routes() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    job_client = LocalJobClient()

    with Session(engine) as session:
        _seed(session)

    app = create_app()

    def override_db() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_job_client] = lambda: job_client
    client = TestClient(app)

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/competitions").json()[0]["id"] == "competition:1"
    assert client.get("/competitions/competition:1/seasons").json()[0]["id"] == "season:1"
    assert client.get("/matches").json()[0]["id"] == "match:1"
    assert client.get("/matches/missing").status_code == 404
    assert client.get("/matches/match:1/metrics").json()[0]["metric_name"] == "xg"

    ingest = client.post("/matches/match:1/ingest").json()
    assert ingest["status"] == "queued"
    ingest_status = client.get(f"/jobs/{ingest['job_id']}").json()
    assert ingest_status["task_name"] == "tactical_analyst.ingest_match"

    analyze = client.post("/matches/match:1/analyze").json()
    assert analyze["status"] == "queued"
    assert (
        client.get(f"/jobs/{analyze['job_id']}").json()["task_name"]
        == "tactical_analyst.run_tactical_analysis"
    )

    report = client.get("/reports/report:1").json()
    assert report["id"] == "report:1"
    assert report["claims"][0]["id"] == "claim:1"
    assert client.get("/reports/report:1/evidence").json()["metrics"][0]["evidence_id"] == "E1"
    claim_evidence = client.get("/reports/report:1/claims/claim:1/evidence").json()
    assert claim_evidence["evidence"][0]["evidence_id"] == "E1"


def _seed(session: Session) -> None:
    session.add(
        CompetitionModel(
            id="competition:1",
            provider="statsbomb_open",
            provider_competition_id="1",
            name="Competition",
        )
    )
    session.add(
        SeasonModel(
            id="season:1",
            competition_id="competition:1",
            provider_season_id="1",
            name="Season",
        )
    )
    session.add_all(
        [
            TeamModel(id="team:home", name="Home", provider_ids={"statsbomb": "1"}),
            TeamModel(id="team:away", name="Away", provider_ids={"statsbomb": "2"}),
        ]
    )
    session.add(
        MatchModel(
            id="match:1",
            competition_id="competition:1",
            season_id="season:1",
            provider="statsbomb_open",
            provider_match_id="1",
            home_team_id="team:home",
            away_team_id="team:away",
            home_score=2,
            away_score=1,
            status="available",
            ingestion_version="test",
        )
    )
    session.add(
        CalculatedMetricModel(
            id="metric:1",
            match_id="match:1",
            entity_type="team",
            entity_id="team:home",
            metric_name="xg",
            metric_version="shots_xg_v1",
            value_numeric=1.2,
            source_event_ids=["event:1"],
            input_hash="hash",
        )
    )
    session.add(
        TacticalReportModel(
            id="report:1",
            match_id="match:1",
            report_version="v1",
            evidence_hash="evidence-hash",
            llm_provider="gemini",
            llm_model="gemini-2.5-flash",
            prompt_version="v1",
            report_json={"evidence": {"metrics": [{"evidence_id": "E1", "value": 1.2}]}},
            report_markdown="# Report",
            verification_status="passed",
        )
    )
    session.add(
        ReportClaimModel(
            id="claim:1",
            report_id="report:1",
            claim_text="Supported claim",
            claim_type="summary",
            strength="weak",
            verification_status="passed",
            evidence_ids=["E1"],
            caveats=[],
        )
    )
    session.commit()
