from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch, validate_pitch_coordinates


class HeatmapRenderer:
    asset_type = "attacking_heatmap"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Attacking Heatmap")
        events = [
            event
            for event in context.events
            if event.event_type not in {"Substitution"}
            and validate_pitch_coordinates(event.x, event.y)
        ]
        xs = [event.x for event in events]
        ys = [event.y for event in events]
        if xs and ys:
            ax.hist2d(xs, ys, bins=(12, 8), cmap="YlGnBu", alpha=0.75)
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in events],
            metadata={"event_count": len(events)},
        )
