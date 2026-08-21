from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.db.models import LineupModel, MatchEventModel, MatchModel
from tactical_analyst.providers.soccer.capabilities import ProviderCapabilities
from tactical_analyst.schemas.event import MatchEvent
from tactical_analyst.schemas.lineup import LineupPlayer


def load_match_context(
    session: Session,
    match_id: str,
    *,
    capabilities: ProviderCapabilities | None = None,
) -> MatchContext:
    """Rebuild a deterministic analytics context from persisted canonical rows."""

    match = session.get(MatchModel, match_id)
    if match is None:
        raise LookupError(f"Match not found: {match_id}")

    event_rows = list(
        session.scalars(
            select(MatchEventModel)
            .where(MatchEventModel.match_id == match_id)
            .order_by(MatchEventModel.event_index)
        ).all()
    )
    if not event_rows:
        raise LookupError(f"No events found for match: {match_id}")

    lineup_rows = list(
        session.scalars(select(LineupModel).where(LineupModel.match_id == match_id)).all()
    )
    team_ids = tuple(dict.fromkeys(event.team_id for event in event_rows))
    return MatchContext(
        match_id=match_id,
        events=[_event_from_row(row) for row in event_rows],
        team_ids=team_ids,
        lineups=[_lineup_from_row(row) for row in lineup_rows],
        capabilities=capabilities,
        input_hash=match.raw_payload_hash,
    )


def _event_from_row(row: MatchEventModel) -> MatchEvent:
    return MatchEvent(
        id=row.provider_event_id,
        match_id=row.match_id,
        index=row.event_index,
        period=row.period,
        timestamp_ms=row.timestamp_ms,
        team_id=row.team_id,
        player_id=row.player_id,
        receiver_player_id=row.receiver_player_id,
        event_type=row.event_type,
        event_subtype=row.event_subtype,
        outcome=row.outcome,
        possession_id=row.possession_id,
        play_pattern=row.play_pattern,
        x=row.x,
        y=row.y,
        end_x=row.end_x,
        end_y=row.end_y,
        xg=row.xg,
        under_pressure=row.under_pressure,
        related_event_ids=list(row.related_event_ids or []),
        provider_payload=dict(row.provider_payload or {}),
    )


def _lineup_from_row(row: LineupModel) -> LineupPlayer:
    return LineupPlayer(
        id=row.id,
        match_id=row.match_id,
        team_id=row.team_id,
        player_id=row.player_id,
        player_name=row.player_id,
        starter=row.starter,
        position=row.position,
        formation_slot=row.formation_slot,
        shirt_number=row.shirt_number,
        start_second=row.start_second,
        end_second=row.end_second,
    )
