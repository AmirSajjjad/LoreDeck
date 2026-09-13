FROM python:3.13-slim-bookworm AS builder

ARG UV_VERSION=0.8.19
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY static ./static
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN addgroup --system loredeck && adduser --system --ingroup loredeck loredeck

WORKDIR /app
COPY --from=builder --chown=loredeck:loredeck /app /app

USER loredeck
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/decks', timeout=3).read()"]

CMD ["uvicorn", "loredeck.game.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
