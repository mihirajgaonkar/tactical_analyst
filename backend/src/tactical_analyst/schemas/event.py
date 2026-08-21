from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MatchEvent(BaseModel):
    """Canonical event model normalized from provider event data."""

    model_config = ConfigDict(extra="forbid")

    id: str
    match_id: str
    index: int
    period: int
    timestamp_ms: int

    team_id: str
    player_id: str | None = None
    receiver_player_id: str | None = None

    event_type: str
    event_subtype: str | None = None
    outcome: str | None = None

    possession_id: str | None = None
    play_pattern: str | None = None

    x: float | None = None
    y: float | None = None
    end_x: float | None = None
    end_y: float | None = None

    xg: float | None = None
    under_pressure: bool | None = None

    related_event_ids: list[str] = Field(default_factory=list)
    provider_payload: dict[str, Any]

    @field_validator("x", "end_x")
    @classmethod
    def x_inside_pitch(cls, value: float | None) -> float | None:
        if value is not None and not 0 <= value <= 105:
            raise ValueError("x coordinate must be between 0 and 105 meters")
        return value

    @field_validator("y", "end_y")
    @classmethod
    def y_inside_pitch(cls, value: float | None) -> float | None:
        if value is not None and not 0 <= value <= 68:
            raise ValueError("y coordinate must be between 0 and 68 meters")
        return value
