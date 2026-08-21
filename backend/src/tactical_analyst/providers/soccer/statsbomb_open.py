from __future__ import annotations

from typing import Any

import httpx

from tactical_analyst.providers.soccer.capabilities import (
    STATSBOMB_OPEN_DATA_CAPABILITIES,
    ProviderCapabilities,
)


class StatsBombOpenDataProvider:
    """StatsBomb Open Data adapter returning raw provider JSON."""

    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client

    def capabilities(self) -> ProviderCapabilities:
        return STATSBOMB_OPEN_DATA_CAPABILITIES

    async def list_competitions(self) -> list[dict[str, Any]]:
        return await self._get_json("competitions.json")

    async def list_matches(self, competition_id: str, season_id: str) -> list[dict[str, Any]]:
        return await self._get_json(f"matches/{competition_id}/{season_id}.json")

    async def get_match(self, match_id: str) -> dict[str, Any]:
        for competition in await self.list_competitions():
            matches = await self.list_matches(
                str(competition["competition_id"]),
                str(competition["season_id"]),
            )
            for match in matches:
                if str(match["match_id"]) == str(match_id):
                    return match
        raise LookupError(f"StatsBomb match not found: {match_id}")

    async def get_lineups(self, match_id: str) -> list[dict[str, Any]]:
        return await self._get_json(f"lineups/{match_id}.json")

    async def get_events(self, match_id: str) -> list[dict[str, Any]]:
        return await self._get_json(f"events/{match_id}.json")

    async def get_frames(self, match_id: str) -> list[dict[str, Any]]:
        return []

    async def _get_json(self, path: str) -> Any:
        if self._client is not None:
            response = await self._client.get(f"{self.base_url}/{path}")
            response.raise_for_status()
            return response.json()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/{path}")
            response.raise_for_status()
            return response.json()
