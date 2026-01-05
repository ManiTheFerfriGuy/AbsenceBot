"""Configuration loader for AbsenceBot."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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


def _parse_csv(value: str) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_int_list(value: str, field_name: str) -> List[int]:
    entries = _parse_csv(value)
    ids: List[int] = []
    for entry in entries:
        try:
            ids.append(int(entry))
        except ValueError as exc:
            raise ConfigError(f"{field_name} must be a comma-separated list of integers.") from exc
    return ids


def load_config() -> BotConfig:
    token = os.getenv("ABSENCEBOT_TOKEN", "").strip()
    timezone = os.getenv("ABSENCEBOT_TIMEZONE", "UTC").strip() or "UTC"
    grades = _parse_csv(os.getenv("ABSENCEBOT_GRADES", ""))
    if not grades:
        raise ConfigError("ABSENCEBOT_GRADES must include at least one grade name.")

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Invalid timezone: {timezone}") from exc

    page_size_raw = os.getenv("ABSENCEBOT_PAGE_SIZE", "10").strip() or "10"
    try:
        page_size = int(page_size_raw)
    except ValueError as exc:
        raise ConfigError("ABSENCEBOT_PAGE_SIZE must be an integer.") from exc

    if page_size <= 0:
        raise ConfigError("ABSENCEBOT_PAGE_SIZE must be greater than zero.")

    return BotConfig(
        token=token,
        timezone=timezone,
        authorized_teacher_ids=_parse_int_list(
            os.getenv("ABSENCEBOT_AUTH_TEACHER_IDS", ""),
            "ABSENCEBOT_AUTH_TEACHER_IDS",
        ),
        management_user_ids=_parse_int_list(
            os.getenv("ABSENCEBOT_MANAGEMENT_USER_IDS", ""),
            "ABSENCEBOT_MANAGEMENT_USER_IDS",
        ),
        grades=grades,
        page_size=page_size,
        database=DatabaseConfig(
            sqlite_path=os.getenv("ABSENCEBOT_DB_PATH", "absence_bot.sqlite3").strip()
            or "absence_bot.sqlite3",
        ),
    )
