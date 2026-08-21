from typing import Any, Protocol

from tactical_analyst.providers.soccer.capabilities import ProviderCapabilities


class SoccerDataProvider(Protocol):
    """Provider-neutral soccer data access interface."""

    async def list_competitions(self) -> list[dict[str, Any]]:
        """List available competitions and seasons."""

    async def list_matches(self, competition_id: str, season_id: str) -> list[dict[str, Any]]:
        """List matches for a provider competition and season."""

    async def get_match(self, match_id: str) -> dict[str, Any]:
        """Return provider match metadata by provider match ID."""

    async def get_lineups(self, match_id: str) -> list[dict[str, Any]]:
        """Return raw provider lineups."""

    async def get_events(self, match_id: str) -> list[dict[str, Any]]:
        """Return raw provider events."""

    async def get_frames(self, match_id: str) -> list[dict[str, Any]]:
        """Return provider freeze-frame or tracking data where available."""

    def capabilities(self) -> ProviderCapabilities:
        """Describe provider capability support."""
