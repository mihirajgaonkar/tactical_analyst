from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.visualization.average_action_positions import AverageActionPositionRenderer
from tactical_analyst.visualization.base import (
    VisualizationAsset,
    VisualizationRenderer,
    ensure_output_dir,
)
from tactical_analyst.visualization.defensive_actions import DefensiveActionsRenderer
from tactical_analyst.visualization.entries import EntryMapRenderer
from tactical_analyst.visualization.heatmap import HeatmapRenderer
from tactical_analyst.visualization.passing_network import PassingNetworkRenderer
from tactical_analyst.visualization.progressive_actions import ProgressiveActionsRenderer
from tactical_analyst.visualization.shot_map import ShotMapRenderer
from tactical_analyst.visualization.xg_timeline import XgTimelineRenderer

VISUALIZATION_REGISTRY: dict[str, VisualizationRenderer] = {
    "shot_map": ShotMapRenderer(),
    "xg_timeline": XgTimelineRenderer(),
    "passing_network": PassingNetworkRenderer(),
    "progressive_actions": ProgressiveActionsRenderer(),
    "defensive_actions": DefensiveActionsRenderer(),
    "entry_map": EntryMapRenderer(),
    "attacking_heatmap": HeatmapRenderer(),
    "average_action_positions": AverageActionPositionRenderer(),
}


def render_all_visualizations(
    context: MatchContext,
    output_dir: Path,
    registry: dict[str, VisualizationRenderer] | None = None,
) -> list[VisualizationAsset]:
    """Render every registered report visualization."""

    ensure_output_dir(output_dir)
    renderers = registry or VISUALIZATION_REGISTRY
    return [renderer.render(context, output_dir) for renderer in renderers.values()]
