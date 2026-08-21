from __future__ import annotations

import hashlib
import json
from typing import Any


def competition_matches_key(competition_id: str) -> str:
    return f"competition:{competition_id}:matches"


def match_metadata_key(match_id: str) -> str:
    return f"match:{match_id}:metadata"


def match_metrics_key(match_id: str, analytics_version: str) -> str:
    return f"match:{match_id}:metrics:{analytics_version}"


def report_cache_key(
    match_id: str,
    evidence_hash: str,
    prompt_version: str,
    model: str,
) -> str:
    return f"report:{match_id}:{evidence_hash}:{prompt_version}:{model}"


def stable_payload_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()
