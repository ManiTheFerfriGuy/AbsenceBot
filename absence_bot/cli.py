"""Command-line entry points for AbsenceBot."""
from __future__ import annotations

import argparse
import os

from absence_bot.bot import run

DEFAULT_CONFIG_PATH = "config.toml"
ENV_CONFIG_PATH = "ABSENCEBOT_CONFIG"


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
