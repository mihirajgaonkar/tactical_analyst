# AI Soccer Match Tactical Analyst — Implementation Plan

## 1. Project Goal

Build a production-ready AI Soccer Match Tactical Analyst that allows a user to select a completed soccer match and generates an evidence-based tactical report explaining:

- how both teams played,
- how they progressed the ball,
- how they pressed and defended,
- where chances came from,
- which players influenced the match,
- how substitutions changed the match,
- and why the final result occurred.

The system must follow one core rule:

> All quantitative statistics are computed deterministically in Python before any data is passed to an LLM.

The LLM may interpret evidence, organize findings, and write the tactical narrative, but it must never invent or calculate match statistics on its own.

---

## 2. MVP Scope

### Data source

Use **StatsBomb Open Data** for the initial portfolio MVP.

Optional later enhancement:

- SkillCorner Open Data for true tracking / off-ball spatial analysis.

### LLM provider

Use **Google Gemini** as the initial LLM provider.

The LLM layer must be implemented behind a provider abstraction so the project can later switch to:

- OpenAI
- Anthropic
- Groq
- OpenRouter
- Azure OpenAI
- local models
- other LangChain-supported chat models

without changing the LangGraph workflow or business logic.

### Initial supported analyses

The MVP should calculate and explain:

1. score and match context
2. formations and lineups
3. possession
4. shots
5. xG
6. xG per shot
7. shot locations
8. passing network
9. progressive passes
10. progressive carries
11. field tilt
12. PPDA
13. final-third entries
14. box entries
15. high turnovers
16. defensive action height
17. possession sequences
18. build-up patterns
19. attacking zones
20. player influence
21. substitutions and pre/post impact windows

Do not implement true defensive line height or true average physical player position using ordinary event data. Event-data versions must be labeled accurately, e.g.:

- Average Action Position
- Defensive Action Height

True line height / compactness / physical player location may be added later with tracking or StatsBomb 360 data.

---

# 3. Primary Technical Principles

## 3.1 Deterministic analytics first

All values shown in the application or report must come from deterministic services.

Examples:

- PPDA
- field tilt
- xG totals
- progressive passes
- progressive carries
- box entries
- final-third entries
- high turnovers
- passing network counts
- shot counts
- possession sequences
- substitution windows

The LLM must not perform arithmetic.

---

## 3.2 Evidence-linked generation

Every important tactical claim must reference one or more evidence IDs.

Example:

```json
{
  "claim": "Team A applied the more aggressive press.",
  "evidence_ids": [
    "METRIC_PPDA_TEAM_A",
    "METRIC_HIGH_TURNOVERS_TEAM_A",
    "METRIC_PRESSURES_FINAL_THIRD_TEAM_A"
  ]
}
```

---

## 3.3 Provider abstraction

Both soccer-data providers and LLM providers must be replaceable.

The internal analytics engine must only work with canonical models, never provider-specific raw schemas.

---

## 3.4 Reproducibility

Every calculated metric must store:

- metric name
- metric version
- input data version/hash
- match ID
- entity ID where relevant
- time window where relevant
- calculated value
- sample size
- source event IDs

---

# 4. Recommended Stack

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Celery
- LangChain
- LangGraph
- Google Gemini via LangChain Google Generative AI integration
- Polars
- NumPy
- NetworkX
- mplsoccer
- matplotlib
- Plotly

## Frontend

- React
- TypeScript
- Vite
- TanStack Query
- Plotly.js / react-plotly.js
- React Markdown

## Infrastructure

- Docker
- Docker Compose
- PostgreSQL
- Redis
- MinIO for local object storage
- S3/R2-compatible object storage for hosted deployment
- GitHub Actions

## Testing

- pytest
- pytest-asyncio
- httpx AsyncClient
- Testcontainers where useful
- Playwright for frontend E2E

## Observability

- Python structured logging
- OpenTelemetry-ready architecture
- Sentry optional
- LangSmith optional

---

# 5. High-Level Architecture

```text
React Frontend
      |
      v
FastAPI Backend
      |
      +----------------------+
      |                      |
      v                      v
PostgreSQL                Redis
      |                      |
      |                      v
      |                 Celery Worker
      |                      |
      |                      v
      |                 LangGraph Workflow
      |                      |
      |      +---------------+-------------------+
      |      |               |                   |
      |      v               v                   v
      |  Data Ingestion  Analytics Engine   Visualization Engine
      |      |               |                   |
      |      v               v                   v
      |  StatsBomb       Evidence Builder   Object Storage
      |                      |
      |                      v
      |                 LLM Interpretation
      |                      |
      |                      v
      |                 Fact Verification
      |                      |
      +<---------------------+
```

---

# 6. Target Repository Structure

