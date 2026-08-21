from tactical_analyst.config.settings import Settings, get_settings
from tactical_analyst.workers.jobs import CeleryJobClient, JobClient


def get_app_settings() -> Settings:
    return get_settings()


def get_job_client() -> JobClient:
    from tactical_analyst.workers.tasks import celery_app

    return CeleryJobClient(celery_app)
