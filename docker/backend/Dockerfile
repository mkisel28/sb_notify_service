FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY backend_app/pyproject.toml \
backend_app/uv.lock ./

FROM base AS prod

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen --extra prod

ENV PATH="/app/.venv/bin:$PATH"

COPY backend_app/src/ /app/src
WORKDIR /app/src
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]


FROM base AS dev

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen --extra dev

ENV PATH="/app/.venv/bin:$PATH"

COPY backend_app/src/ /app/src
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
