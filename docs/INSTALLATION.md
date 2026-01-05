# AbsenceBot Installation Guide

## Summary
This guide walks you through a simple, step-by-step install for local machines or cPanel hosting. AbsenceBot uses **environment variables only** (no config file).

## Before You Start (Get These Ready)
1. **Telegram bot token** from [@BotFather](https://t.me/BotFather).
2. **Your Telegram user ID(s)** for teachers and managers (use @userinfobot in Telegram to get IDs).
3. A server or local machine with **Python 3.9+**.

---

## Option A: Local Install (Fastest Way to Test)

### Step 1: Download the project
```bash
git clone <repo-url>
cd AbsenceBot
```

### Step 2: Install Python packages
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Set your environment variables
```bash
export ABSENCEBOT_TOKEN="your-telegram-token"
export ABSENCEBOT_GRADES="Grade 10,Grade 11"
export ABSENCEBOT_MANAGEMENT_USER_IDS="123456789"
export ABSENCEBOT_AUTH_TEACHER_IDS="123456789,987654321"
```

### Step 4: Start the bot
```bash
python -m absence_bot
```

### Step 5: Check it
- Open Telegram and send `/start` to your bot.
- If you see the menu, the install worked.

---

## Option B: cPanel Install (No Terminal Experience Required)

### Step 1: Upload the files
1. Log into **cPanel**.
2. Open **File Manager**.
3. Click **Upload** and upload the project ZIP.
4. Extract it so you get a folder like `/home/<user>/absencebot`.

### Step 2: Create the Python app
1. In cPanel, open **Setup Python App**.
2. Click **Create Application**.
3. Use these settings:
   - **Python version:** 3.9 or newer
   - **Application root:** `/home/<user>/absencebot`
   - **Application startup file:** `absence_bot/__main__.py`
   - **Application entry point:** `main`
4. Click **Create**.

### Step 3: Install dependencies
1. Inside **Setup Python App**, click **Open** next to the virtual environment.
2. Run:
   ```bash
   pip install -r /home/<user>/absencebot/requirements.txt
   ```

### Step 4: Add environment variables (no config file)
In **Setup Python App**, scroll to **Environment variables** and add:
- `ABSENCEBOT_TOKEN` = your Telegram bot token
- `ABSENCEBOT_GRADES` = `Grade 10,Grade 11`
- `ABSENCEBOT_MANAGEMENT_USER_IDS` = `123456789`
- `ABSENCEBOT_AUTH_TEACHER_IDS` = `123456789,987654321`

Optional:
- `ABSENCEBOT_TIMEZONE` = `UTC`
- `ABSENCEBOT_PAGE_SIZE` = `10`
- `ABSENCEBOT_DB_PATH` = `/home/<user>/absencebot/absence_bot.sqlite3`

### Step 5: Restart the app
- Click **Restart** in **Setup Python App**.

### Step 6: Confirm the bot works
- Send `/start` in Telegram and confirm the menu appears.

---

## Option C: cPanel Install (Terminal + Long-Running Process)
Use this if you prefer terminal commands and want the bot running continuously.

### Step 1: Install dependencies
```bash
cd /home/<user>/absencebot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Set environment variables
```bash
export ABSENCEBOT_TOKEN="your-telegram-token"
export ABSENCEBOT_GRADES="Grade 10,Grade 11"
export ABSENCEBOT_MANAGEMENT_USER_IDS="123456789"
export ABSENCEBOT_AUTH_TEACHER_IDS="123456789,987654321"
```

### Step 3: Start the bot in the background
```bash
nohup /home/<user>/absencebot/venv/bin/python -m absence_bot > /home/<user>/absencebot/bot.log 2>&1 &
```

### Step 4: Verify it is running
```bash
ps -u "$USER" -f | grep absence_bot
tail -n 50 /home/<user>/absencebot/bot.log
```

### Step 5: Keep it running (optional cron fallback)
If your host stops background jobs, add a cron job:
```bash
*/5 * * * * /home/<user>/absencebot/venv/bin/python -m absence_bot >> /home/<user>/absencebot/bot.log 2>&1
```

---

## Database Notes
- AbsenceBot uses SQLite by default. The database file is `absence_bot.sqlite3`.
- To move it, set `ABSENCEBOT_DB_PATH` to a full path.

## Verification Checklist
- ✅ Bot starts without errors
- ✅ `/start` responds in Telegram
- ✅ Teachers can authenticate
- ✅ Database tables are created and updated
