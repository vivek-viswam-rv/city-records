from pathlib import Path

import dagster as dg
from dotenv import load_dotenv

# Dev only: pick up the repo-root .env if present (no-op in containers).
for _p in Path(__file__).resolve().parents:
    if (_p / ".env").is_file():
        load_dotenv(_p / ".env")
        break

from .assets import enriched_notices, raw_notices, vendors  # noqa: E402
from .automation import daily_job, daily_schedule, run_failure_sensor  # noqa: E402
from .resources import Bedrock, ObjectStore, Postgres, Socrata  # noqa: E402

defs = dg.Definitions(
    assets=[raw_notices, enriched_notices, vendors],
    jobs=[daily_job],
    schedules=[daily_schedule],
    sensors=[run_failure_sensor],
    resources={
        "db": Postgres(database_url=dg.EnvVar("DATABASE_URL")),
        "store": ObjectStore(bucket=dg.EnvVar("S3_BUCKET"), region=dg.EnvVar("AWS_REGION")),
        "bedrock": Bedrock(region=dg.EnvVar("AWS_REGION"), model_id=dg.EnvVar("BEDROCK_MODEL_ID")),
        "socrata": Socrata(app_token=dg.EnvVar("SOCRATA_APP_TOKEN")),
    },
)
