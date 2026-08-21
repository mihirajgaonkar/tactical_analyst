from __future__ import annotations

from celery import Celery

from tactical_analyst.config.settings import get_settings
from tactical_analyst.workers.pipeline import (
    calculate_match_metrics_pipeline,
    generate_match_visualizations_pipeline,
    ingest_match_pipeline,
    run_tactical_analysis_pipeline,
)

settings = get_settings()
celery_app = Celery(
    "tactical_analyst",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="tactical_analyst.ingest_match")
def ingest_match(match_id: str) -> dict:
    """Fetch, normalize, validate, and persist a StatsBomb match."""

    return ingest_match_pipeline(match_id)


@celery_app.task(name="tactical_analyst.calculate_match_metrics")
def calculate_match_metrics(match_id: str) -> dict:
    return calculate_match_metrics_pipeline(match_id)


@celery_app.task(name="tactical_analyst.generate_match_visualizations")
def generate_match_visualizations(match_id: str) -> dict:
    return generate_match_visualizations_pipeline(match_id)


@celery_app.task(name="tactical_analyst.run_tactical_analysis")
def run_tactical_analysis(match_id: str) -> dict:
    return run_tactical_analysis_pipeline(match_id)
