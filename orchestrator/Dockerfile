# Multi-stage build — 2026 best practice
FROM python:3.12-slim AS builder

WORKDIR /build
COPY orchestrator/pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .[dev]

FROM python:3.12-slim AS runtime

# Non-root user (security best practice)
RUN groupadd -r orchestrator && useradd -r -g orchestrator orchestrator

COPY --from=builder /install /usr/local
WORKDIR /app

COPY orchestrator/src/orchestrator ./src/orchestrator
COPY orchestrator/tests ./tests

USER orchestrator

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
