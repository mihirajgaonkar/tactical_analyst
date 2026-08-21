from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from tactical_analyst.ingestion.coordinates import (
    normalize_statsbomb_end_location,
    normalize_statsbomb_location,
)
from tactical_analyst.schemas.event import MatchEvent
from tactical_analyst.schemas.lineup import LineupPlayer
from tactical_analyst.schemas.match import Match, TeamRef

INGESTION_VERSION = "statsbomb_open_v1"


def normalize_statsbomb_match(raw: dict[str, Any]) -> Match:
    competition_id = f"statsbomb:{raw['competition']['competition_id']}"
    season_id = f"{competition_id}:{raw['season']['season_id']}"
    kickoff_at = _parse_datetime(raw.get("match_date"), raw.get("kick_off"))
    return Match(
        id=f"statsbomb:{raw['match_id']}",
        provider="statsbomb_open",
        provider_match_id=str(raw["match_id"]),
        competition_id=competition_id,
        season_id=season_id,
        home_team=TeamRef(
            id=f"statsbomb:{raw['home_team']['home_team_id']}",
            name=raw["home_team"]["home_team_name"],
            country=_name(raw["home_team"].get("country")),
        ),
        away_team=TeamRef(
            id=f"statsbomb:{raw['away_team']['away_team_id']}",
            name=raw["away_team"]["away_team_name"],
            country=_name(raw["away_team"].get("country")),
        ),
        kickoff_at=kickoff_at,
        home_score=raw.get("home_score"),
        away_score=raw.get("away_score"),
        status=raw.get("match_status", "available"),
        ingestion_version=INGESTION_VERSION,
    )


def normalize_statsbomb_lineups(
    match_id: str,
    raw_lineups: list[dict[str, Any]],
) -> list[LineupPlayer]:
    players: list[LineupPlayer] = []
    for team in raw_lineups:
        team_id = f"statsbomb:{team['team_id']}"
        for item in team.get("lineup", []):
            positions = item.get("positions") or []
            first_position = positions[0] if positions else {}
            players.append(
                LineupPlayer(
                    id=f"{match_id}:lineup:{item['player_id']}",
                    match_id=match_id,
                    team_id=team_id,
                    player_id=f"statsbomb:{item['player_id']}",
                    player_name=item["player_name"],
                    starter=bool(first_position.get("start_reason") == "Starting XI"),
                    position=_name(first_position.get("position")),
                    formation_slot=_as_str(first_position.get("position_id")),
                    shirt_number=item.get("jersey_number"),
                    start_second=_timestamp_to_ms(first_position.get("from") or "00:00") // 1000,
                    end_second=(
                        _timestamp_to_ms(first_position["to"]) // 1000
                        if first_position.get("to")
                        else None
                    ),
                )
            )
    return players


def normalize_statsbomb_events(match_id: str, raw_events: list[dict[str, Any]]) -> list[MatchEvent]:
    events = [_normalize_event(match_id, event) for event in raw_events]
    return sorted(events, key=lambda event: event.index)


def _normalize_event(match_id: str, event: dict[str, Any]) -> MatchEvent:
    event_type = _name(event.get("type")) or "Unknown"
    event_details = event.get(event_type.lower().replace(" ", "_"), {}) or {}
    x, y = normalize_statsbomb_location(event.get("location"))
    end_x, end_y = normalize_statsbomb_end_location(event)

    return MatchEvent(
        id=str(event["id"]),
        match_id=match_id,
        index=int(event.get("index", 0)),
        period=int(event.get("period", 0)),
        timestamp_ms=_timestamp_to_ms(event.get("timestamp", "00:00:00.000")),
        team_id=f"statsbomb:{event['team']['id']}",
        player_id=f"statsbomb:{event['player']['id']}" if event.get("player") else None,
        receiver_player_id=(
            f"statsbomb:{event_details['recipient']['id']}"
            if event_details.get("recipient")
            else None
        ),
        event_type=event_type,
        event_subtype=_name(event_details.get("type")),
        outcome=_name(event_details.get("outcome")),
        possession_id=_as_str(event.get("possession")),
        play_pattern=_name(event.get("play_pattern")),
        x=x,
        y=y,
        end_x=end_x,
        end_y=end_y,
        xg=_extract_xg(event_type, event_details),
        under_pressure=event.get("under_pressure"),
        related_event_ids=list(event.get("related_events", [])),
        provider_payload=event,
    )


def _extract_xg(event_type: str, details: dict[str, Any]) -> float | None:
    if event_type != "Shot":
        return None
    value = details.get("statsbomb_xg")
    return float(value) if value is not None else None


def _timestamp_to_ms(value: str) -> int:
    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        hours = 0
    else:
        hours, minutes, seconds = parts
    return int((int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000)


def _parse_datetime(match_date: str | None, kick_off: str | None) -> datetime | None:
    if not match_date:
        return None
    time_value = kick_off or "00:00:00.000"
    return datetime.fromisoformat(f"{match_date}T{time_value}").replace(tzinfo=UTC)


def _name(value: dict[str, Any] | None) -> str | None:
    return value.get("name") if value else None


def _as_str(value: Any) -> str | None:
    return str(value) if value is not None else None
