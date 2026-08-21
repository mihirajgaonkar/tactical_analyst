from __future__ import annotations

from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.analytics.helpers import crosses_final_third, enters_box, has_start_end
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch


class EntryMapRenderer:
    asset_type = "entry_map"
    version = "v1"

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Final-Third and Box Entries")
        entries = [
            event
            for event in context.events
            if has_start_end(event) and (crosses_final_third(event) or enters_box(event))
        ]
        for event in entries:
            color = "#16a34a" if enters_box(event) else "#2563eb"
            ax.annotate(
                "",
                xy=(event.end_x, event.end_y),
                xytext=(event.x, event.y),
                arrowprops={"arrowstyle": "->", "color": color, "lw": 1.5, "alpha": 0.75},
            )
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in entries],
            metadata={
                "entries": len(entries),
                "final_third_entries": sum(1 for event in entries if crosses_final_third(event)),
                "box_entries": sum(1 for event in entries if enters_box(event)),
            },
        )
