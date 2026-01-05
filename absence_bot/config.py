"""Configuration loader for AbsenceBot."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import importlib.util

if importlib.util.find_spec("tomllib"):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib


@dataclass(frozen=True)
class DatabaseConfig:
    engine: str
    host: str
    port: int
    name: str
    user: str
    password: str
    sqlite_path: str


@dataclass(frozen=True)
class BotConfig:
    token: str
    timezone: str
    authorized_teacher_ids: List[int]
    grades: Dict[str, List[str]]
    page_size: int
    database: DatabaseConfig


class ConfigError(RuntimeError):
    """Raised when configuration is missing or invalid."""


def load_config(path: str | Path) -> BotConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"Config file not found at {config_path}. Copy config.example.toml to config.toml."
        )

    data = tomllib.loads(config_path.read_text())
    database = data.get("database", {})
    bot = data.get("bot", {})

    authorized_ids = bot.get("authorized_teacher_ids", [])
    if not isinstance(authorized_ids, list) or not all(
        isinstance(item, int) for item in authorized_ids
    ):
        raise ConfigError("authorized_teacher_ids must be a list of integers.")

    grades = bot.get("grades", {})
    if not isinstance(grades, dict) or not grades:
        raise ConfigError("grades must be a mapping of grade names to majors.")

    timezone = str(bot.get("timezone", "UTC"))
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Invalid timezone: {timezone}") from exc

    return BotConfig(
        token=str(bot.get("token", "")).strip(),
        timezone=timezone,
        authorized_teacher_ids=authorized_ids,
        grades={str(grade): [str(major) for major in majors] for grade, majors in grades.items()},
        page_size=int(bot.get("page_size", 10)),
        database=DatabaseConfig(
            engine=str(database.get("engine", "sqlite")),
            host=str(database.get("host", "localhost")),
            port=int(database.get("port", 3306)),
            name=str(database.get("name", "absence_bot")),
            user=str(database.get("user", "")),
            password=str(database.get("password", "")),
            sqlite_path=str(database.get("sqlite_path", "absence_bot.sqlite3")),
        ),
    )
