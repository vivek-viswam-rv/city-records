# city-records pipeline

Dagster pipeline: NYC City Record procurement notices (Socrata `dg92-zbpx`) -> S3 + Postgres (`cr` schema), enriched by Bedrock.

Assets (group `cityrecord`, daily partitions from 2026-09-01): `raw_notices` -> `enriched_notices` -> `vendors`.
`daily_schedule` (14:00 UTC Mon-Fri) runs the previous business day. `run_failure_sensor` reports to Honeybadger.

## Setup
```bash
uv sync
# env: repo-root .env is loaded in dev (pipeline/.env is a symlink to ../.env for dg CLI)
uv run alembic upgrade head      # creates schema cr + notices/enrichments/vendors
export DAGSTER_HOME=$PWD         # dagster.yaml -> Postgres storage via DATABASE_URL (public schema)
uv run dg check defs && uv run dg list defs
uv run dg dev                    # UI at :3000
uv run dg launch --assets '*' --partition 2026-10-09
uv run pytest -q
```
Required env: DATABASE_URL, S3_BUCKET, AWS_REGION, AWS_ACCESS_KEY_ID/SECRET, BEDROCK_MODEL_ID, SOCRATA_APP_TOKEN.
Optional: LANGFUSE_*, HONEYBADGER_API_KEY, DAGSTER_URL, APP_ENV.

## Docker
```bash
docker build -t cityrecords-pipeline pipeline/
docker run --env-file .env -p 3030:3030 cityrecords-pipeline          # code server (gRPC)
docker run --env-file .env cityrecords-pipeline alembic upgrade head   # migrations
```
