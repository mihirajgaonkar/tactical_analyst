from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tactical_analyst.analytics.base import MatchContext


@dataclass(frozen=True)
class VisualizationAsset:
    """Generated visualization metadata returned to API/workflow layers."""

    match_id: str
    asset_type: str
    version: str
    uri: str
    format: str
    source_event_ids: list[str]
    metadata: dict


class VisualizationRenderer(Protocol):
    """Common interface for deterministic visualization renderers."""

    asset_type: str
    version: str

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        """Render one visualization asset."""


def stable_asset_path(output_dir: Path, match_id: str, asset_type: str, version: str) -> Path:
    """Create a deterministic PNG path for a match visualization."""

    safe_match_id = match_id.replace(":", "_").replace("/", "_")
    return output_dir / f"{safe_match_id}_{asset_type}_{version}.png"


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def save_figure(fig, path: Path) -> None:
    """Save and close a matplotlib figure."""

    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    pyplot = _import_pyplot()
    pyplot.close(fig)


def _import_pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt
