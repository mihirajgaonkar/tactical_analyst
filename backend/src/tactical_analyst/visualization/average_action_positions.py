from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch, validate_pitch_coordinates


class AverageActionPositionRenderer:
    asset_type = "average_action_positions"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Average Action Positions")
        events_by_player = defaultdict(list)
        for event in context.events:
            if event.player_id and validate_pitch_coordinates(event.x, event.y):
                events_by_player[event.player_id].append(event)
        positions = {}
        for player_id, events in events_by_player.items():
            x = sum(event.x for event in events if event.x is not None) / len(events)
            y = sum(event.y for event in events if event.y is not None) / len(events)
            positions[player_id] = {"x": round(x, 4), "y": round(y, 4), "actions": len(events)}
            ax.scatter(x, y, s=80 + len(events) * 18, c="#4f46e5", edgecolors="#111827", alpha=0.85)
            ax.text(x, y, player_id.rsplit(":", 1)[-1], ha="center", va="center", fontsize=7)
        source_events = [event for events in events_by_player.values() for event in events]
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in source_events],
            metadata={
                "player_count": len(positions),
                "positions": positions,
                "label": "Average Action Position",
            },
        )
