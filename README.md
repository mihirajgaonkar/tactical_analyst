# AI Soccer Match Tactical Analyst

Phase 1 foundation is scaffolded in `backend/`.

## Environment Notes

This workspace currently has Python at `C:\Python314\python.exe`. The local `uv run python`
probe failed because uv could not access its global cache under
`C:\Users\AjgMi001\AppData\Local\uv\cache`.

## Backend

Phase 1 includes:

- Pydantic settings
- FastAPI health skeleton
- StatsBomb Open Data provider
- canonical match, lineup, and event schemas
- coordinate normalization to a 105m x 68m left-to-right pitch
- local raw JSON object storage
- SQLAlchemy models/session
- Alembic scaffold
- idempotent ingestion service for matches, lineups, and events
- unit tests for settings, coordinates, validation, fixture parsing, and idempotency

Phase 2 includes:

- deterministic metric result schema and analytics context
- calculator registry
- shots and xG metrics
- passing network metrics
- progressive pass/carry metrics
- field tilt, final-third entries, and box entries
- PPDA, high turnovers, and defensive action height
- possession sequence summaries
- deterministic build-up pattern labels
- attacking zone counts
- transparent player influence features
- substitution pre/post windows
- metric persistence helper for `calculated_metrics`
- synthetic unit tests with hand-checked expected values

Phase 3 includes:

- report-ready visualization renderer interface and asset metadata
- deterministic asset naming
- pitch helpers for normalized `105m x 68m` coordinates
- shot map
- xG timeline
- passing network
- progressive pass/carry map
- defensive actions map
- final-third/box entry map
- attacking heatmap
- Average Action Position map
- visualization registry for rendering all MVP assets
- dependency-aware visualization tests for PNG creation and metadata counts

Phase 4 includes:

- provider-neutral LLM factory and Gemini adapter
- structured LLM schemas for tactical claims, interpretations, and final reports
- bundled tactical interpreter and final report prompts
- compact evidence packet builder from deterministic metrics
- deterministic evidence hashing
- claim evidence verification
- numeric verification for invented values
- capability verification for tracking/360-only claims
- repair-aware tactical analysis workflow
- optional LangGraph workflow builder
- mocked LLM workflow tests for happy path, repair path, and retry ceiling

Phase 5 includes:

- FastAPI routes for competitions, seasons, matches, metrics, reports, jobs, ingestion, and analysis
- route registration in the FastAPI app
- response serializers for database models
- read repository helpers
- Celery app and named tasks wired to ingestion, metrics, visualization, and report pipelines
- queue abstraction with Celery and local/mock job clients
- API tests for route validation, queue mocking, metrics, reports, and claim evidence

Phase 6 includes:

- React + TypeScript + Vite frontend
- Match Explorer flow for competition, season, match selection, and analysis submission
- Analysis dashboard sections for overview, territory/progression, pressing/defending, build-up, players, substitutions, and tactical report
- Plotly metric charts and xG timeline
- markdown-rendered tactical report
- evidence drawer for claim-level evidence inspection
- API client with backend calls and demo fallback data
- frontend tests for match selection, analysis submission, report rendering, visualization rendering, and evidence drawer

Phase 7 includes:

- 10-match evaluation manifest
- deterministic evaluation result schema
- claim-grounding evaluator using existing evidence, numeric, and capability verifiers
- retry/backoff helper for structured LLM calls
- cache key helpers for match metadata, metrics, and report reuse
- local TTL cache primitive
- duplicate-report lookup by match, evidence hash, prompt version, provider, and model
- idempotent local job enqueueing
- structured JSON analysis logging helper
- reliability/evaluation unit tests covering release-blocking criteria

Phase 8 includes:

- backend Dockerfile
- frontend Dockerfile and Nginx config
- Docker Compose stack for backend, worker, frontend, PostgreSQL, Redis, and MinIO
- service health checks
- backend readiness endpoint
- GitHub Actions CI for backend, frontend, and Docker image builds
- deployment documentation
- local filesystem object storage as the active MVP storage strategy
- optional S3-compatible storage placeholder for later hosted deployment wiring

Worker pipeline wiring includes:

- StatsBomb ingestion through Celery task `tactical_analyst.ingest_match`
- deterministic metric calculation through `tactical_analyst.calculate_match_metrics`
- local visualization generation through `tactical_analyst.generate_match_visualizations`
- evidence building, LLM report generation, verification, and DB persistence through `tactical_analyst.run_tactical_analysis`

Phase 9 includes:

- canonical tracking-frame schemas
- provider-neutral tracking data interface
- local JSON tracking-file provider
- deterministic true-position metrics for team width, team depth, compactness area, defensive line height, and true average player position
- tracking tests that keep these metrics separate from event-only analytics

When dependencies are available:

```powershell
cd backend
uv sync
uv run pytest
```

After Phase 5, run `uv sync --group dev` once so Celery is installed and `uv.lock`
is refreshed.

Frontend commands:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
npm.cmd test
npm.cmd run build
```

Phase 7 release checks currently enforce:

```text
Unsupported numeric claims = 0
Unknown evidence references = 0
Unavailable-metric claims = 0
```

Deployment:

```powershell
copy .env.example .env
docker compose up --build
```

Docker Desktop must be installed and available on `PATH` before running Compose.

If uv cache permissions remain blocked, run the equivalent commands from your VS Code terminal
or use an activated virtual environment with `pip install -e .[dev]` once dependencies are available.
