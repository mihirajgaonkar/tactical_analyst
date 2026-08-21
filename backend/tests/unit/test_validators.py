import pytest

from tactical_analyst.ingestion.normalizer import normalize_statsbomb_events
from tactical_analyst.ingestion.validators import validate_events
from tests.fixtures.statsbomb_sample import SAMPLE_EVENTS


def test_validate_events_accepts_sorted_unique_events() -> None:
    events = normalize_statsbomb_events("statsbomb:1", SAMPLE_EVENTS)
    validate_events(events)


def test_validate_events_rejects_duplicates() -> None:
    events = normalize_statsbomb_events("statsbomb:1", [SAMPLE_EVENTS[0], SAMPLE_EVENTS[0]])

    with pytest.raises(ValueError, match="Duplicate event id"):
        validate_events(events)
