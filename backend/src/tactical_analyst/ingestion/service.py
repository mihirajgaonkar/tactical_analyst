from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from tactical_analyst.db.models import (
    CompetitionModel,
    LineupModel,
    MatchEventModel,
    MatchModel,
    PlayerModel,
    SeasonModel,
    TeamModel,
)
from tactical_analyst.ingestion.normalizer import (
    INGESTION_VERSION,
    normalize_statsbomb_events,
    normalize_statsbomb_lineups,
    normalize_statsbomb_match,
)
from tactical_analyst.ingestion.validators import validate_events
from tactical_analyst.providers.soccer.base import SoccerDataProvider
from tactical_analyst.schemas.event import MatchEvent
from tactical_analyst.schemas.lineup import LineupPlayer
from tactical_analyst.schemas.match import Match
from tactical_analyst.storage.base import ObjectStorage


@dataclass(frozen=True)
class IngestionResult:
    match_id: str
    raw_payload_uri: str
    raw_payload_hash: str
    events_ingested: int
    lineups_ingested: int


class MatchIngestionService:
    """Coordinates provider reads, raw storage, normalization, and database persistence."""

    def __init__(
        self,
        provider: SoccerDataProvider,
        storage: ObjectStorage,
        session: Session,
    ) -> None:
        self.provider = provider
        self.storage = storage
        self.session = session

    async def ingest_match(self, provider_match_id: str) -> IngestionResult:
        raw_match = await self.provider.get_match(provider_match_id)
        raw_lineups = await self.provider.get_lineups(provider_match_id)
        raw_events = await self.provider.get_events(provider_match_id)

        match = normalize_statsbomb_match(raw_match)
        lineups = normalize_statsbomb_lineups(match.id, raw_lineups)
        events = normalize_statsbomb_events(match.id, raw_events)
        validate_events(events)

        raw_payload_uri, raw_payload_hash = self.storage.put_json_gz(
            f"raw/statsbomb/{match.provider_match_id}.json.gz",
            {"match": raw_match, "lineups": raw_lineups, "events": raw_events},
        )
        match.raw_payload_uri = raw_payload_uri
        match.raw_payload_hash = raw_payload_hash

        self._upsert_match_graph(match, lineups)
        self._replace_match_events(match.id, events)
        self.session.commit()

        return IngestionResult(
            match_id=match.id,
            raw_payload_uri=raw_payload_uri,
            raw_payload_hash=raw_payload_hash,
            events_ingested=len(events),
            lineups_ingested=len(lineups),
        )

    def _upsert_match_graph(self, match: Match, lineups: Sequence[LineupPlayer]) -> None:
        competition = self.session.get(CompetitionModel, match.competition_id)
        if competition is None:
            self.session.add(
                CompetitionModel(
                    id=match.competition_id,
                    provider=match.provider,
                    provider_competition_id=match.competition_id.rsplit(":", 1)[-1],
                    name=match.competition_id,
                )
            )

        season = self.session.get(SeasonModel, match.season_id)
        if season is None:
            self.session.add(
                SeasonModel(
                    id=match.season_id,
                    competition_id=match.competition_id,
                    provider_season_id=match.season_id.rsplit(":", 1)[-1],
                    name=match.season_id,
                )
            )

        self._upsert_team(match.home_team.id, match.home_team.name, match.home_team.country)
        self._upsert_team(match.away_team.id, match.away_team.name, match.away_team.country)

        db_match = self.session.get(MatchModel, match.id)
        values = {
            "competition_id": match.competition_id,
            "season_id": match.season_id,
            "provider": match.provider,
            "provider_match_id": match.provider_match_id,
            "home_team_id": match.home_team.id,
            "away_team_id": match.away_team.id,
            "kickoff_at": match.kickoff_at,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "status": match.status,
            "raw_payload_uri": match.raw_payload_uri,
            "raw_payload_hash": match.raw_payload_hash,
            "ingestion_version": INGESTION_VERSION,
        }
        if db_match is None:
            self.session.add(MatchModel(id=match.id, **values))
        else:
            for key, value in values.items():
                setattr(db_match, key, value)

        self.session.flush()
        self._replace_lineups(match.id, lineups)

    def _replace_lineups(self, match_id: str, lineups: Sequence[LineupPlayer]) -> None:
        self.session.query(LineupModel).filter(LineupModel.match_id == match_id).delete()
        for lineup in lineups:
            self._upsert_team(lineup.team_id, lineup.team_id)
            self._upsert_player(lineup.player_id, lineup.player_name, lineup.position)
            self.session.add(
                LineupModel(
                    id=lineup.id,
                    match_id=lineup.match_id,
                    team_id=lineup.team_id,
                    player_id=lineup.player_id,
                    starter=lineup.starter,
                    position=lineup.position,
                    formation_slot=lineup.formation_slot,
                    shirt_number=lineup.shirt_number,
                    start_second=lineup.start_second,
                    end_second=lineup.end_second,
                )
            )

    def _replace_match_events(self, match_id: str, events: Sequence[MatchEvent]) -> None:
        self.session.query(MatchEventModel).filter(MatchEventModel.match_id == match_id).delete()
        for event in events:
            self._ensure_event_player(event.player_id, event.provider_payload.get("player"))
            self._upsert_team(
                event.team_id,
                _provider_name(event.provider_payload.get("team")) or event.team_id,
            )
            self.session.add(
                MatchEventModel(
                    id=f"{match_id}:event:{event.id}",
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

    def _upsert_team(self, team_id: str, name: str, country: str | None = None) -> None:
        team = self.session.get(TeamModel, team_id)
        provider_ids = {"statsbomb": team_id.rsplit(":", 1)[-1]}
        if team is None:
            self.session.add(
                TeamModel(id=team_id, name=name, country=country, provider_ids=provider_ids)
            )
        else:
            team.name = name
            team.country = country or team.country
            team.provider_ids = {**team.provider_ids, **provider_ids}

    def _upsert_player(
        self,
        player_id: str,
        name: str,
        primary_position: str | None = None,
    ) -> None:
        player = self.session.get(PlayerModel, player_id)
        provider_ids = {"statsbomb": player_id.rsplit(":", 1)[-1]}
        if player is None:
            self.session.add(
                PlayerModel(
                    id=player_id,
                    name=name,
                    primary_position=primary_position,
                    provider_ids=provider_ids,
                )
            )
        else:
            player.name = name
            player.primary_position = primary_position or player.primary_position
            player.provider_ids = {**player.provider_ids, **provider_ids}

    def _ensure_event_player(
        self,
        player_id: str | None,
        raw_player: dict[str, Any] | None,
    ) -> None:
        if player_id is None:
            return
        self._upsert_player(player_id, _provider_name(raw_player) or player_id)


def _provider_name(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return value.get("name")
