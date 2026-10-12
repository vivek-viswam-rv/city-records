from pathlib import Path

import dagster as dg
from dotenv import load_dotenv

# Dev only: pick up the repo-root .env if present (no-op in containers).
for _p in Path(__file__).resolve().parents:
    if (_p / ".env").is_file():
        load_dotenv(_p / ".env")
        break


@dg.definitions
def defs() -> dg.Definitions:
    """Assets, jobs, schedules, sensors and resources are autoloaded from cityrecords/defs/."""
    return dg.load_from_defs_folder(project_root=Path(__file__).resolve().parents[2])
