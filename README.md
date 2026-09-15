# Hermes Watchdog Bot

A lightweight, bulletproof Telegram watchdog bot for monitoring Docker container health and remote server management. Designed to run independently on the host machine to ensure high availability and self-healing for the Hermes AI Agent container.

## Features
- **Container Health Monitoring**: Check Hermes container status (`/status`).
- **Remote Management**: Restart the Hermes Docker container instantly (`/restart`).
- **Log Inspection**: View recent container logs (`/logs`).
- **Bulletproof Error Handling**: Infinite loop with auto-recovery against network interruptions or API drops.
- **Strict Security**: Whitelist access restricted to authorized User IDs only.

## Commands
- `/start` - Show help menu.
- `/status` - Check Hermes Docker container status.
- `/restart` - Restart the Hermes container.
- `/logs` - View the last 20 lines of container logs.

## Setup & Running on Host
1. Clone the repository:
   ```bash
   git clone https://github.com/soriprog/hermes-watchdog.git
   cd hermes-watchdog
   ```
2. Set environment variables (`.env` or export):
   ```env
   WATCHDOG_TOKEN=your_telegram_watchdog_bot_token
   ALLOWED_USER_ID=your_telegram_user_id
   ```
3. Run in the background:
   ```bash
   nohup python3 watchdog.py > watchdog.log 2>&1 &
   ```
