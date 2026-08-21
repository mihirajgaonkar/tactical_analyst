from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch, validate_pitch_coordinates


class ShotMapRenderer:
    asset_type = "shot_map"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Shot Map")
        shots = [
            event
            for event in context.events
            if event.event_type == "Shot" and validate_pitch_coordinates(event.x, event.y)
        ]
        team_colors = _team_colors(context.team_ids)
        for event in shots:
            size = 80 + (event.xg or 0) * 500
            marker = "*" if event.outcome == "Goal" else "o"
            ax.scatter(
                event.x,
                event.y,
                s=size,
                c=team_colors.get(event.team_id, "#2563eb"),
                edgecolors="#111827",
                marker=marker,
                alpha=0.85,
            )
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in shots],
            metadata={"shot_count": len(shots)},
        )


def _team_colors(team_ids: tuple[str, ...]) -> dict[str, str]:
    palette = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]
    return {team_id: palette[index % len(palette)] for index, team_id in enumerate(team_ids)}
