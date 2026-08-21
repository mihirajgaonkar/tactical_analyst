from pydantic import BaseModel


class ProviderCapabilities(BaseModel):
    """Capabilities exposed by a soccer data provider."""

    event_coordinates: bool
    pass_events: bool
    carry_events: bool
    pressure_events: bool
    xg: bool
    possession_ids: bool
    lineups: bool
    formations: bool
    substitutions: bool
    freeze_frames_360: bool
    tracking: bool


STATSBOMB_OPEN_DATA_CAPABILITIES = ProviderCapabilities(
    event_coordinates=True,
    pass_events=True,
    carry_events=True,
    pressure_events=True,
    xg=True,
    possession_ids=True,
    lineups=True,
    formations=True,
    substitutions=True,
    freeze_frames_360=False,
    tracking=False,
)
