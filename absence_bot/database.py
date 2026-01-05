"""Database connection helpers."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from absence_bot.config import DatabaseConfig
from absence_bot.models import Base


@dataclass
class Database:
    engine: Engine
    session_factory: sessionmaker


def _build_database_url(config: DatabaseConfig) -> str:
    if config.engine == "mysql":
        return (
            f"mysql+pymysql://{config.user}:{config.password}"
            f"@{config.host}:{config.port}/{config.name}"
        )
    if config.engine == "sqlite":
        return f"sqlite:///{config.sqlite_path}"
    raise ValueError(f"Unsupported database engine: {config.engine}")


def create_database(config: DatabaseConfig) -> Database:
    url = _build_database_url(config)
    engine = create_engine(url, pool_pre_ping=True, future=True)
    Base.metadata.create_all(engine)
    return Database(engine=engine, session_factory=sessionmaker(bind=engine, expire_on_commit=False))


@contextmanager
def session_scope(database: Database) -> Iterator[Session]:
    session = database.session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
