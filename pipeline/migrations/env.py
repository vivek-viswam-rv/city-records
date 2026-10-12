import os
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

for p in Path(__file__).resolve().parents:
    if (p / ".env").is_file():
        load_dotenv(p / ".env")
        break

from cityrecords.resources import to_sqlalchemy_url  # noqa: E402

config = context.config
url = to_sqlalchemy_url(os.environ["DATABASE_URL"])


def run() -> None:
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text("create schema if not exists cr"))
        conn.commit()
        context.configure(connection=conn, target_metadata=None, version_table_schema="cr")
        with context.begin_transaction():
            context.run_migrations()


run()
