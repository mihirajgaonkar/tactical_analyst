from typing import Annotated

from fastapi import APIRouter, Depends

from tactical_analyst.api.dependencies import get_job_client
from tactical_analyst.workers.jobs import JobClient

router = APIRouter(prefix="/jobs", tags=["jobs"])
JobDependency = Annotated[JobClient, Depends(get_job_client)]


@router.get("/{job_id}")
def get_job_status(job_id: str, job_client: JobDependency) -> dict:
    return job_client.status(job_id)
