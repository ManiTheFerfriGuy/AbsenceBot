# AbsenceBot Installation (cPanel)

## Summary
This guide explains how to deploy AbsenceBot on cPanel with MySQL and long polling.

## 1. Upload Files
1. Download or clone the repository.
2. Upload the project files to your cPanel home directory (e.g., `~/absencebot`).

## 2. Create Python App (cPanel)
1. Open **Setup Python App** in cPanel.
2. Create a new app:
   - **Python version:** 3.9+ (match your hosting).
   - **Application root:** `/home/<user>/absencebot`
   - **Startup file:** `run_bot.py`

## 3. Install Dependencies
From the cPanel terminal (or SSH):
```bash
cd ~/absencebot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Create the Database (MySQL)
1. Open **MySQL Database Wizard**.
2. Create a database (e.g., `absence_bot`).
3. Create a database user and grant **ALL PRIVILEGES**.
4. Note host, username, password, and database name.

## 5. Configure the Bot
1. Copy the example config:
```bash
cp config.example.toml config.toml
```
2. Edit `config.toml`:
   - Set `token` to your Telegram bot token.
   - Add all authorized teacher Telegram user IDs.
   - Configure MySQL credentials.

## 6. Start the Bot (Long Polling)
With the virtualenv active:
```bash
python run_bot.py config.toml
```

For production, use a **cron job** or **process manager** (if provided by your cPanel host) to keep the bot running.

## Optional: Webhook Setup
If your host supports HTTPS and a persistent Python service:
- Configure a reverse proxy to expose a webhook endpoint.
- Ensure TLS is enabled.

---

## Troubleshooting
- **Database errors:** verify credentials and firewall access.
- **Unauthorized errors:** confirm teacher IDs are correct.
- **Missing students:** ensure you added students to the selected grade/major.
