from __future__ import annotations

from sqlalchemy.orm import Session

from tactical_analyst.db.models import CalculatedMetricModel
from tactical_analyst.schemas.metric import MetricResult


def persist_metric_results(session: Session, results: list[MetricResult]) -> None:
    """Idempotently persist deterministic metric results."""

    for result in results:
        db_metric = session.get(CalculatedMetricModel, result.id)
        values = {
            "match_id": result.match_id,
            "entity_type": result.entity_type,
            "entity_id": result.entity_id,
            "metric_name": result.metric_name,
            "metric_version": result.metric_version,
            "window_start_ms": result.window_start_ms,
            "window_end_ms": result.window_end_ms,
            "value_numeric": result.value_numeric,
            "value_json": result.value_json,
            "sample_size": result.sample_size,
            "source_event_ids": result.source_event_ids,
            "input_hash": result.input_hash,
        }
        if db_metric is None:
            session.add(CalculatedMetricModel(id=result.id, **values))
        else:
            for key, value in values.items():
                setattr(db_metric, key, value)
    session.commit()
