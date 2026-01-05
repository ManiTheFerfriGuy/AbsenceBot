# Debugging & Common Bugs

Use this guide if the bot does not start or does not respond. Each issue includes a clear fix.

## 1) Bot starts but does not respond in Telegram
**Symptoms**
- The process is running, but `/start` gets no reply.

**Fix**
1. Confirm the token is correct:
   - Re-copy `ABSENCEBOT_TOKEN` from BotFather.
2. Restart the bot after updating the token.
3. Check logs for auth errors:
   ```bash
   tail -n 100 bot.log
   ```

---

## 2) “ABSENCEBOT_TOKEN is missing” error
**Symptoms**
- Bot exits immediately with a missing token error.

**Fix**
1. Set the environment variable:
   ```bash
   export ABSENCEBOT_TOKEN="your-telegram-token"
   ```
2. Restart the bot.

---

## 3) No grades appear in the bot
**Symptoms**
- Grade list is empty.

**Fix**
1. Open **Manage Grades** from the bot menu.
2. Add the grade names you need.

---

## 4) Invalid timezone error
**Symptoms**
- Error like: `Invalid timezone: XYZ`.

**Fix**
1. Use a valid IANA timezone, for example:
   ```bash
   export ABSENCEBOT_TIMEZONE="America/New_York"
   ```
2. Restart the bot.

---

## 5) Database permission or “unable to open database file”
**Symptoms**
- Bot fails on startup with database errors.

**Fix**
1. Check write permissions to the database directory.
2. Use a full path you can write to:
   ```bash
   export ABSENCEBOT_DB_PATH="/home/<user>/absencebot/absence_bot.sqlite3"
   ```
3. Restart the bot.

---

## 6) “ABSENCEBOT_PAGE_SIZE must be an integer”
**Symptoms**
- Startup failure after setting page size.

**Fix**
1. Use a whole number:
   ```bash
   export ABSENCEBOT_PAGE_SIZE="10"
   ```
2. Restart the bot.

---

## 7) “Job queue unavailable” warning
**Symptoms**
- Warning logged during startup.

**Fix**
- This is safe to ignore if you do not need scheduled exports.
- To enable it, install the job queue extra:
  ```bash
  pip install "python-telegram-bot[job-queue]"
  ```

---

## 8) cPanel app won’t start
**Symptoms**
- cPanel shows the app stopped or instantly restarts.

**Fix**
1. Confirm the **startup file** is `absence_bot/__main__.py`.
2. Confirm the **entry point** is `main`.
3. Reinstall dependencies:
   ```bash
   pip install -r /home/<user>/absencebot/requirements.txt
   ```
4. Re-check environment variables in **Setup Python App**.

---

## 9) Teachers are blocked as “Unauthorized”
**Symptoms**
- A teacher gets an access denied message.

**Fix**
1. Add their Telegram user ID to `ABSENCEBOT_AUTH_TEACHER_IDS` or `ABSENCEBOT_MANAGEMENT_USER_IDS`.
2. Use commas between IDs:
   ```bash
   export ABSENCEBOT_AUTH_TEACHER_IDS="123456789,987654321"
   ```
3. Restart the bot.

---

## 10) SQLite database is locked
**Symptoms**
- Errors about “database is locked.”

**Fix**
1. Make sure only one bot process is running:
   ```bash
   ps -u "$USER" -f | grep absence_bot
   ```
2. Stop extra processes, then start one clean instance.

---

## 11) cPanel cron restarts repeatedly
**Symptoms**
- Multiple bot instances, high CPU, or duplicate logs.

**Fix**
1. Use only one start method:
   - **Either** Setup Python App **or** cron/terminal, not both.
2. Remove duplicate cron entries.

---
