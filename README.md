# AbsenceBot

AbsenceBot is a production-ready Telegram bot for managing school absences. It uses inline keyboards for all interactions and supports cPanel deployments.

## Features
- Authorized-teacher access control
- Student roster management by grade and major
- Absence recording with duplicate prevention
- SQLite storage
- Clear documentation and testing report

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the required environment variables:
   ```bash
   export ABSENCEBOT_TOKEN="your-telegram-token"
   ```
3. Run the bot:
   ```bash
   python -m absence_bot
   ```
4. Add grades from the bot's **Manage Grades** menu once it is running.

## Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Usage Guide](docs/USAGE.md)
- [Debugging & Bugs](docs/DEBUGGING.md)
- [Database Schema](docs/database_schema.sql)
- [Testing Report](docs/TESTING_REPORT.md)
- [Scalability Notes](docs/SCALABILITY.md)
- [Technical Blueprint](docs/TECHNICAL_BLUEPRINT.md)
