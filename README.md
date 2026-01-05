# AbsenceBot

AbsenceBot is a production-ready Telegram bot for managing school absences. It uses inline keyboards for all interactions and supports cPanel deployments.

## Features
- Authorized-teacher access control
- Student roster management by grade and major
- Absence recording with duplicate prevention
- SQLite storage
- Clear documentation and testing report

## Quick Start
1. Copy the config template:
   ```bash
   cp config.example.toml config.toml
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py config.toml
   ```

## Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Usage Guide](docs/USAGE.md)
- [Database Schema](docs/database_schema.sql)
- [Testing Report](docs/TESTING_REPORT.md)
- [Scalability Notes](docs/SCALABILITY.md)
- [Technical Blueprint](docs/TECHNICAL_BLUEPRINT.md)
