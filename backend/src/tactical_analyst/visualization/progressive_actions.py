from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.analytics.helpers import has_start_end, is_carry, is_pass, is_progressive
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch


class ProgressiveActionsRenderer:
    asset_type = "progressive_actions"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Progressive Passes and Carries")
        actions = [
            event
            for event in context.events
            if (
                (is_pass(event) or is_carry(event))
                and has_start_end(event)
                and is_progressive(event)
            )
        ]
        for event in actions:
            color = "#2563eb" if is_pass(event) else "#f97316"
            ax.annotate(
                "",
                xy=(event.end_x, event.end_y),
                xytext=(event.x, event.y),
                arrowprops={"arrowstyle": "->", "color": color, "lw": 1.4, "alpha": 0.75},
            )
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in actions],
            metadata={
                "progressive_actions": len(actions),
                "progressive_passes": sum(1 for event in actions if is_pass(event)),
                "progressive_carries": sum(1 for event in actions if is_carry(event)),
            },
        )
