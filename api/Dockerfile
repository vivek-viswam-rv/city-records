# Build from repo root: docker build -f api/Dockerfile .
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY api/ /app/api/
# The API queries the cr schema directly and does not import the pipeline package.
RUN uv pip install /app/api
EXPOSE 8000
# KEEP IN SYNC (API agent): module `cityrecords_api.main:app` must match api/pyproject.toml package name.
CMD ["uvicorn", "cityrecords_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
