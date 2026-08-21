from __future__ import annotations

import json
from pathlib import Path

from tactical_analyst.providers.tracking.base import TrackingDataProvider
from tactical_analyst.schemas.tracking import TrackingFrame, TrackingProviderCapabilities


class LocalTrackingFileProvider(TrackingDataProvider):
    """Read canonical tracking frames from local JSON files.

    Expected layout:
    data/tracking/{match_id}.json
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    async def list_matches(self) -> list[dict]:
        return [
            {"match_id": path.stem, "uri": path.as_posix()}
            for path in self.root.glob("*.json")
        ]

    async def get_frames(self, match_id: str) -> list[TrackingFrame]:
        path = self.root / f"{match_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        frames = payload["frames"] if isinstance(payload, dict) else payload
        return [TrackingFrame.model_validate(frame) for frame in frames]

    def capabilities(self) -> TrackingProviderCapabilities:
        return TrackingProviderCapabilities(
            true_player_positions=True,
            ball_positions=True,
            velocities=False,
            event_links=False,
        )
