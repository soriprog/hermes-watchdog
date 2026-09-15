import os
import time
import subprocess
import urllib.request
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment
TELEGRAM_TOKEN = os.getenv("WATCHDOG_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
POLL_INTERVAL = 5

def send_telegram_message(chat_id, text):
    """Send a message back to the user via Telegram Bot API."""
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Error sending message: {e}")

def run_shell_command(cmd):
    """Execute a local shell command securely with a timeout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error executing command: {str(e)}"

def poll_updates():
    """Long-polling loop for receiving Telegram commands and executing management tasks."""
    if not TELEGRAM_TOKEN:
        print("Error: WATCHDOG_TOKEN not set in environment.")
        return
    offset = 0
    print("Watchdog bot started successfully on host...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if result.get("ok"):
                    for update in result.get("result", []):
                        offset = update["update_id"] + 1
                        message = update.get("message")
                        if not message:
                            continue
                            
                        user_id = message["from"]["id"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "").strip()
                        
                        # Authorize user
                        if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
                            send_telegram_message(chat_id, "Unauthorized access.")
                            continue
                            
                        if text == "/status":
                            status = run_shell_command("docker inspect -f '{{.State.Status}}' hermes 2>&1")
                            send_telegram_message(chat_id, f"Hermes container status: {status}")
                            
                        elif text == "/restart":
                            send_telegram_message(chat_id, "Restarting Hermes container...")
                            output = run_shell_command("sudo docker restart hermes")
                            send_telegram_message(chat_id, f"Hermes restarted!\nOutput: {output}")
                            
                        elif text == "/logs":
                            logs = run_shell_command("docker logs --tail 20 hermes")
                            send_telegram_message(chat_id, f"Recent Hermes container logs:\n<code>{logs}</code>")
                            
                        elif text == "/start":
                            reply = (
                                "Hello! I am the Hermes Watchdog bot 🛡️\n\n"
                                "Available commands:\n"
                                "/status - Check container health\n"
                                "/restart - Restart Hermes container\n"
                                "/logs - View recent logs"
                            )
                            send_telegram_message(chat_id, reply)
                            
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    poll_updates()
