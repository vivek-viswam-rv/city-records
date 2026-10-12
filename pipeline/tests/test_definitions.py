"""The whole code location must load: every asset, job, schedule, sensor and resource binding."""
import dagster as dg

from cityrecords.definitions import defs


def test_definitions_load_and_bind():
    d = defs()
    assert isinstance(d, dg.Definitions)
    assert {k.to_user_string() for k in d.resolve_asset_graph().get_all_asset_keys()} == {
        "raw_notices", "enriched_notices", "vendors"}
    assert d.resolve_job_def("daily_job")
    assert d.resolve_schedule_def("daily_schedule")
    assert d.resolve_sensor_def("run_failure_sensor")
    assert set(d.resources) == {"db", "store", "bedrock", "socrata"}
