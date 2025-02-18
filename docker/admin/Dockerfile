FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY admin_app/pyproject.toml \
    admin_app/uv.lock ./

FROM base AS prod

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen --extra prod

ENV PATH="/app/.venv/bin:$PATH"

COPY admin_app/src/ /app/src


FROM base AS dev

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen --extra dev

ENV PATH="/app/.venv/bin:$PATH"

COPY admin_app/src/ /app/src
