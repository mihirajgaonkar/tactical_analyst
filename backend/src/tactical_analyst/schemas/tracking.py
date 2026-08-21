from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TrackingPlayerFrame(BaseModel):
    """One player's true tracked location at a frame timestamp."""

    model_config = ConfigDict(extra="forbid")

    player_id: str
    team_id: str
    x: float
    y: float
    speed_mps: float | None = None

    @field_validator("x")
    @classmethod
    def x_inside_pitch(cls, value: float) -> float:
        if not 0 <= value <= 105:
            raise ValueError("tracking x coordinate must be between 0 and 105 meters")
        return value

    @field_validator("y")
    @classmethod
    def y_inside_pitch(cls, value: float) -> float:
        if not 0 <= value <= 68:
            raise ValueError("tracking y coordinate must be between 0 and 68 meters")
        return value


class TrackingFrame(BaseModel):
    """Canonical tracking frame independent from a vendor payload."""

    model_config = ConfigDict(extra="forbid")

    match_id: str
    frame_id: str
    period: int
    timestamp_ms: int
    ball_x: float | None = None
    ball_y: float | None = None
    players: list[TrackingPlayerFrame] = Field(default_factory=list)
    provider_payload: dict = Field(default_factory=dict)


class TrackingProviderCapabilities(BaseModel):
    """Capabilities advertised by a tracking data provider."""

    true_player_positions: bool = True
    ball_positions: bool = False
    velocities: bool = False
    event_links: bool = False
