from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from tactical_analyst.db.models import (
    CalculatedMetricModel,
    CompetitionModel,
    MatchModel,
    ReportClaimModel,
    SeasonModel,
    TacticalReportModel,
    TeamModel,
)


def list_competitions(session: Session) -> list[CompetitionModel]:
    return list(session.scalars(select(CompetitionModel).order_by(CompetitionModel.name)).all())


def list_seasons(session: Session, competition_id: str) -> list[SeasonModel]:
    statement = (
        select(SeasonModel)
        .where(SeasonModel.competition_id == competition_id)
        .order_by(SeasonModel.name)
    )
    return list(session.scalars(statement).all())


def list_matches(
    session: Session,
    competition_id: str | None = None,
    season_id: str | None = None,
) -> list[MatchModel]:
    statement = select(MatchModel).order_by(MatchModel.kickoff_at.desc().nullslast())
    if competition_id:
        statement = statement.where(MatchModel.competition_id == competition_id)
    if season_id:
        statement = statement.where(MatchModel.season_id == season_id)
    return list(session.scalars(statement).all())


def get_match(session: Session, match_id: str) -> MatchModel | None:
    return session.get(MatchModel, match_id)


def get_team(session: Session, team_id: str) -> TeamModel | None:
    return session.get(TeamModel, team_id)


def list_metrics(session: Session, match_id: str) -> list[CalculatedMetricModel]:
    statement = (
        select(CalculatedMetricModel)
        .where(CalculatedMetricModel.match_id == match_id)
        .order_by(CalculatedMetricModel.metric_name, CalculatedMetricModel.entity_id)
    )
    return list(session.scalars(statement).all())


def get_report(session: Session, report_id: str) -> TacticalReportModel | None:
    return session.get(TacticalReportModel, report_id)


def find_existing_report(
    session: Session,
    *,
    match_id: str,
    evidence_hash: str,
    prompt_version: str,
    llm_provider: str,
    llm_model: str,
) -> TacticalReportModel | None:
    statement = select(TacticalReportModel).where(
        TacticalReportModel.match_id == match_id,
        TacticalReportModel.evidence_hash == evidence_hash,
        TacticalReportModel.prompt_version == prompt_version,
        TacticalReportModel.llm_provider == llm_provider,
        TacticalReportModel.llm_model == llm_model,
    )
    return session.scalar(statement)


def list_report_claims(session: Session, report_id: str) -> list[ReportClaimModel]:
    statement = select(ReportClaimModel).where(ReportClaimModel.report_id == report_id)
    return list(session.scalars(statement).all())


def get_report_claim(
    session: Session,
    report_id: str,
    claim_id: str,
) -> ReportClaimModel | None:
    statement = select(ReportClaimModel).where(
        ReportClaimModel.report_id == report_id,
        ReportClaimModel.id == claim_id,
    )
    return session.scalar(statement)
