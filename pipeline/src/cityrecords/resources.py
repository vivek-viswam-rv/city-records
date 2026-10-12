
import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import boto3
import dagster as dg
from pydantic import PrivateAttr
from sqlalchemy import Connection, Engine, create_engine


def to_sqlalchemy_url(url: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


SECTIONS = (
    "Procurement",
    "Public Comment on Contract Awards",
    "Contract Award Hearings",
    "Public Hearings and Meetings",
)


class Postgres(dg.ConfigurableResource):
    """Owns the SQLAlchemy engine for a run. Assets borrow connections; they never see the engine.

    The engine (and its pool) is created once when the run starts and disposed when it ends, so an
    asset that touches the database three times shares one pool instead of building three.
    """

    database_url: str
    _engine: Engine | None = PrivateAttr(default=None)

    def setup_for_execution(self, context: dg.InitResourceContext) -> None:
        self._engine = create_engine(to_sqlalchemy_url(self.database_url), pool_pre_ping=True)

    def teardown_after_execution(self, context: dg.InitResourceContext) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def _get_engine(self) -> Engine:
        if self._engine is None:  # direct use outside a Dagster run, e.g. scripts
            self._engine = create_engine(to_sqlalchemy_url(self.database_url), pool_pre_ping=True)
        return self._engine

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        """Read-only work: autocommit-free connection, closed on exit."""
        with self._get_engine().connect() as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        """Writes: one transaction, committed on exit or rolled back on error."""
        with self._get_engine().begin() as conn:
            yield conn


class ObjectStore(dg.ConfigurableResource):
    bucket: str
    region: str

    def _client(self):
        return boto3.client("s3", region_name=self.region)

    def put_json(self, key: str, payload: Any) -> str:
        self._client().put_object(
            Bucket=self.bucket, Key=key, Body=json.dumps(payload, default=str).encode(), ContentType="application/json"
        )
        return key


class Bedrock(dg.ConfigurableResource):
    region: str
    model_id: str

    def client(self):
        from botocore.config import Config

        return boto3.client("bedrock-runtime", region_name=self.region, config=Config(read_timeout=120, retries={"max_attempts": 3}))


class Socrata(dg.ConfigurableResource):
    app_token: str = ""
    base_url: str = "https://data.cityofnewyork.us/resource/dg92-zbpx.json"
    page_size: int = 5000

    def fetch_day(self, day: str) -> list[dict[str, Any]]:
        import requests

        sections = ",".join("'" + s + "'" for s in SECTIONS)
        where = f"start_date between '{day}T00:00:00' and '{day}T23:59:59.999' and section_name in({sections})"
        headers = {"X-App-Token": self.app_token} if self.app_token else {}
        rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            r = requests.get(
                self.base_url,
                params={"$where": where, "$order": "request_id", "$limit": self.page_size, "$offset": offset},
                headers=headers,
                timeout=60,
            )
            r.raise_for_status()
            page = r.json()
            rows.extend(page)
            if len(page) < self.page_size:
                return rows
            offset += self.page_size
