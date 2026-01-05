"""Configuration loader for AbsenceBot."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import importlib.util

if importlib.util.find_spec("tomllib"):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib


@dataclass(frozen=True)
class DatabaseConfig:
    sqlite_path: str


@dataclass(frozen=True)
class BotConfig:
    token: str
    timezone: str
    authorized_teacher_ids: List[int]
    management_user_ids: List[int]
    grades: List[str]
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

    management_ids = bot.get("management_user_ids", [])
    if not isinstance(management_ids, list) or not all(
        isinstance(item, int) for item in management_ids
    ):
        raise ConfigError("management_user_ids must be a list of integers.")

    grades = bot.get("grades", [])
    if not isinstance(grades, list) or not grades or not all(
        isinstance(grade, str) for grade in grades
    ):
        raise ConfigError("grades must be a list of grade names.")

    timezone = str(bot.get("timezone", "UTC"))
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Invalid timezone: {timezone}") from exc

    return BotConfig(
        token=str(bot.get("token", "")).strip(),
        timezone=timezone,
        authorized_teacher_ids=authorized_ids,
        management_user_ids=management_ids,
        grades=[str(grade) for grade in grades],
        page_size=int(bot.get("page_size", 10)),
        database=DatabaseConfig(
            sqlite_path=str(database.get("sqlite_path", "absence_bot.sqlite3")),
        ),
    )
