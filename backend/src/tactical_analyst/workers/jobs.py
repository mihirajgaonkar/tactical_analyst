from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from uuid import uuid4


@dataclass(frozen=True)
class QueuedJob:
    job_id: str
    status: str


class JobClient(Protocol):
    def enqueue(self, task_name: str, *args, **kwargs) -> QueuedJob:
        """Queue a task and return its job ID."""

    def status(self, job_id: str) -> dict:
        """Return queue status for a job."""


class LocalJobClient:
    """Test/development job client that records queued work without executing it."""

    def __init__(self) -> None:
        self.jobs: dict[str, dict] = {}

    def enqueue(self, task_name: str, *args, **kwargs) -> QueuedJob:
        job_id = str(uuid4())
        idempotency_key = kwargs.pop("idempotency_key", None)
        if idempotency_key:
            for existing in self.jobs.values():
                if existing.get("idempotency_key") == idempotency_key:
                    return QueuedJob(job_id=existing["job_id"], status=existing["status"])
        self.jobs[job_id] = {
            "job_id": job_id,
            "task_name": task_name,
            "status": "queued",
            "args": args,
            "kwargs": kwargs,
            "idempotency_key": idempotency_key,
        }
        return QueuedJob(job_id=job_id, status="queued")

    def status(self, job_id: str) -> dict:
        return self.jobs.get(job_id, {"job_id": job_id, "status": "unknown"})


class CeleryJobClient:
    """Celery-backed job client."""

    def __init__(self, celery_app) -> None:
        self.celery_app = celery_app

    def enqueue(self, task_name: str, *args, **kwargs) -> QueuedJob:
        # Idempotency metadata belongs to the queue client, not the task signature.
        # Passing it as a task kwarg makes Celery reject tasks that only accept match_id.
        kwargs.pop("idempotency_key", None)
        result = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
        return QueuedJob(job_id=result.id, status="queued")

    def status(self, job_id: str) -> dict:
        result = self.celery_app.AsyncResult(job_id)
        return {
            "job_id": job_id,
            "status": result.status.lower(),
            "result": _json_safe_result(result.result),
        }


def _json_safe_result(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)
