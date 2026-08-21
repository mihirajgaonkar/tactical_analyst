from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TacticalClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    topic: str
    claim: str
    evidence_ids: list[str]
    strength: Literal["weak", "moderate", "strong"]
    caveats: list[str] = Field(default_factory=list)


class TacticalInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_summary: str
    claims: list[TacticalClaim] = Field(default_factory=list)
    turning_points: list[TacticalClaim] = Field(default_factory=list)
    player_findings: list[TacticalClaim] = Field(default_factory=list)


class FinalReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    sections: list[dict]
    markdown: str
