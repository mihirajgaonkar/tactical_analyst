def route_after_verification(state: dict) -> str:
    """Route verified claims to final report, otherwise repair or stop."""

    if state.get("verification_errors"):
        if int(state.get("verification_attempts", 0)) >= 1:
            return "invalid"
        return "repair"
    return "valid"
