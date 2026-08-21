from __future__ import annotations


class S3ObjectStorage:
    """Placeholder S3-compatible storage adapter for hosted deployment wiring."""

    def __init__(
        self,
        *,
        endpoint_url: str | None,
        bucket: str,
        access_key_id: str | None,
        secret_access_key: str | None,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def put_json_gz(self, key: str, payload: object) -> tuple[str, str]:
        raise NotImplementedError("S3 object storage upload will be wired in a hosted storage pass")
