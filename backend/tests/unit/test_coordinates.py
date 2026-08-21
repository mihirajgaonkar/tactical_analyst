import pytest

from tactical_analyst.ingestion.coordinates import normalize_statsbomb_location


def test_normalize_statsbomb_location_scales_to_metric_pitch() -> None:
    assert normalize_statsbomb_location([120, 80]) == (105.0, 68.0)
    assert normalize_statsbomb_location([60, 40]) == (52.5, 34.0)


def test_normalize_statsbomb_location_rejects_partial_location() -> None:
    with pytest.raises(ValueError):
        normalize_statsbomb_location([10])
