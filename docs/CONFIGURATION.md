# AbsenceBot Configuration Guide

## Summary
AbsenceBot is configured entirely through environment variables. There is no config file.

## Required Environment Variables
| Variable | Description | Example |
| --- | --- | --- |
| `ABSENCEBOT_TOKEN` | Telegram bot token from BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |

## Optional Environment Variables
| Variable | Description | Default |
| --- | --- | --- |
| `ABSENCEBOT_AUTH_TEACHER_IDS` | Comma-separated list of Telegram user IDs allowed to use the bot | *(empty)* |
| `ABSENCEBOT_MANAGEMENT_USER_IDS` | Comma-separated list of Telegram user IDs with management access | *(empty)* |
| `ABSENCEBOT_TIMEZONE` | IANA timezone name | `UTC` |
| `ABSENCEBOT_PAGE_SIZE` | Number of students per page in listings | `10` |
| `ABSENCEBOT_DB_PATH` | SQLite database file path | `absence_bot.sqlite3` |

## Notes
- Use commas between values, no brackets.
- Example list: `123456,7891011`.
- If a variable is missing or invalid, the bot will stop with a clear error message.
- Grades are managed inside the bot (Manage Grades) rather than through environment variables.
