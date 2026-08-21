from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    backoff_seconds: float = 0.5
    retry_exceptions: tuple[type[Exception], ...] = (Exception,)


def retry_call[T](operation: Callable[[], T], config: RetryConfig) -> T:
    """Run an operation with simple linear backoff."""

    attempts = 0
    while True:
        attempts += 1
        try:
            return operation()
        except config.retry_exceptions:
            if attempts >= config.max_attempts:
                raise
            sleep(config.backoff_seconds * attempts)
