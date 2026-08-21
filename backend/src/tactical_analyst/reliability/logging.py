from __future__ import annotations

import json
import logging
from typing import Any


def log_analysis_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit one structured JSON log line for analysis/job observability."""

    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, sort_keys=True, default=str))
