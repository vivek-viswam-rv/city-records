FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1 DAGSTER_HOME=/app
WORKDIR /app
# deps first (cached layer); runtime deps only, no dev group
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini dagster.yaml ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 3030
# gRPC code server for a Dagster webserver/daemon. Migrate with: docker run ... alembic upgrade head
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "3030", "-m", "cityrecords.definitions"]
