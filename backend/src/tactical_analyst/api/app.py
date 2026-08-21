from fastapi import FastAPI

from tactical_analyst.api.routes.competitions import router as competitions_router
from tactical_analyst.api.routes.health import router as health_router
from tactical_analyst.api.routes.jobs import router as jobs_router
from tactical_analyst.api.routes.matches import router as matches_router
from tactical_analyst.api.routes.metrics import router as metrics_router
from tactical_analyst.api.routes.reports import router as reports_router


def create_app() -> FastAPI:
    app = FastAPI(title="Tactical Analyst API", version="0.1.0")
    app.include_router(health_router)
    app.include_router(competitions_router)
    app.include_router(matches_router)
    app.include_router(metrics_router)
    app.include_router(jobs_router)
    app.include_router(reports_router)
    return app


app = create_app()
