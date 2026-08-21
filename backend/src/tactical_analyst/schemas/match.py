from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TeamRef(BaseModel):
    id: str
    name: str
    country: str | None = None


class Competition(BaseModel):
    id: str
    provider: str
    provider_competition_id: str
    name: str
    country: str | None = None
    gender: str | None = None


class Season(BaseModel):
    id: str
    competition_id: str
    provider_season_id: str
    name: str


class Match(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    provider: str
    provider_match_id: str
    competition_id: str
    season_id: str
    home_team: TeamRef
    away_team: TeamRef
    kickoff_at: datetime | None = None
    home_score: int | None = None
    away_score: int | None = None
    status: str = "available"
    raw_payload_uri: str | None = None
    raw_payload_hash: str | None = None
    ingestion_version: str
