from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tactical_analyst.analytics.base import MatchContext
from tactical_analyst.analytics.helpers import is_completed_action, is_pass
from tactical_analyst.visualization.base import VisualizationAsset, save_figure, stable_asset_path
from tactical_analyst.visualization.pitch import create_pitch


class PassingNetworkRenderer:
    asset_type = "passing_network"
    version = "v1"

    def __init__(self, minimum_edge_count: int = 1) -> None:
        self.minimum_edge_count = minimum_edge_count

    def render(self, context: MatchContext, output_dir: Path) -> VisualizationAsset:
        path = stable_asset_path(output_dir, context.match_id, self.asset_type, self.version)
        fig, ax = create_pitch("Passing Network")
        passes = [
            event
            for event in context.events
            if (
                is_pass(event)
                and is_completed_action(event)
                and event.player_id
                and event.receiver_player_id
            )
        ]
        positions = _average_player_locations(passes)
        edges = Counter((event.player_id, event.receiver_player_id) for event in passes)
        for (passer, receiver), weight in edges.items():
            if (
                weight < self.minimum_edge_count
                or passer not in positions
                or receiver not in positions
            ):
                continue
            start = positions[passer]
            end = positions[receiver]
            ax.plot(
                [start[0], end[0]],
                [start[1], end[1]],
                color="#475569",
                linewidth=0.8 + weight * 0.35,
                alpha=0.65,
            )
        for player_id, (x, y) in positions.items():
            ax.scatter(x, y, s=180, c="#0f766e", edgecolors="#111827", zorder=3)
            ax.text(x, y, player_id.rsplit(":", 1)[-1], ha="center", va="center", fontsize=7)
        save_figure(fig, path)
        return VisualizationAsset(
            match_id=context.match_id,
            asset_type=self.asset_type,
            version=self.version,
            uri=path.as_posix(),
            format="png",
            source_event_ids=[event.id for event in passes],
            metadata={"completed_passes": len(passes), "edge_count": len(edges)},
        )


def _average_player_locations(events) -> dict[str, tuple[float, float]]:
    grouped = defaultdict(list)
    for event in events:
        if event.x is not None and event.y is not None:
            grouped[event.player_id].append((event.x, event.y))
    return {
        player_id: (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )
        for player_id, points in grouped.items()
    }
