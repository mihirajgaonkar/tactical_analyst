from pydantic import BaseModel, ConfigDict


class LineupPlayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    match_id: str
    team_id: str
    player_id: str
    player_name: str
    starter: bool
    position: str | None = None
    formation_slot: str | None = None
    shirt_number: int | None = None
    start_second: int = 0
    end_second: int | None = None