```text
soccer-tactical-analyst/
|
|-- backend/
|   |-- src/
|   |   |-- tactical_analyst/
|   |   |   |
|   |   |   |-- api/
|   |   |   |   |-- app.py
|   |   |   |   |-- dependencies.py
|   |   |   |   `-- routes/
|   |   |   |       |-- health.py
|   |   |   |       |-- competitions.py
|   |   |   |       |-- matches.py
|   |   |   |       |-- metrics.py
|   |   |   |       |-- reports.py
|   |   |   |       `-- jobs.py
|   |   |   |
|   |   |   |-- config/
|   |   |   |   `-- settings.py
|   |   |   |
|   |   |   |-- providers/
|   |   |   |   |-- soccer/
|   |   |   |   |   |-- base.py
|   |   |   |   |   |-- statsbomb_open.py
|   |   |   |   |   `-- capabilities.py
|   |   |   |   |
|   |   |   |   `-- llm/
|   |   |   |       |-- base.py
|   |   |   |       |-- factory.py
|   |   |   |       `-- gemini.py
|   |   |   |
|   |   |   |-- schemas/
|   |   |   |   |-- match.py
|   |   |   |   |-- event.py
|   |   |   |   |-- lineup.py
|   |   |   |   |-- metric.py
|   |   |   |   |-- evidence.py
|   |   |   |   `-- report.py
|   |   |   |
|   |   |   |-- ingestion/
|   |   |   |   |-- service.py
|   |   |   |   |-- normalizer.py
|   |   |   |   |-- coordinates.py
|   |   |   |   `-- validators.py
|   |   |   |
|   |   |   |-- analytics/
|   |   |   |   |-- registry.py
|   |   |   |   |-- base.py
|   |   |   |   |-- shots.py
|   |   |   |   |-- passing.py
|   |   |   |   |-- progression.py
|   |   |   |   |-- possession.py
|   |   |   |   |-- pressing.py
|   |   |   |   |-- territory.py
|   |   |   |   |-- transitions.py
|   |   |   |   |-- spatial.py
|   |   |   |   |-- players.py
|   |   |   |   `-- substitutions.py
|   |   |   |
|   |   |   |-- evidence/
|   |   |   |   |-- builder.py
|   |   |   |   |-- registry.py
|   |   |   |   `-- serializers.py
|   |   |   |
|   |   |   |-- graph/
|   |   |   |   |-- state.py
|   |   |   |   |-- nodes.py
|   |   |   |   |-- workflow.py
|   |   |   |   `-- routing.py
|   |   |   |
|   |   |   |-- llm/
|   |   |   |   |-- schemas.py
|   |   |   |   |-- prompts/
|   |   |   |   |   |-- tactical_interpreter.md
|   |   |   |   |   `-- final_report.md
|   |   |   |   `-- service.py
|   |   |   |
|   |   |   |-- verification/
|   |   |   |   |-- claim_verifier.py
|   |   |   |   |-- numeric_verifier.py
|   |   |   |   `-- coverage_verifier.py
|   |   |   |
|   |   |   |-- visualization/
|   |   |   |   |-- base.py
|   |   |   |   |-- pitch.py
|   |   |   |   |-- passing_network.py
|   |   |   |   |-- shot_map.py
|   |   |   |   |-- xg_timeline.py
|   |   |   |   |-- progressive_actions.py
|   |   |   |   |-- defensive_actions.py
|   |   |   |   `-- heatmap.py
|   |   |   |
|   |   |   |-- db/
|   |   |   |   |-- base.py
|   |   |   |   |-- models.py
|   |   |   |   |-- session.py
|   |   |   |   `-- repositories/
|   |   |   |
|   |   |   |-- storage/
|   |   |   |   |-- base.py
|   |   |   |   |-- local.py
|   |   |   |   `-- s3.py
|   |   |   |
|   |   |   `-- workers/
|   |   |       `-- tasks.py
|   |   |
|   |   `-- alembic/
|   |
|   |-- tests/
|   |   |-- unit/
|   |   |-- integration/
|   |   |-- fixtures/
|   |   `-- golden_matches/
|   |
|   |-- pyproject.toml
|   `-- Dockerfile
|
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- charts/
|   |   |-- pages/
|   |   |-- types/
|   |   `-- App.tsx
|   |-- package.json
|   `-- Dockerfile
|
|-- docker-compose.yml
|-- .env.example
|-- README.md
`-- plan.md
```

---

# 7. Environment Variables

Create `.env.example` with at least:

```dotenv
APP_ENV=development
LOG_LEVEL=INFO

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/tactical_analyst
REDIS_URL=redis://redis:6379/0

OBJECT_STORAGE_PROVIDER=local
OBJECT_STORAGE_PATH=./data/object_store

LLM_PROVIDER=gemini
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-3.6-flash

LLM_TEMPERATURE=0.1
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=60

SOCCER_DATA_PROVIDER=statsbomb_open

REPORT_PROMPT_VERSION=v1

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

Do not hard-code model names in graph nodes.

All model configuration must come from settings.

---

# 8. LLM Provider Abstraction

Implement a provider-neutral interface.

Suggested interface:

