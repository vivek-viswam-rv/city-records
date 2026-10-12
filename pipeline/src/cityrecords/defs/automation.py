
import os
from datetime import timedelta

import dagster as dg

from .assets import GROUP

daily_job = dg.define_asset_job("daily_job", selection=dg.AssetSelection.groups(GROUP))
FAILURE_TAGS = ["pipeline"]  # Honeybadger's GitHub integration turns this into the issue label


def previous_business_day_key(tick_date) -> str:
    """Mon -> previous Fri; otherwise the previous calendar day."""
    back = 3 if tick_date.weekday() == 0 else 1
    return (tick_date - timedelta(days=back)).strftime("%Y-%m-%d")


@dg.schedule(job=daily_job, cron_schedule="0 14 * * 1-5", execution_timezone="UTC",
             default_status=dg.DefaultScheduleStatus.RUNNING)
def daily_schedule(context: dg.ScheduleEvaluationContext):
    key = previous_business_day_key(context.scheduled_execution_time)
    return dg.RunRequest(run_key=key, partition_key=key)


@dg.run_failure_sensor(default_status=dg.DefaultSensorStatus.RUNNING)
def run_failure_sensor(context: dg.RunFailureSensorContext):
    run = context.dagster_run
    msg = context.failure_event.message or "run failed"
    ctx = {
        "job": run.job_name,
        "run_id": run.run_id,
        "partition": run.tags.get("dagster/partition"),
        "dagster_url": f"{os.getenv('DAGSTER_URL', 'http://localhost:3000')}/runs/{run.run_id}",
    }
    api_key = os.getenv("HONEYBADGER_API_KEY")
    if api_key:
        from honeybadger import honeybadger

        honeybadger.configure(api_key=api_key, environment=os.getenv("APP_ENV", "production"))
        honeybadger.notify(error_class="DagsterRunFailure", error_message=msg, context=ctx, tags=FAILURE_TAGS,
                           fingerprint=f"{run.job_name}:{ctx['partition']}")
    else:
        context.log.error(f"DagsterRunFailure (HONEYBADGER_API_KEY unset): {msg} {ctx}")
