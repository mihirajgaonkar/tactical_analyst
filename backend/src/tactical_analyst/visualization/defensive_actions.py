from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.analytics.helpers import DEFENSIVE_ACTION_TYPES
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch, validate_pitch_coordinates


class DefensiveActionsRenderer:
    asset_type = "defensive_actions"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Defensive Actions")
        actions = [
            event
            for event in context.events
            if event.event_type in DEFENSIVE_ACTION_TYPES
            and validate_pitch_coordinates(event.x, event.y)
        ]
        for event in actions:
            ax.scatter(event.x, event.y, s=70, c="#7c2d12", edgecolors="#111827", alpha=0.8)
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in actions],
            metadata={"defensive_actions": len(actions)},
        )
