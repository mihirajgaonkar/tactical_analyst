from tactical_analyst.db.models import (
    CalculatedMetricModel,
    CompetitionModel,
    MatchModel,
    ReportClaimModel,
    SeasonModel,
    TacticalReportModel,
    TeamModel,
)


def competition_to_dict(competition: CompetitionModel) -> dict:
    return {
        "id": competition.id,
        "provider": competition.provider,
        "provider_competition_id": competition.provider_competition_id,
        "name": competition.name,
        "country": competition.country,
        "gender": competition.gender,
    }


def season_to_dict(season: SeasonModel) -> dict:
    return {
        "id": season.id,
        "competition_id": season.competition_id,
        "provider_season_id": season.provider_season_id,
        "name": season.name,
        "start_date": season.start_date,
        "end_date": season.end_date,
    }


def team_to_dict(team: TeamModel | None) -> dict | None:
    if team is None:
        return None
    return {"id": team.id, "name": team.name, "country": team.country}


def match_to_dict(
    match: MatchModel,
    home_team: TeamModel | None,
    away_team: TeamModel | None,
) -> dict:
    return {
        "id": match.id,
        "competition_id": match.competition_id,
        "season_id": match.season_id,
        "provider": match.provider,
        "provider_match_id": match.provider_match_id,
        "home_team": team_to_dict(home_team),
        "away_team": team_to_dict(away_team),
        "kickoff_at": match.kickoff_at,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "status": match.status,
        "raw_payload_uri": match.raw_payload_uri,
        "raw_payload_hash": match.raw_payload_hash,
        "ingestion_version": match.ingestion_version,
    }


def metric_to_dict(metric: CalculatedMetricModel) -> dict:
    return {
        "id": metric.id,
        "match_id": metric.match_id,
        "entity_type": metric.entity_type,
        "entity_id": metric.entity_id,
        "metric_name": metric.metric_name,
        "metric_version": metric.metric_version,
        "window_start_ms": metric.window_start_ms,
        "window_end_ms": metric.window_end_ms,
        "value_numeric": metric.value_numeric,
        "value_json": metric.value_json,
        "sample_size": metric.sample_size,
        "source_event_ids": metric.source_event_ids,
        "input_hash": metric.input_hash,
    }


def report_to_dict(report: TacticalReportModel) -> dict:
    return {
        "id": report.id,
        "match_id": report.match_id,
        "report_version": report.report_version,
        "evidence_hash": report.evidence_hash,
        "llm_provider": report.llm_provider,
        "llm_model": report.llm_model,
        "prompt_version": report.prompt_version,
        "report_json": report.report_json,
        "report_markdown": report.report_markdown,
        "verification_status": report.verification_status,
        "input_tokens": report.input_tokens,
        "output_tokens": report.output_tokens,
        "llm_cost": report.llm_cost,
    }


def claim_to_dict(claim: ReportClaimModel) -> dict:
    return {
        "id": claim.id,
        "report_id": claim.report_id,
        "claim_text": claim.claim_text,
        "claim_type": claim.claim_type,
        "strength": claim.strength,
        "verification_status": claim.verification_status,
        "evidence_ids": claim.evidence_ids,
        "caveats": claim.caveats,
    }
