from pathlib import Path

import pytest

from tactical_analyst.visualization.base import stable_asset_path
from tactical_analyst.visualization.pitch import validate_pitch_coordinates
from tactical_analyst.visualization.registry import render_all_visualizations
from tests.fixtures.analytics_sample import sample_context

pytest.importorskip("matplotlib")

OUTPUT_DIR = Path("tests/fixtures/visualization_outputs")


def test_stable_asset_path_uses_match_id_asset_type_and_version() -> None:
    path = stable_asset_path(Path("out"), "statsbomb:123", "shot_map", "v1")

    assert path == Path("out/statsbomb_123_shot_map_v1.png")


def test_validate_pitch_coordinates() -> None:
    assert validate_pitch_coordinates(0, 0) is True
    assert validate_pitch_coordinates(105, 68) is True
    assert validate_pitch_coordinates(106, 68) is False
    assert validate_pitch_coordinates(None, 20) is False


def test_render_all_visualizations_creates_report_assets() -> None:
    assets = _render_or_skip()

    assert len(assets) == 8
    assert {asset.asset_type for asset in assets} == {
        "shot_map",
        "xg_timeline",
        "passing_network",
        "progressive_actions",
        "defensive_actions",
        "entry_map",
        "attacking_heatmap",
        "average_action_positions",
    }
    for asset in assets:
        path = Path(asset.uri)
        assert path.exists()
        assert path.suffix == ".png"
        assert asset.format == "png"
        assert asset.version == "v1"


def test_visualization_metadata_counts_match_synthetic_events() -> None:
    assets = {asset.asset_type: asset for asset in _render_or_skip()}

    assert assets["shot_map"].metadata["shot_count"] == 3
    assert assets["xg_timeline"].metadata["shot_count"] == 3
    assert assets["progressive_actions"].metadata["progressive_actions"] == 3
    assert assets["defensive_actions"].metadata["defensive_actions"] == 2
    assert assets["entry_map"].metadata["box_entries"] == 2
    assert assets["attacking_heatmap"].metadata["event_count"] == 10
    assert assets["average_action_positions"].metadata["player_count"] == 4


def _render_or_skip():
    try:
        return render_all_visualizations(sample_context(), OUTPUT_DIR)
    except PermissionError as exc:
        pytest.skip(f"visualization output directory is not writable: {exc}")
