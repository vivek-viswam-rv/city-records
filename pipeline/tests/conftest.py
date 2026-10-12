import json
from pathlib import Path

import pytest


@pytest.fixture
def socrata_rows():
    return json.loads((Path(__file__).parent / "fixtures" / "socrata_rows.json").read_text())