```python
from typing import Protocol
from langchain_core.language_models.chat_models import BaseChatModel


class LLMProvider(Protocol):
    def get_chat_model(self) -> BaseChatModel:
        ...
```

Factory:

```python
def get_llm(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "gemini":
        return build_gemini_model(settings)

    if settings.llm_provider == "openai":
        return build_openai_model(settings)

    if settings.llm_provider == "anthropic":
        return build_anthropic_model(settings)

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
```

Initial Gemini implementation should use the official LangChain Gemini integration.

All LLM calls must use structured output with Pydantic models wherever possible.

---

# 9. Canonical Soccer Provider Interface

Implement:

```python
class SoccerDataProvider(Protocol):
    async def list_competitions(self): ...
    async def list_matches(self, competition_id: str, season_id: str): ...
    async def get_match(self, match_id: str): ...
    async def get_lineups(self, match_id: str): ...
    async def get_events(self, match_id: str): ...
    async def get_frames(self, match_id: str): ...
    def capabilities(self) -> ProviderCapabilities: ...
```

StatsBomb Open Data is the first implementation.

The rest of the application must consume only normalized canonical models.

---

# 10. Provider Capability Registry

Create a capability model such as:

```python
class ProviderCapabilities(BaseModel):
    event_coordinates: bool
    pass_events: bool
    carry_events: bool
    pressure_events: bool
    xg: bool
    possession_ids: bool
    lineups: bool
    formations: bool
    substitutions: bool
    freeze_frames_360: bool
    tracking: bool
```

The analytics engine must not calculate unsupported metrics.

Example:

```python
if not capabilities.pressure_events:
    skip("pressing_pressure_event_metrics")
```

The final report must never mention unavailable metrics as though they were observed.

---

# 11. Canonical Event Schema

Normalized events should include at least:

```python
class MatchEvent(BaseModel):
    id: str
    match_id: str
    index: int
    period: int
    timestamp_ms: int

    team_id: str
    player_id: str | None
    receiver_player_id: str | None

    event_type: str
    event_subtype: str | None
    outcome: str | None

    possession_id: str | None
    play_pattern: str | None

    x: float | None
    y: float | None
    end_x: float | None
    end_y: float | None

    xg: float | None
    under_pressure: bool | None

    related_event_ids: list[str] = []
    provider_payload: dict
```

Use normalized pitch coordinates:

```text
Pitch = 105m x 68m
Attacking direction = left to right
```

Store provider coordinates separately in `provider_payload` or explicit raw-coordinate fields.

---

# 12. Database Design

Create SQLAlchemy models and Alembic migrations for:

## competitions

- id
- provider
- provider_competition_id
- name
- country
- gender
- created_at

## seasons

- id
- competition_id
- provider_season_id
- name
- start_date
- end_date

## teams

- id
- name
- country
- provider_ids JSONB

## players

- id
- name
- date_of_birth nullable
- primary_position nullable
- provider_ids JSONB

## matches

- id
- competition_id
- season_id
- provider_match_id
- home_team_id
- away_team_id
- kickoff_at
- home_score
- away_score
- status
- raw_payload_uri
- raw_payload_hash
- ingestion_version
- created_at

## lineups

- id
- match_id
- team_id
- player_id
- starter
- position
- formation_slot nullable
- shirt_number nullable
- start_second
- end_second

## match_events

- id
- match_id
- provider_event_id
- event_index
- period
- timestamp_ms
- team_id
- player_id nullable
- receiver_player_id nullable
- event_type
- event_subtype nullable
- outcome nullable
- possession_id nullable
- play_pattern nullable
- x nullable
- y nullable
- end_x nullable
- end_y nullable
- xg nullable
- under_pressure nullable
- related_event_ids JSONB
- provider_payload JSONB

Important indexes:

```text
(match_id, event_index)
(match_id, timestamp_ms)
(match_id, team_id, event_type)
(match_id, player_id)
(match_id, possession_id)
```

## player_match_stats

- match_id
- player_id
- minutes
- passes
- completed_passes
- progressive_passes
- carries
- progressive_carries
- shots
- xg
- pressures
- tackles
- interceptions
- recoveries
- extra JSONB

## team_match_stats

- match_id
- team_id
- possession
- shots
- xg
- passes
- progressive_passes
- progressive_carries
- ppda
- field_tilt
- final_third_entries
- box_entries
- high_turnovers
- extra JSONB

## calculated_metrics

- id
- match_id
- entity_type
- entity_id
- metric_name
- metric_version
- window_start_ms nullable
- window_end_ms nullable
- value_numeric nullable
- value_json nullable
- sample_size nullable
- source_event_ids JSONB
- input_hash
- created_at

## tactical_reports

- id
- match_id
- report_version
- evidence_hash
- llm_provider
- llm_model
- prompt_version
- report_json JSONB
- report_markdown TEXT
- verification_status
- input_tokens nullable
- output_tokens nullable
- llm_cost nullable
- created_at

