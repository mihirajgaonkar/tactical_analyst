from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from statistics import median

from tactical_analyst.schemas.event import MatchEvent

PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0
FINAL_THIRD_X = PITCH_LENGTH_M * 2 / 3
PENALTY_AREA_X = 88.5
PENALTY_AREA_Y_MIN = 13.84
PENALTY_AREA_Y_MAX = 54.16
HIGH_TURNOVER_X = 70.0
BUILDUP_ZONE_X_MAX = 63.0
GOAL_CENTER = (PITCH_LENGTH_M, PITCH_WIDTH_M / 2)

COMPLETED_OUTCOMES = {None, "Complete", "Won"}
SHOT_ON_TARGET_OUTCOMES = {"Goal", "Saved", "Saved to Post"}
DEFENSIVE_ACTION_TYPES = {
    "Pressure",
    "Tackle",
    "Interception",
    "Foul Committed",
    "Duel",
    "Ball Recovery",
    "Block",
}
REGAIN_TYPES = {"Ball Recovery", "Interception"}


def teams_from_events(events: Iterable[MatchEvent]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(event.team_id for event in events))


def by_team(events: Iterable[MatchEvent]) -> dict[str, list[MatchEvent]]:
    grouped: dict[str, list[MatchEvent]] = defaultdict(list)
    for event in events:
        grouped[event.team_id].append(event)
    return dict(grouped)


def is_completed_action(event: MatchEvent) -> bool:
    return event.outcome in COMPLETED_OUTCOMES


def is_pass(event: MatchEvent) -> bool:
    return event.event_type == "Pass"


def is_carry(event: MatchEvent) -> bool:
    return event.event_type == "Carry"


def has_start_end(event: MatchEvent) -> bool:
    return None not in (event.x, event.y, event.end_x, event.end_y)


def distance_to_goal(x: float, y: float) -> float:
    return math.dist((x, y), GOAL_CENTER)


def is_progressive(event: MatchEvent) -> bool:
    """Progressive action v1: zone-specific reduction in distance to opponent goal."""

    if not has_start_end(event) or event.end_x is None or event.x is None:
        return False
    if event.end_x <= event.x:
        return False
    start_distance = distance_to_goal(event.x, event.y or 0)
    end_distance = distance_to_goal(event.end_x, event.end_y or 0)
    gained = start_distance - end_distance
    starts_own_half = event.x < PITCH_LENGTH_M / 2
    ends_own_half = event.end_x < PITCH_LENGTH_M / 2
    if starts_own_half and ends_own_half:
        return gained >= 30
    if starts_own_half and not ends_own_half:
        return gained >= 15
    return gained >= 10


def crosses_final_third(event: MatchEvent) -> bool:
    return (
        has_start_end(event)
        and event.x is not None
        and event.end_x is not None
        and event.x < FINAL_THIRD_X <= event.end_x
    )


def is_inside_box(x: float | None, y: float | None) -> bool:
    return (
        x is not None
        and y is not None
        and x >= PENALTY_AREA_X
        and PENALTY_AREA_Y_MIN <= y <= PENALTY_AREA_Y_MAX
    )


def enters_box(event: MatchEvent) -> bool:
    return (
        has_start_end(event)
        and not is_inside_box(event.x, event.y)
        and is_inside_box(event.end_x, event.end_y)
    )


def lane_for_y(y: float | None) -> str:
    if y is None:
        return "unknown"
    if y < PITCH_WIDTH_M / 3:
        return "left"
    if y < PITCH_WIDTH_M * 2 / 3:
        return "central"
    return "right"


def five_zone_for_y(y: float | None) -> str:
    if y is None:
        return "unknown"
    width = PITCH_WIDTH_M / 5
    zones = ["left_lane", "left_half_space", "central_lane", "right_half_space", "right_lane"]
    return zones[min(int(y // width), 4)]


def median_x(events: list[MatchEvent]) -> float | None:
    values = [event.x for event in events if event.x is not None]
    return float(median(values)) if values else None


def event_ids(events: Iterable[MatchEvent]) -> list[str]:
    return [event.id for event in events]
