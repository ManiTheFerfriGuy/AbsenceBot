"""Legacy entrypoint for running AbsenceBot.

Prefer running the module directly: ``python -m absence_bot``.
"""
from __future__ import annotations

from absence_bot.cli import main


if __name__ == "__main__":
    main()
