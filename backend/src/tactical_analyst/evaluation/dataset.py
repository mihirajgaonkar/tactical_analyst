from __future__ import annotations

import json
from importlib.resources import files


def load_evaluation_matches() -> list[dict]:
    """Load the manually reviewed evaluation match manifest."""

    text = files("tactical_analyst.evaluation").joinpath("matches.json").read_text()
    return json.loads(text)
