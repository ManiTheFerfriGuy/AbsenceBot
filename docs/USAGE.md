# AbsenceBot Usage Guide

## Summary
AbsenceBot uses inline keyboards only. Teachers never need to type commands besides `/start`.

## Teacher Flow

### 1. Start the Bot
- Send `/start` to the bot.
- Unauthorized users receive a blocked message.

### 2. Main Menu
Options:
- **Manage Students**
- **Record Absence**

### 3. Add Students
1. **Manage Students → Add Students**
2. Select **Grade** → **Major**
3. Send student entries in this strict format:
   ```text
   STUDENT_ID,Full Name
   A1001,Alex Johnson
   A1002,Jamie Lee
   ```
4. The bot confirms how many were added and skipped.

### 4. View Students
1. **Manage Students → View Students**
2. Select **Grade** → **Major**
3. Students are listed with pagination.

### 5. Record Absence
1. **Record Absence**
2. Select **Grade** → **Major**
3. Tap students to toggle their absence.
4. Tap **Confirm Absence** to save.

## Notes
- Duplicate absences for the same student on the same day are prevented.
- If a class has no students, the bot displays a friendly message.
