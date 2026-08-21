from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path


class XgTimelineRenderer:
    asset_type = "xg_timeline"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
        shots = sorted(
            [event for event in context.events if event.event_type == "Shot"],
            key=lambda event: event.timestamp_ms,
        )
        by_team: dict[str, list] = defaultdict(list)
        for event in shots:
            by_team[event.team_id].append(event)
        for team_id, team_shots in by_team.items():
            total = 0.0
            xs = [0.0]
            ys = [0.0]
            for event in team_shots:
                total += event.xg or 0
                xs.append(event.timestamp_ms / 60000)
                ys.append(round(total, 4))
            ax.step(xs, ys, where="post", label=team_id)
        ax.set_xlabel("Minute")
        ax.set_ylabel("Cumulative xG")
        ax.set_title("xG Timeline")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
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
