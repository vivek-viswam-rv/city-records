import json
import os
from pathlib import Path

import pytest

# Tests never talk to Langfuse. Set (not pop) so the dev .env loaded by cityrecords.definitions
# cannot re-enable it: python-dotenv does not override variables that already exist.
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "")


@pytest.fixture
def socrata_rows():
    return json.loads((Path(__file__).parent / "fixtures" / "socrata_rows.json").read_text())
