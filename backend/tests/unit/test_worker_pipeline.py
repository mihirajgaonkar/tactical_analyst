from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from tactical_analyst.config.settings import Settings
from tactical_analyst.db.models import (
    Base,
    CompetitionModel,
    MatchEventModel,
    MatchModel,
    SeasonModel,
    TeamModel,
)
from tactical_analyst.llm.schemas import FinalReport, TacticalClaim, TacticalInterpretation
from tactical_analyst.workers import pipeline
from tests.fixtures.analytics_sample import sample_context


class FakeLLMService:
    def interpret(self, evidence_packet):
        return TacticalInterpretation(
            match_summary="The synthetic match has supported evidence.",
            claims=[
                TacticalClaim(
                    claim_id="c1",
                    topic="shots",
                    claim="Team A generated shot volume.",
                    evidence_ids=["METRIC_SHOTS_TEAM_A"],
                    strength="weak",
                )
            ],
        )

    def final_report(self, evidence_packet, interpretation):
        return FinalReport(
            title="Synthetic report",
            sections=[],
            markdown="Synthetic report grounded in 3 shots.",
        )


def test_worker_pipeline_calculates_metrics_and_persists_report(monkeypatch) -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        _seed_match(session)

    settings = Settings(
        database_url="sqlite://",
        object_storage_path=Path("data/test_object_store"),
        google_api_key="test-key",
    )
    metrics_result = pipeline.calculate_match_metrics_pipeline(
        "match:analytics",
        settings=settings,
        session_factory=session_factory,
    )

    assert metrics_result["status"] == "completed"
    assert metrics_result["metrics_calculated"] > 0

    monkeypatch.setattr(pipeline, "_build_llm_service", lambda settings: FakeLLMService())
    monkeypatch.setattr(pipeline, "render_all_visualizations", lambda context, output_dir: [])

    report_result = pipeline.run_tactical_analysis_pipeline(
        "match:analytics",
        settings=settings,
        session_factory=session_factory,
    )

    assert report_result["status"] == "completed"
    assert report_result["report_id"].startswith("report:")


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def _seed_match(session: Session) -> None:
    context = sample_context()
    session.add(
        CompetitionModel(
            id="competition:test",
            provider="statsbomb_open",
            provider_competition_id="test",
            name="Synthetic Competition",
        )
    )
    session.add(
        SeasonModel(
            id="season:test",
            competition_id="competition:test",
            provider_season_id="test",
            name="Synthetic Season",
        )
    )
    session.add_all(
        [
            TeamModel(id="team:a", name="Team A", provider_ids={"statsbomb": "a"}),
            TeamModel(id="team:b", name="Team B", provider_ids={"statsbomb": "b"}),
        ]
    )
    session.add(
        MatchModel(
            id="match:analytics",
            competition_id="competition:test",
            season_id="season:test",
            provider="statsbomb_open",
            provider_match_id="analytics",
            home_team_id="team:a",
            away_team_id="team:b",
            home_score=1,
            away_score=0,
            status="available",
            raw_payload_hash="test-input-hash",
            ingestion_version="test",
        )
    )
    for event in context.events:
        session.add(
            MatchEventModel(
                id=f"{event.match_id}:event:{event.id}",
                match_id=event.match_id,
                provider_event_id=event.id,
                event_index=event.index,
                period=event.period,
                timestamp_ms=event.timestamp_ms,
                team_id=event.team_id,
                player_id=event.player_id,
                receiver_player_id=event.receiver_player_id,
                event_type=event.event_type,
                event_subtype=event.event_subtype,
                outcome=event.outcome,
                possession_id=event.possession_id,
                play_pattern=event.play_pattern,
                x=event.x,
                y=event.y,
                end_x=event.end_x,
                end_y=event.end_y,
                xg=event.xg,
                under_pressure=event.under_pressure,
                related_event_ids=event.related_event_ids,
                provider_payload=event.provider_payload,
            )
        )
    session.commit()
