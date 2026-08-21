# Deployment

The application is deployment-provider neutral. The local production-like stack uses Docker
Compose with:

- backend FastAPI service
- Celery worker
- React frontend served by Nginx
- PostgreSQL
- Redis
- local filesystem object storage for the MVP
- MinIO only if you decide to exercise S3-compatible storage later

## Local Compose

```powershell
copy .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`
- Backend readiness: `http://localhost:8000/ready`
- MinIO console, if enabled: `http://localhost:9001`

## Required Production Settings

Set these per environment:

```dotenv
APP_ENV=production
DATABASE_URL=
REDIS_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
OBJECT_STORAGE_PROVIDER=s3
S3_ENDPOINT_URL=
S3_BUCKET=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
GOOGLE_API_KEY=
GEMINI_MODEL=
```

For the MVP, keep object storage local:

```dotenv
OBJECT_STORAGE_PROVIDER=local
OBJECT_STORAGE_PATH=./data/object_store
```

Use S3, R2, or MinIO later only when multiple deployed services need shared durable files.

## Backups

PostgreSQL backups should be managed by the hosting provider or scheduled with `pg_dump`.
Object storage should use bucket versioning or provider-native lifecycle backups.

## Logs

The backend emits structured analysis log payloads through Python logging. Container platforms
should collect stdout/stderr and ship them to the selected provider log sink.

## Provider Notes

Railway, Render, Fly.io, AWS ECS/Fargate, and similar platforms can run the same service
layout. Keep provider-specific settings in environment variables rather than application code.
