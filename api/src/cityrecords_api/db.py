import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = os.environ["DATABASE_POOL_URL"]
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    # Supabase transaction pooler: no server-side prepared statements.
    return create_engine(
        url,
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"prepare_threshold": None},
    )


def db_ok() -> bool:
    try:
        from sqlalchemy import text

        with get_engine().connect() as c:
            c.execute(text("select 1"))
        return True
    except Exception:
        return False
