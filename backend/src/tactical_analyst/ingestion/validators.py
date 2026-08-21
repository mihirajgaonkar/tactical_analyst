from tactical_analyst.schemas.event import MatchEvent


def validate_events(events: list[MatchEvent]) -> None:
    """Validate canonical event ordering and duplicate IDs for one match."""

    seen: set[str] = set()
    previous_index = -1
    for event in events:
        if event.id in seen:
            raise ValueError(f"Duplicate event id: {event.id}")
        seen.add(event.id)
        if event.index < previous_index:
            raise ValueError("Events must be sorted by nondecreasing index")
        previous_index = event.index
