from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CompetitionModel(Base):
    __tablename__ = "competitions"
    __table_args__ = (UniqueConstraint("provider", "provider_competition_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_competition_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str | None] = mapped_column(String)
    gender: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SeasonModel(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("competition_id", "provider_season_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    competition_id: Mapped[str] = mapped_column(ForeignKey("competitions.id"), nullable=False)
    provider_season_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str | None] = mapped_column(String)
    provider_ids: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    primary_position: Mapped[str | None] = mapped_column(String)
    provider_ids: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class MatchModel(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("provider", "provider_match_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    competition_id: Mapped[str] = mapped_column(ForeignKey("competitions.id"), nullable=False)
    season_id: Mapped[str] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_match_id: Mapped[str] = mapped_column(String, nullable=False)
    home_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    kickoff_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, nullable=False)
    raw_payload_uri: Mapped[str | None] = mapped_column(String)
    raw_payload_hash: Mapped[str | None] = mapped_column(String)
    ingestion_version: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LineupModel(Base):
    __tablename__ = "lineups"
    __table_args__ = (UniqueConstraint("match_id", "team_id", "player_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), nullable=False)
    starter: Mapped[bool] = mapped_column(nullable=False)
    position: Mapped[str | None] = mapped_column(String)
    formation_slot: Mapped[str | None] = mapped_column(String)
    shirt_number: Mapped[int | None] = mapped_column(Integer)
    start_second: Mapped[int] = mapped_column(Integer, nullable=False)
    end_second: Mapped[int | None] = mapped_column(Integer)


class MatchEventModel(Base):
    __tablename__ = "match_events"
    __table_args__ = (
        UniqueConstraint("match_id", "provider_event_id"),
        Index("ix_match_events_match_index", "match_id", "event_index"),
        Index("ix_match_events_match_timestamp", "match_id", "timestamp_ms"),
        Index("ix_match_events_match_team_type", "match_id", "team_id", "event_type"),
        Index("ix_match_events_match_player", "match_id", "player_id"),
        Index("ix_match_events_match_possession", "match_id", "possession_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), nullable=False)
    provider_event_id: Mapped[str] = mapped_column(String, nullable=False)
    event_index: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[str | None] = mapped_column(ForeignKey("players.id"))
    receiver_player_id: Mapped[str | None] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_subtype: Mapped[str | None] = mapped_column(String)
    outcome: Mapped[str | None] = mapped_column(String)
    possession_id: Mapped[str | None] = mapped_column(String)
    play_pattern: Mapped[str | None] = mapped_column(String)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)
    end_x: Mapped[float | None] = mapped_column(Float)
    end_y: Mapped[float | None] = mapped_column(Float)
    xg: Mapped[float | None] = mapped_column(Float)
    under_pressure: Mapped[bool | None] = mapped_column()
    related_event_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    provider_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class PlayerMatchStatsModel(Base):
    __tablename__ = "player_match_stats"

    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.id"), primary_key=True)
    minutes: Mapped[float] = mapped_column(Float, default=0)
    passes: Mapped[int] = mapped_column(Integer, default=0)
    completed_passes: Mapped[int] = mapped_column(Integer, default=0)
    progressive_passes: Mapped[int] = mapped_column(Integer, default=0)
    carries: Mapped[int] = mapped_column(Integer, default=0)
    progressive_carries: Mapped[int] = mapped_column(Integer, default=0)
    shots: Mapped[int] = mapped_column(Integer, default=0)
    xg: Mapped[float] = mapped_column(Float, default=0)
    pressures: Mapped[int] = mapped_column(Integer, default=0)
    tackles: Mapped[int] = mapped_column(Integer, default=0)
    interceptions: Mapped[int] = mapped_column(Integer, default=0)
    recoveries: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class TeamMatchStatsModel(Base):
    __tablename__ = "team_match_stats"

    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    possession: Mapped[float | None] = mapped_column(Float)
    shots: Mapped[int] = mapped_column(Integer, default=0)
    xg: Mapped[float] = mapped_column(Float, default=0)
    passes: Mapped[int] = mapped_column(Integer, default=0)
    progressive_passes: Mapped[int] = mapped_column(Integer, default=0)
    progressive_carries: Mapped[int] = mapped_column(Integer, default=0)
    ppda: Mapped[float | None] = mapped_column(Float)
    field_tilt: Mapped[float | None] = mapped_column(Float)
    final_third_entries: Mapped[int] = mapped_column(Integer, default=0)
    box_entries: Mapped[int] = mapped_column(Integer, default=0)
    high_turnovers: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class CalculatedMetricModel(Base):
    __tablename__ = "calculated_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String)
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    metric_version: Mapped[str] = mapped_column(String, nullable=False)
    window_start_ms: Mapped[int | None] = mapped_column(Integer)
    window_end_ms: Mapped[int | None] = mapped_column(Integer)
    value_numeric: Mapped[float | None] = mapped_column(Float)
    value_json: Mapped[dict | None] = mapped_column(JSON)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    source_event_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    input_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TacticalReportModel(Base):
    __tablename__ = "tactical_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), nullable=False)
    report_version: Mapped[str] = mapped_column(String, nullable=False)
    evidence_hash: Mapped[str] = mapped_column(String, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String, nullable=False)
    llm_model: Mapped[str] = mapped_column(String, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String, nullable=False)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    report_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    verification_status: Mapped[str] = mapped_column(String, nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    llm_cost: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReportClaimModel(Base):
    __tablename__ = "report_claims"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("tactical_reports.id"), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String, nullable=False)
    strength: Mapped[str] = mapped_column(String, nullable=False)
    verification_status: Mapped[str] = mapped_column(String, nullable=False)
    evidence_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    caveats: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
