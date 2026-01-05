# AbsenceBot Configuration

## Summary
All settings live in `config.toml`. Copy from `config.example.toml` and edit.

## Add/Remove Teacher IDs
- Update the list under `bot.authorized_teacher_ids`.
- Example:
  ```toml
  authorized_teacher_ids = [123456789, 555555555]
  ```
 - You can also add teacher IDs from the bot's **Management Tools** menu.

## Management Access
- Add admin user IDs under `bot.management_user_ids`.
- Example:
  ```toml
  management_user_ids = [111111111]
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
- SQLite database path:
  ```toml
  [database]
  sqlite_path = "absence_bot.sqlite3"
  ```

## Reset the Database
⚠️ This deletes all student and absence records.

1. Stop the bot.
2. Drop the tables or delete the SQLite file.
3. Restart the bot to recreate tables.
