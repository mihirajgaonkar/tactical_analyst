from tactical_analyst.ingestion.normalizer import (
    normalize_statsbomb_events,
    normalize_statsbomb_lineups,
    normalize_statsbomb_match,
)
from tests.fixtures.statsbomb_sample import SAMPLE_EVENTS, SAMPLE_LINEUPS, SAMPLE_MATCH


def test_normalize_statsbomb_match() -> None:
    match = normalize_statsbomb_match(SAMPLE_MATCH)

    assert match.id == "statsbomb:1"
    assert match.home_team.name == "Home FC"
    assert match.away_team.name == "Away FC"
    assert match.home_score == 2
    assert match.away_score == 1


def test_normalize_statsbomb_lineups() -> None:
    lineups = normalize_statsbomb_lineups("statsbomb:1", SAMPLE_LINEUPS)

    assert len(lineups) == 2
    assert lineups[0].starter is True
    assert lineups[0].position == "Right Center Midfield"
    assert lineups[0].shirt_number == 8


def test_normalize_statsbomb_events() -> None:
    events = normalize_statsbomb_events("statsbomb:1", SAMPLE_EVENTS)

    assert len(events) == 2
    assert events[0].event_type == "Pass"
    assert events[0].x == 52.5
    assert events[0].end_x == 63.0
    assert events[1].event_type == "Shot"
    assert events[1].xg == 0.31
    assert events[1].outcome == "Goal"
