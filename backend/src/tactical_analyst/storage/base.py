from typing import Protocol


class ObjectStorage(Protocol):
    """Object storage protocol for raw provider payloads and generated assets."""

    def put_json_gz(self, key: str, payload: object) -> tuple[str, str]:
        """Persist compressed JSON and return URI plus SHA-256 hash."""
