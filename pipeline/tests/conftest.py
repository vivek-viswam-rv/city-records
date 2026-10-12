import json
import os
from pathlib import Path

import pytest

# Tests never talk to Langfuse, even when the developer's shell has exported the dev .env.
# Force the keys empty (not pop): the .env loaded by cityrecords.definitions cannot re-enable
# tracing because python-dotenv does not override variables that already exist.
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""


@pytest.fixture
def socrata_rows():
    return json.loads((Path(__file__).parent / "fixtures" / "socrata_rows.json").read_text())