## report_claims

- id
- report_id
- claim_text
- claim_type
- strength
- verification_status
- evidence_ids JSONB
- caveats JSONB

---

# 13. Raw Data Storage Strategy

Store raw StatsBomb JSON outside PostgreSQL.

Local development:

```text
./data/object_store/raw/statsbomb/{competition}/{season}/{match_id}.json.gz
```

Production:

```text
s3://bucket/raw/statsbomb/{competition}/{season}/{match_id}.json.gz
```

Store:

- URI
- SHA-256 hash
- ingestion version

inside PostgreSQL.

Normalized events go into PostgreSQL.

Future tracking data should be stored as compressed Parquet in object storage and queried with Polars/DuckDB when needed.

---

# 14. Analytics Engine Design

Every metric should implement a common interface.

```python
class MetricCalculator(Protocol):
    name: str
    version: str

    def calculate(self, context: MatchContext) -> list[MetricResult]:
        ...
```

Create a registry:

```python
METRIC_REGISTRY = {
    "shots": ShotMetrics(),
    "passing": PassingMetrics(),
    "progression": ProgressionMetrics(),
    "pressing": PressingMetrics(),
    "territory": TerritoryMetrics(),
}
```

Do not put metric logic inside LangGraph nodes.

---

# 15. Metric Definitions — MVP

## 15.1 Shots and xG

Inputs:

- shot events
- xG
- shot coordinates
- body part if available
- shot outcome

Calculate:

- shots
- shots on target
- goals
- total xG
- xG per shot
- open-play xG
- set-piece xG
- average shot distance
- big-chance style threshold counts if a project-specific threshold is configured

Version all definitions.

---

## 15.2 Passing Network

Inputs:

- passer
- receiver
- pass start/end coordinates
- completion outcome

Calculate:

- completed passes between player pairs
- pass volume by player
- network edge weights
- weighted degree
- betweenness centrality optional
- average/median action location per player

Minimum edge count should be configurable.

Do not call average event location a true average physical position.

---

## 15.3 Progressive Passes

Define a documented deterministic project rule.

Recommended initial logic:

Calculate distance to opponent goal before and after action.

Flag as progressive if action materially reduces that distance using zone-specific thresholds.

Store metric definition in code and documentation.

Suggested initial thresholds:

```text
Own half -> own half: >= 30m closer to goal
Own half -> opponent half: >= 15m closer
Opponent half -> opponent half: >= 10m closer
```

Exclude obvious backward/sideways actions.

Metric version:

```text
progressive_pass_v1
```

---

## 15.4 Progressive Carries

Use same progression logic on carry start/end locations.

Metric version:

```text
progressive_carry_v1
```

---

## 15.5 Field Tilt

Initial definition:

```text
Team completed passes in attacking third
----------------------------------------
Both teams completed passes in attacking third
```

Metric version:

```text
field_tilt_passes_v1
```

Store numerator and denominator as evidence.

---

## 15.6 PPDA

Use an explicit project definition.

Initial recommendation:

```text
Opponent completed passes in their build-up zone
-------------------------------------------------
Pressing team defensive actions in that zone
```

Defensive actions may include:

- pressures
- tackles
- interceptions
- fouls
- challenges

The exact pitch zone must be documented and versioned.

Example version:

```text
ppda_v1
```

Do not mix multiple PPDA definitions silently.

---

## 15.7 Final-Third Entries

Count completed passes/carries where:

```text
start_x < final_third_boundary
end_x >= final_third_boundary
```

Track separately:

- passes
- carries
- left channel
- central channel
- right channel

---

## 15.8 Box Entries

Count completed passes/carries that start outside the penalty area and end inside it.

Separate:

- pass entries
- carry entries
- cutback-style entries if deterministically identifiable

---

## 15.9 High Turnovers

A high turnover is a possession regain occurring in a configurable high zone near the opponent goal.

Store:

- event ID of regain
- location
- following possession result
- whether it led to a shot
- whether it led to a goal

Suggested outputs:

- high turnovers
- high turnovers leading to shot
- high turnovers leading to goal

---

## 15.10 Defensive Action Height

Use median X position of defensive actions.

Supported events may include:

- pressure
- tackle
- interception
- ball recovery
- block

Name this metric:

```text
defensive_action_height
```

Do not call it defensive line height.

---

## 15.11 Possession Sequences

Use StatsBomb possession IDs where reliable.

For each sequence calculate:

- start time
- end time
- duration
- starting zone
- ending zone
- number of passes
- number of carries
- progressive actions
- final-third entry
- box entry
- shot
- goal
- players involved

---

## 15.12 Build-Up Patterns

Start with deterministic heuristic labels.

Suggested labels:

```text
SHORT_BUILDUP
DIRECT_BUILDUP
LEFT_BUILDUP
RIGHT_BUILDUP
CENTRAL_BUILDUP
SWITCH_OF_PLAY
COUNTERATTACK
FAILED_BUILDUP
```

