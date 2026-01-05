"""Database connection helpers."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from absence_bot.config import DatabaseConfig
from absence_bot.models import Base, Grade


@dataclass
class Database:
    engine: Engine
    session_factory: sessionmaker


def _build_database_url(config: DatabaseConfig) -> str:
    return f"sqlite:///{config.sqlite_path}"


def create_database(config: DatabaseConfig) -> Database:
    url = _build_database_url(config)
    engine = create_engine(url, pool_pre_ping=True, future=True)
    Base.metadata.create_all(engine)
    return Database(engine=engine, session_factory=sessionmaker(bind=engine, expire_on_commit=False))


def seed_grades(database: Database, grades: list[str]) -> None:
    if not grades:
        return
    with session_scope(database) as session:
        existing = session.query(Grade).first()
        if existing:
            return
        unique_grades = {grade.strip() for grade in grades if grade.strip()}
        session.add_all([Grade(name=grade) for grade in sorted(unique_grades)])


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
