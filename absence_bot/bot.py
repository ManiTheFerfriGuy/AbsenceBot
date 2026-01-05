"""Main application setup for AbsenceBot."""
from __future__ import annotations

import argparse
import logging
import os
from datetime import timedelta
from pathlib import Path

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from absence_bot.config import ConfigError, load_config
from absence_bot.database import create_database, seed_grades
from absence_bot.handlers import (
    HandlerContext,
    handle_callback,
    handle_message,
    scheduled_database_export,
    start,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config.toml"
ENV_CONFIG_PATH = "ABSENCEBOT_CONFIG"


def build_application(config_path: str | Path) -> Application:
    config = load_config(config_path)
    if not config.token:
        raise ConfigError("Bot token missing in config.")

    try:
        database = create_database(config.database)
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Database connection failed: %s", exc)
        raise ConfigError("Unable to connect to the database.") from exc
    application = Application.builder().token(config.token).build()

    application.bot_data["handler_context"] = HandlerContext(config=config, database=database)
    seed_grades(database, config.grades)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    if application.job_queue is None:
        LOGGER.warning(
            "Job queue unavailable; scheduled database exports are disabled. "
            "Install python-telegram-bot[job-queue] to enable them."
        )
    else:
        application.job_queue.run_repeating(
            scheduled_database_export,
            interval=timedelta(hours=12),
            first=timedelta(hours=12),
            name="automatic-database-export",
        )

    return application


def run(config_path: str | Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )
    LOGGER.info("Loading configuration from %s", config_path)
    application = build_application(config_path)
    LOGGER.info("Starting AbsenceBot")
    application.run_polling()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AbsenceBot with the provided config.")
    parser.add_argument(
        "config",
        nargs="?",
        default=os.getenv(ENV_CONFIG_PATH, DEFAULT_CONFIG_PATH),
        help=(
            "Path to the config TOML file. Defaults to config.toml or the "
            "ABSENCEBOT_CONFIG environment variable."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
