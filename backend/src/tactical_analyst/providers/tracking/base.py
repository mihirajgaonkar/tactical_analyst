from __future__ import annotations

from typing import Protocol

from tactical_analyst.schemas.tracking import (
    TrackingFrame,
    TrackingProviderCapabilities,
)


class TrackingDataProvider(Protocol):
    """Provider-neutral interface for true tracking / off-ball data."""

    async def list_matches(self) -> list[dict]:
        """Return provider-specific tracking match metadata."""

    async def get_frames(self, match_id: str) -> list[TrackingFrame]:
        """Return canonical tracking frames for a match."""

    def capabilities(self) -> TrackingProviderCapabilities:
        """Return the metrics supported by this tracking provider."""
