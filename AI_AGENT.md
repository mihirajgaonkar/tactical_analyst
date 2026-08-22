# AI Agent Handoff: tactical_analyst

This file is context for Codex or another AI coding agent when continuing the project
on a new machine.

## Project Summary

Repository: `tactical_analyst`

Goal: build an AI Soccer Match Tactical Analyst that:

- ingests StatsBomb Open Data,
- normalizes match, lineup, and event data,
- computes deterministic tactical metrics in Python,
- generates report-ready visualizations,
- builds compact evidence packets,
- sends only computed evidence to Gemini,
- verifies LLM claims against evidence,
- renders the result in a React frontend.

Core rule: the LLM must not invent or calculate match statistics. All quantitative
values must come from deterministic Python services before being passed to the LLM.

## Current Implementation Status

Phases 1 through 9 from `plan.md` have been implemented.

### Backend

Implemented:

- FastAPI app and route registration.
- Pydantic settings.
- StatsBomb Open Data provider.
- Canonical match, lineup, and event schemas.
- Coordinate normalization to a 105m x 68m pitch.
- Local filesystem object storage.
- SQLAlchemy models and Alembic scaffold.
- Match ingestion service.
- Deterministic analytics registry and metric calculators.
- Metric persistence.
- Static tactical visualization renderers.
- Gemini provider abstraction through LangChain.
- LLM service with structured Pydantic outputs.
- Evidence packet builder and deterministic evidence hashing.
- Claim, numeric, and capability verifiers.
- Repair-aware tactical workflow.
- API routes for competitions, seasons, matches, metrics, reports, jobs, ingestion,
  and analysis.
- Celery app and named task functions.
- Worker pipeline wiring for ingestion, metrics, visualization generation, and
  tactical report persistence.
- Retry/backoff, cache helpers, structured logging helper, evaluation scaffolding.
- Optional Phase 9 tracking schemas/provider/analytics kept separate from event data.

Important backend files:

- `backend/src/tactical_analyst/workers/tasks.py`
- `backend/src/tactical_analyst/workers/pipeline.py`
- `backend/src/tactical_analyst/db/repositories/context.py`
- `backend/src/tactical_analyst/db/repositories/write.py`
- `backend/src/tactical_analyst/analytics/tracking.py`
- `backend/src/tactical_analyst/schemas/tracking.py`
- `backend/src/tactical_analyst/providers/tracking/base.py`
- `backend/src/tactical_analyst/providers/tracking/local_file.py`

### Frontend

Implemented:

- React + TypeScript + Vite app.
- Match Explorer.
- Tactical dashboard sections.
- Plotly metric charts and xG timeline.
- Markdown tactical report panel.
- Evidence drawer.
- Demo fallback data so the UI can be tested before real backend data exists.

Important frontend files:

- `frontend/src/App.tsx`
- `frontend/src/pages/MatchExplorer.tsx`
- `frontend/src/pages/TacticalReportPanel.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/demoData.ts`

### Deployment

Implemented:

- Backend Dockerfile.
- Frontend Dockerfile and Nginx config.
- Docker Compose stack.
- GitHub Actions CI.
- Deployment docs.
- Backend `/health` and `/ready` endpoints.

Docker services:

- `postgres`
- `redis`
- `minio`
- `backend`
- `worker`
- `frontend`

Current storage decision: use local filesystem object storage for MVP. S3-compatible
storage remains optional later.

## Current Test Status

On the original Windows work laptop, running from `backend`:

```powershell
cd C:\GITHUB\tactical_analyst\backend
uv run pytest
```

Result reported by user:

```text
44 tests passed
```

The assistant also previously verified with the backend virtualenv:

```text
ruff: all checks passed
pytest: 42 passed, 2 skipped
```

The difference is expected because later tests were added and the user confirmed
all 44 passed through `uv`.

Do not run backend tests from the repository root with:

```powershell
uv run pytest
```

That causes import/dependency errors because the backend is its own uv project.
Use `cd backend` first.

