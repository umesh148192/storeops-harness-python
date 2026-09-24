FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 1000 appuser
USER appuser

ENV PATH="/app/.venv/bin:${PATH}"
ENV PORT=8000
ENV LOG_LEVEL=info

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/health', timeout=2)" || exit 1

CMD ["sh", "-c", "uvicorn storeops.main:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL}"]
