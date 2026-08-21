STATSBOMB_LENGTH = 120.0
STATSBOMB_WIDTH = 80.0
PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0


def normalize_statsbomb_location(
    location: list[float] | tuple[float, ...] | None,
) -> tuple[float, float] | tuple[None, None]:
    """Convert StatsBomb [x, y] coordinates to 105m x 68m pitch coordinates."""

    if not location:
        return None, None
    if len(location) < 2:
        raise ValueError("StatsBomb location must include x and y")
    x = float(location[0]) / STATSBOMB_LENGTH * PITCH_LENGTH_M
    y = float(location[1]) / STATSBOMB_WIDTH * PITCH_WIDTH_M
    return round(x, 4), round(y, 4)


def normalize_statsbomb_end_location(event: dict) -> tuple[float, float] | tuple[None, None]:
    """Extract and normalize the best-known end location for a StatsBomb event."""

    event_type = event.get("type", {}).get("name")
    details = event.get((event_type or "").lower().replace(" ", "_"), {})
    return normalize_statsbomb_location(details.get("end_location"))