## Known Environment Notes

Original work laptop:

- Python executable found by assistant: `C:\Python314\python.exe`
- Python version: `3.14.7`
- uv executable: `C:\Users\AjgMi001\AppData\Local\Programs\Python\Python313\Scripts\uv.exe`
- uv version: `0.12.3`
- Assistant shell could not run `uv run python` due uv cache permissions:

```text
C:\Users\AjgMi001\AppData\Local\uv\cache\sdists-v9\.git Access is denied
```

The user's VS Code terminal could run `uv sync --group dev` and `uv run pytest`
successfully from `backend`.

Docker Desktop on the work laptop required elevated permissions and the Docker
Linux engine failed to start. That is why the user is switching to a personal laptop.

## Personal Laptop Setup

Install:

1. Git
2. Docker Desktop for Windows with WSL 2 support
3. Python 3.12+ or 3.13
4. uv
5. Node.js LTS
6. VS Code
7. A Gemini API key

Clone:

```powershell
cd C:\GITHUB
git clone https://github.com/mihirajgaonkar/tactical_analyst.git
cd tactical_analyst
copy .env.example .env
```

Edit `.env` and add:

```dotenv
GOOGLE_API_KEY=your_key_here
```

Do not commit `.env`. It is ignored by git.

## Backend Setup And Tests

```powershell
cd C:\GITHUB\tactical_analyst\backend
uv sync --group dev
uv run pytest
uv run ruff check . --no-cache
```

Expected: all backend tests pass.

## Frontend Setup And Tests

```powershell
cd C:\GITHUB\tactical_analyst\frontend
npm.cmd install
npm.cmd test
npm.cmd run build
```

Known frontend note: build may warn about a large Plotly bundle. That is expected
for now and does not mean the build failed.

Run frontend dev server:

```powershell
cd C:\GITHUB\tactical_analyst\frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

If port `5173` is busy, Vite may choose `5174`. Use the URL Vite prints.

## Full Docker App

Start Docker Desktop first and wait until Docker is running.

Check:

```powershell
docker info
docker compose version
```

Run full stack:

```powershell
cd C:\GITHUB\tactical_analyst
docker compose up --build
```

Open:

```text
Frontend: http://localhost:5173
Backend docs: http://localhost:8000/docs
Health: http://localhost:8000/health
Readiness: http://localhost:8000/ready
```

## Current Caveats

- The frontend can show demo fallback data before the backend database is populated.
- Real tactical report generation requires `GOOGLE_API_KEY`.
- Full asynchronous job flow requires Docker/Redis/PostgreSQL or equivalent services.
- Docker was not verified on the work laptop because the Docker Desktop engine was
  blocked by work-laptop permissions.
- S3 is not required for the MVP. Local filesystem object storage is the intended
  active setup.
- Phase 9 tracking support is scaffolded and tested with canonical local tracking
  frames, but no real SkillCorner provider integration has been added yet.
- The evaluation manifest currently contains placeholder evaluation match slots and
  should be replaced later with real curated StatsBomb matches.

## Useful Commands

Backend:

```powershell
cd C:\GITHUB\tactical_analyst\backend
uv sync --group dev
uv run pytest
uv run ruff check . --no-cache
```

Frontend:

```powershell
cd C:\GITHUB\tactical_analyst\frontend
npm.cmd install
npm.cmd test
npm.cmd run build
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Docker:

```powershell
cd C:\GITHUB\tactical_analyst
docker info
docker compose up --build
```

Git:

```powershell
git status
git pull
git push
```

## Recommended Next Work

When continuing:

1. Verify Docker Compose on the personal laptop.
2. Confirm backend and frontend tests pass there.
3. Run the full stack.
4. Exercise ingestion and analysis through the API docs.
5. Seed or ingest real StatsBomb matches so the frontend can use live data instead
   of demo fallback data.
6. If needed, improve end-to-end UX around job polling and report refresh.