Use rules based on:

- sequence start location
- sequence duration
- number of actions
- vertical progression
- lateral movement
- field zones
- whether possession starts from restart/recovery

Document every rule.

The LLM may explain frequency and effectiveness, but may not invent pattern classifications.

---

## 15.13 Attacking Zones

Divide pitch into configurable grid or tactical lanes.

Recommended first version:

- defensive third
- middle third
- attacking third
- left lane
- left half-space
- central lane
- right half-space
- right lane

Calculate:

- touches/actions per zone
- progressive actions per zone
- final-third entries by lane
- box entries by lane
- shots by zone

---

## 15.14 Player Influence

Do not create one opaque "AI influence score" initially.

Show a transparent feature set:

- pass involvement
- progressive passes
- progressive carries
- final-third entries
- box entries
- shot involvement
- xG
- pressures
- recoveries
- passing-network degree
- on-ball centrality

A composite score may be added later only if its formula is deterministic and documented.

---

## 15.15 Substitution Impact

For each substitution compare configurable windows.

Default:

```text
10 minutes before
10 minutes after
```

Compare:

- xG
- shots
- field tilt
- final-third entries
- box entries
- high turnovers
- PPDA if sample size is adequate

Do not claim causality.

Approved language:

> Team A's attacking output increased after the substitution.

Avoid:

> The substitution caused Team A to dominate.

---

# 16. Visualization Requirements

Generate report-ready visualizations.

## MVP visualizations

1. Shot map
2. xG timeline
3. Passing network
4. Progressive pass/carry map
5. Defensive actions map
6. Final-third/box entry map
7. Team attacking heatmap
8. Average Action Position map

Use:

- mplsoccer
- matplotlib
- NetworkX
- Plotly where interactivity adds value

Generated static assets should be stored in object storage.

Return their URLs/URIs through the API.

---

# 17. Evidence Packet

The LLM should never receive the full raw event feed by default.

Create a compact `EvidencePacket`.

Example:

```json
{
  "match": {
    "home_team": "Team A",
    "away_team": "Team B",
    "score": "2-1",
    "home_formation": "4-3-3",
    "away_formation": "4-2-3-1"
  },
  "metrics": [
    {
      "evidence_id": "METRIC_PPDA_TEAM_A",
      "metric": "ppda",
      "team": "Team A",
      "value": 7.8,
      "opponent_value": 14.2,
      "comparison": "45.1% lower",
      "source_event_ids": ["..."],
      "definition_version": "ppda_v1"
    }
  ],
  "key_sequences": [],
  "key_events": [],
  "substitution_windows": [],
  "capabilities": {}
}
```

The analytics layer should precompute comparisons such as:

- absolute differences
- percentage differences
- team rank between the two sides

Do not ask Gemini to calculate them.

---

# 18. LLM Output Schema

## Tactical interpretation output

Create Pydantic schemas.

```python
class TacticalClaim(BaseModel):
    claim_id: str
    topic: str
    claim: str
    evidence_ids: list[str]
    strength: Literal["weak", "moderate", "strong"]
    caveats: list[str] = []


class TacticalInterpretation(BaseModel):
    match_summary: str
    claims: list[TacticalClaim]
    turning_points: list[TacticalClaim]
    player_findings: list[TacticalClaim]
```

Require Gemini structured output.

---

# 19. LLM Prompt Rules

The tactical interpretation prompt must explicitly state:

1. Do not calculate statistics.
2. Do not invent statistics.
3. Do not use a number unless present in evidence.
4. Every important tactical claim must reference evidence IDs.
5. If evidence is insufficient, say so.
6. Do not describe true player positioning unless tracking/360 capability exists.
7. Prefer correlation language over unsupported causality.
8. Do not mention metrics not included in the evidence packet.
9. Distinguish territorial dominance from chance quality.
10. Distinguish pressure activity from successful pressing outcomes.

---

# 20. Verification Layer

Verification should be mostly deterministic.

## Numeric verifier

Extract numeric values from generated structured claims/report and ensure they exist in evidence.

Any unseen number is rejected.

## Evidence verifier

For every claim:

```text
claim.evidence_ids must exist in EvidencePacket
```

Important claims require at least one valid evidence item.

Strong tactical claims should normally require at least two independent evidence signals.

## Capability verifier

Reject claims like:

> Team A maintained a compact 31m block.

if tracking data does not exist.

## Repair route

If verification fails:

```text
interpretation
    |
    v
verification
    |
    +-- pass --> final report
    |
    `-- fail --> repair prompt --> verification
```

Maximum repair attempts should be configurable.

---

# 21. LangGraph Workflow

Use LangGraph as deterministic orchestration, not as a collection of seven autonomous agents.

Recommended graph:

```text
START
  |
  v
validate_match
  |
  v
ensure_match_ingested
  |
  v
calculate_metrics
  |
  v
generate_visualizations
  |
  v
build_evidence_packet
  |
  v
