# AbsenceBot Configuration

## Summary
All settings live in `config.toml`. Copy from `config.example.toml` and edit.

## Add/Remove Teacher IDs
- Update the list under `bot.authorized_teacher_ids`.
- Example:
  ```toml
  authorized_teacher_ids = [123456789, 555555555]
  ```

## Change Grades
- Update `bot.grades`:
  ```toml
  grades = ["10th Grade", "11th Grade", "12th Grade"]
  ```

## Manage Majors
- Majors are managed inside the bot UI.
- Use **Manage Students → Manage Majors** to add or remove majors per grade.

## Database Settings
- For MySQL:
  ```toml
  [database]
  engine = "mysql"
  host = "localhost"
  port = 3306
  name = "absence_bot"
  user = "absence_bot"
  password = "YOUR_PASSWORD"
  ```
- For SQLite (development):
  ```toml
  [database]
  engine = "sqlite"
  sqlite_path = "absence_bot.sqlite3"
  ```

## Reset the Database
⚠️ This deletes all student and absence records.

1. Stop the bot.
2. Drop the tables or delete the SQLite file.
3. Restart the bot to recreate tables.
