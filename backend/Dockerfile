FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY src ./src
COPY scripts ./scripts

# Windows checkouts may give shell scripts CRLF endings, which Linux reads as `sh\r`.
RUN sed -i 's/\r$//' scripts/*.sh && chmod +x scripts/*.sh

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["sh", "-c", "scripts/prestart.sh && uvicorn tactical_analyst.api.app:app --host 0.0.0.0 --port 8000"]