tactical_interpretation_llm
  |
  v
verify_claims
  |\
  | \ invalid
  |  v
  | repair_claims
  |  |
  |  `----> verify_claims
  |
 valid
  |
  v
final_report_llm
  |
  v
final_numeric_verification
  |
  v
persist_report
  |
  v
END
```

---

# 22. LangGraph State

Suggested state:

```python
class TacticalAnalysisState(TypedDict):
    job_id: str
    match_id: str

    provider: str
    provider_capabilities: dict

    match_loaded: bool
    metric_results: list[dict]
    visualization_assets: list[dict]

    evidence_packet: dict | None
    interpretation: dict | None
    verification_errors: list[str]
    verification_attempts: int

    report: dict | None
    report_markdown: str | None

    errors: list[str]
```

Do not place giant raw event arrays in LangGraph state if avoidable.

Pass database/object-store references instead.

---

# 23. FastAPI API Design

## Health

```text
GET /health
```

## Competitions

```text
GET /competitions
GET /competitions/{id}/seasons
```

## Matches

```text
GET /matches
GET /matches/{match_id}
POST /matches/{match_id}/ingest
```

## Metrics

```text
GET /matches/{match_id}/metrics
```

## Analysis

```text
POST /matches/{match_id}/analyze
```

Return:

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

## Jobs

```text
GET /jobs/{job_id}
```

## Reports

```text
GET /reports/{report_id}
GET /reports/{report_id}/evidence
GET /reports/{report_id}/claims/{claim_id}/evidence
```

---

# 24. Background Worker Design

Use Celery + Redis.

Tasks:

```text
ingest_match
calculate_match_metrics
generate_match_visualizations
run_tactical_analysis
```

The API should not synchronously run the full report generation pipeline.

---

# 25. Caching Strategy

Cache aggressively because completed match data does not change often.

Redis keys may include:

```text
competition:{id}:matches
match:{id}:metadata
match:{id}:metrics:{analytics_version}
report:{match_id}:{evidence_hash}:{prompt_version}:{model}
```

Use evidence/input hashes to avoid unnecessary repeated LLM calls.

If match inputs, prompt version, model config, and evidence hash are unchanged, reuse the existing tactical report.

---

# 26. Frontend Requirements

## Page 1 — Match Explorer

Allow user to:

- choose competition
- choose season
- select completed match
- see score/date/teams
- click `Analyze Match`

## Page 2 — Analysis Dashboard

Sections:

### Overview

- score
- xG
- possession
- shots
- formations
- short tactical summary

### Territory & Progression

- field tilt
- final-third entries
- box entries
- progressive passes/carries
- entry maps

### Pressing & Defending

- PPDA
- high turnovers
- defensive action height
- defensive action map

### Build-Up

- passing network
- possession sequences
- build-up pattern distribution

### Players

- player metrics
- influence indicators
- average action positions

### Substitutions

- timeline
- pre/post metrics

### Tactical Report

- markdown-rendered final report
- evidence buttons for claims

---

# 27. Evidence UI

Every major claim should optionally expose its evidence.

Example:

```text
Team A consistently pinned Team B back with an aggressive press.
[View Evidence]
```

Evidence drawer:

```text
PPDA
Team A: 7.8
Team B: 14.2

High turnovers
Team A: 11
Team B: 4

Attacking-third pressures
Team A: 18
Team B: 7

Metric definitions:
ppda_v1
high_turnover_v1
```

This feature is a high-priority portfolio differentiator.

---

# 28. Logging and Observability

Use structured logs.

Every analysis job should log:

- job ID
- match ID
- provider
- analytics version
- LLM provider/model
- evidence hash
- prompt version
- timings by workflow node
- token usage if available
- retry count
- verification failures

Avoid logging API keys or full sensitive configuration.

---

# 29. Testing Strategy

Testing is mandatory at every phase.

## Unit tests

Analytics metrics must use synthetic events with hand-calculated expected values.

Examples:

- field tilt = known fraction
- PPDA = known result
- progressive pass classification
- final-third boundary crossing
- box entry classification
- high turnover classification
- possession sequence grouping
- pre/post substitution windows

## Provider tests

Test StatsBomb normalization against stored fixture JSON.

Do not require network calls for most tests.

## Golden-match tests

Store a small number of known StatsBomb match fixtures.

Assert stable values for:

- shots
- xG
- PPDA
- field tilt
- progressive actions
- entries
- possessions

## Graph tests

Mock the LLM.

Test:

- happy path
- unsupported tactical claim
- invented number
- missing evidence ID
- repair path
- retry limit
- persistence

## API tests

Use FastAPI/httpx.

Test:

- validation
- missing match
- enqueue analysis
- job status
- report retrieval

## Frontend tests

Test:

- match selection
- analysis submission
- loading state
- report rendering
- visualization rendering
- evidence drawer

---

# 30. Evaluation Strategy

Create a manually reviewed evaluation set of at least 10 matches.

