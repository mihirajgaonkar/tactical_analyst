from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


class LocalObjectStorage:
    """Filesystem-backed object storage for local development."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def put_json_gz(self, key: str, payload: object) -> tuple[str, str]:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wb") as handle:
            handle.write(encoded)
        return path.as_posix(), digest
