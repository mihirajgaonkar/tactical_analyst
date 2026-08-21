from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
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
        idempotency_key = kwargs.pop("idempotency_key", None)
        if idempotency_key:
            kwargs["idempotency_key"] = idempotency_key
        result = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
        return QueuedJob(job_id=result.id, status="queued")

    def status(self, job_id: str) -> dict:
        result = self.celery_app.AsyncResult(job_id)
        return {"job_id": job_id, "status": result.status.lower(), "result": result.result}