For each generated report evaluate:

- numerical accuracy
- claim grounding
- tactical usefulness
- unsupported claims
- unsupported causality
- contradictions
- repetition
- evidence coverage

Key release criteria:

```text
Unsupported numeric claims = 0
Unknown evidence references = 0
Metrics outside provider capability = 0
```

---

# 31. Docker Setup

Create services:

```text
backend
worker
frontend
postgres
redis
minio
```

`docker compose up --build` should start the entire local application.

Add health checks.

---

# 32. CI/CD

GitHub Actions pipeline:

```text
install backend dependencies
lint
backend unit tests
backend integration tests
frontend install
frontend lint
frontend tests
frontend build
Docker build validation
```

Recommended backend quality tools:

- ruff
- mypy or pyright
- pytest

---

# 33. PHASED IMPLEMENTATION PLAN

# Phase 1 — Project Foundation + Data Ingestion

## Create

```text
config/settings.py
providers/soccer/base.py
providers/soccer/statsbomb_open.py
providers/soccer/capabilities.py
schemas/match.py
schemas/event.py
schemas/lineup.py
ingestion/service.py
ingestion/normalizer.py
ingestion/coordinates.py
ingestion/validators.py
db/models.py
db/session.py
storage/base.py
storage/local.py
```

## Functionality

- initialize Python project with uv
- add FastAPI skeleton
- configure settings
- configure PostgreSQL
- create Alembic
- load StatsBomb competitions
- list matches
- ingest match metadata
- ingest lineups
- ingest events
- normalize coordinates
- store raw JSON
- store normalized events
- make ingestion idempotent

## Tests

- settings tests
- StatsBomb fixture parsing
- coordinate normalization
- event validation
- duplicate ingestion
- DB persistence

## Expected output

A selected StatsBomb match can be loaded into PostgreSQL and queried through Python.

---

# Phase 2 — Analytics Engine

## Create

```text
analytics/base.py
analytics/registry.py
analytics/shots.py
analytics/passing.py
analytics/progression.py
analytics/territory.py
analytics/pressing.py
analytics/possession.py
analytics/transitions.py
analytics/spatial.py
analytics/players.py
analytics/substitutions.py
schemas/metric.py
```

## Functionality

Implement versioned metrics for:

- shots
- xG
- xG/shot
- passing network data
- progressive passes
- progressive carries
- field tilt
- PPDA
- final-third entries
- box entries
- high turnovers
- defensive action height
- possession sequences
- build-up patterns
- attacking zones
- player influence features
- substitution impact

Persist calculated metrics.

## Tests

Each metric requires synthetic fixture tests with manually known expected outputs.

Add golden-match regression tests.

## Expected output

```json
{
  "home": {
    "xg": 2.17,
    "ppda": 7.8,
    "field_tilt": 0.63,
    "progressive_passes": 43,
    "box_entries": 24
  },
  "away": {}
}
```

---

# Phase 3 — Tactical Visualizations

## Create

```text
visualization/base.py
visualization/pitch.py
visualization/passing_network.py
visualization/shot_map.py
visualization/xg_timeline.py
visualization/progressive_actions.py
visualization/defensive_actions.py
visualization/heatmap.py
```

## Functionality

Generate:

- passing network
- shot map
- xG timeline
- progressive pass/carry map
- defensive actions map
- entry map
- attacking heatmap
- average action positions

Persist assets to object storage.

## Tests

- output files exist
- valid pitch coordinates
- correct number of shots/actions
- deterministic naming/storage

## Expected output

A folder/object-store path containing report-ready images for a match.

---

# Phase 4 — Gemini + LangGraph Analysis

## Create

```text
providers/llm/base.py
providers/llm/factory.py
providers/llm/gemini.py
llm/schemas.py
llm/service.py
llm/prompts/tactical_interpreter.md
llm/prompts/final_report.md
evidence/builder.py
evidence/registry.py
graph/state.py
graph/nodes.py
graph/routing.py
graph/workflow.py
verification/claim_verifier.py
verification/numeric_verifier.py
verification/coverage_verifier.py
```

## Functionality

- Gemini provider
- provider-agnostic LLM factory
- EvidencePacket creation
- structured tactical interpretation
- claim evidence references
- deterministic claim verification
- repair path
- final report generation
- final numeric verification

## Tests

Mock Gemini.

Test:

- supported claim
- unsupported claim
- invented statistic
- unknown evidence ID
- unavailable capability
- repair loop
- retry ceiling

## Expected output

A verified tactical report with evidence-linked claims.

---

# Phase 5 — FastAPI + Background Jobs

## Create

```text
api/app.py
api/dependencies.py
api/routes/health.py
api/routes/competitions.py
api/routes/matches.py
api/routes/metrics.py
api/routes/reports.py
api/routes/jobs.py
workers/tasks.py
```

## Functionality

