"""Entrypoint for running AbsenceBot locally or on cPanel."""
from __future__ import annotations

import sys

from absence_bot.bot import run


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    run(config_path)


if __name__ == "__main__":
    main()
