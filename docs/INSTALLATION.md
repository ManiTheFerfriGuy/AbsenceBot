# AbsenceBot Installation Guide

## Summary
This guide covers installing AbsenceBot for local development or a cPanel deployment. It includes prerequisites, database setup, configuration, and how to keep the bot running.

## Prerequisites
- **Python:** 3.9+ (3.10+ recommended)
- **Telegram bot token:** Create one via [@BotFather](https://t.me/BotFather)
- **Database:** SQLite (default) or MySQL/MariaDB
- **Server access:** SSH or cPanel terminal for hosted deployments

## Install for Local Development
### 1) Clone the repository
```bash
git clone <repo-url>
cd AbsenceBot
```

### 2) Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Create your config
```bash
cp config.example.toml config.toml
```

### 5) Configure settings
Edit `config.toml` and set:
- `token`: Telegram bot token from BotFather
- `authorized_teacher_ids`: list of Telegram user IDs
- `database`: keep SQLite defaults or provide MySQL credentials

### 6) Run the bot
```bash
python run_bot.py config.toml
```

## Install on cPanel (Command Line Start)
### 1) Upload files
- Download or clone the repository.
- Upload the project to your cPanel home directory (e.g., `~/absencebot`).

### 2) Install dependencies in cPanel
From cPanel Terminal (or SSH):
```bash
cd ~/absencebot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Create the database (MySQL/MariaDB)
Use **MySQL Database Wizard**:
1. Create a database (e.g., `absence_bot`).
2. Create a database user.
3. Grant **ALL PRIVILEGES** for that user on the database.
4. Record **host**, **username**, **password**, and **database name**.

### 4) Configure the bot
```bash
cp config.example.toml config.toml
```
Update `config.toml` with:
- `token`
- `authorized_teacher_ids`
- `grades`
- MySQL connection credentials

### 5) Start the bot (long polling)
Run the bot directly from the terminal:
```bash
cd ~/absencebot
source venv/bin/activate
nohup python run_bot.py config.toml > bot.log 2>&1 &
```

### 6) Verify it is running
```bash
ps -u "$USER" -f | grep run_bot.py
tail -n 50 bot.log
```

### 7) Keep the bot running
If your host does not keep background processes alive, add a cron job that restarts it:
```bash
*/5 * * * * cd /home/<user>/absencebot && ./venv/bin/python run_bot.py config.toml >> /home/<user>/absencebot/bot.log 2>&1
```

## Database Options
### SQLite (default)
- Best for local development or small deployments.
- No external database setup needed.

### MySQL/MariaDB
- Recommended for production.
- Requires credentials configured in `config.toml`.

## Optional: Webhook Mode
If your host supports HTTPS and a persistent Python service:
1. Configure a reverse proxy to expose a webhook endpoint.
2. Enable TLS certificates.
3. Update bot settings to use webhook instead of polling.

## Verification Checklist
- ✅ Bot starts without errors
- ✅ `/start` responds in Telegram
- ✅ Teachers can authenticate
- ✅ Database tables are created and updated

## Troubleshooting
- **Database errors:** verify credentials, host access, and privileges.
- **Unauthorized errors:** ensure teacher IDs are correct.
- **No responses:** confirm the bot is running and the correct token is set.
- **Missing students:** confirm roster entries exist for the chosen grade/major.