- browse competitions
- browse seasons
- browse completed matches
- trigger ingestion
- retrieve metrics
- start asynchronous report generation
- retrieve job status
- retrieve report
- retrieve claim evidence

Use Celery + Redis.

## Tests

- endpoints
- queue mocking
- report retrieval
- errors
- validation

## Expected output

Fully functional backend API with OpenAPI documentation.

---

# Phase 6 — React Frontend

## Create

Pages/components for:

- Match Explorer
- Match Analysis Dashboard
- Metrics Cards
- Passing Network
- Shot Map
- xG Timeline
- Progression Map
- Pressing Section
- Player Section
- Substitution Timeline
- Tactical Report
- Evidence Drawer

## Functionality

User flow:

```text
Select competition
    -> select season
        -> select match
            -> Analyze Match
                -> job progress
                    -> tactical dashboard
```

Render report Markdown.

## Tests

- selection flow
- API error state
- loading state
- report rendering
- visualization components
- evidence drawer

## Expected output

End-to-end usable web application.

---

# Phase 7 — Evaluation, Reliability, Performance

## Implement

- 10+ match evaluation dataset
- analytics regression tests
- claim-grounding evaluator
- retry/backoff for Gemini errors
- request timeouts
- caching
- idempotent jobs
- duplicate-report prevention using evidence hash
- structured logging
- optional LangSmith tracing

## Acceptance criteria

```text
Unsupported numeric claims = 0
Unknown evidence references = 0
Unavailable-metric claims = 0
All deterministic regression tests pass
```

---

# Phase 8 — Deployment

## Implement

- production Dockerfiles
- Docker Compose local setup
- GitHub Actions
- managed PostgreSQL support
- managed Redis support
- S3/R2 object storage support
- environment-specific config
- health/readiness endpoints
- database backups
- logging/monitoring hooks

## Initial hosting target

Keep deployment provider-neutral.

Possible initial targets:

- Railway
- Render
- Fly.io
- AWS ECS/Fargate

Do not hard-code infrastructure provider behavior into application code.

---

# 34. Optional Phase 9 — Advanced Tracking Analytics

After MVP completion, add SkillCorner Open Data or another tracking provider.

New metrics may include:

- true average position
- defensive line height
- team width
- team depth
- compactness
- inter-line distance
- pressure distance
- off-ball runs
- player spacing
- rest-defense shape

Tracking data should use a separate provider abstraction.

Do not force tracking-specific columns into ordinary event tables.

---

# 35. Coding Guidelines for Codex

1. Implement one phase at a time.
2. Do not start a later phase before the current phase tests pass.
3. Keep business logic out of API routes.
4. Keep deterministic calculations out of LLM prompts.
5. Keep provider-specific logic inside provider adapters.
6. Prefer typed Pydantic models over unstructured dictionaries.
7. Prefer Polars for event analytics where practical.
8. Add docstrings to public interfaces.
9. Version analytics formulas.
10. Do not silently change a metric definition.
11. Never hard-code secrets.
12. Never commit `.env`.
13. Never call Gemini directly inside LangGraph nodes; use the LLM service/factory.
14. Do not pass full raw match JSON to the LLM unless explicitly needed.
15. Log the evidence hash, prompt version, model and metric versions for every report.
16. Make ingestion and report generation idempotent.
17. Use stable canonical IDs internally where possible.
18. Separate raw provider payloads from canonical models.
19. Add tests with every feature.
20. Keep README architecture and commands current as phases are completed.

---

# 36. Definition of Done — MVP

The MVP is complete when a user can:

1. open the React application,
2. choose a StatsBomb competition and season,
3. choose a completed match,
4. click `Analyze Match`,
5. have the system ingest the match if required,
6. deterministically calculate tactical metrics,
7. generate tactical visualizations,
8. build an evidence packet,
9. send only computed evidence to Gemini,
10. receive structured tactical claims,
11. reject/repair unsupported claims,
12. generate a final tactical report,
13. view report + charts in the frontend,
14. click an important tactical claim and inspect its supporting evidence.

The system must pass all analytics, API, graph, and verification tests before the MVP is considered finished.

---

# 37. Recommended Implementation Order for Codex

Codex should execute this project strictly in this order:

```text
1. Scaffold repository
2. Configure Python project and settings
3. Configure PostgreSQL + Alembic
4. Implement StatsBomb provider
5. Implement canonical schemas and normalization
6. Persist matches/lineups/events
7. Build deterministic analytics engine
8. Add metric regression tests
9. Add visualizations
10. Add evidence builder
11. Add Gemini provider abstraction
12. Add LangGraph workflow
13. Add verification layer
14. Add FastAPI routes
15. Add Celery/Redis workers
16. Add React frontend
17. Add evidence inspection UI
18. Add caching
19. Add reliability/evaluation tests
20. Add Docker/CI/deployment documentation
```

At the end of each phase, Codex should:

1. run the complete test suite,
2. fix failures,
3. update README progress,
4. summarize files added/changed,
5. state the next phase to implement.

