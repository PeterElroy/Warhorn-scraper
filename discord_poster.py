import sys
import os
import requests

def post_to_discord(message, webhook_url=None):
    """Post the message to Discord using a webhook."""
    if not webhook_url:
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or "https://discord.com/api/webhooks/1480921849381785686/esID1T0ky83CEPv5isqZwjEYtPJLs_r8hC5J89ktlojqjiBmiyyVqc7V39Hbh8HSn6aV"
    if not webhook_url:
        print("No Discord webhook URL provided.")
        return False
    
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Message posted to Discord successfully.")
        return True
    else:
        print(f"Failed to post message: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    # Read message from stdin
    message = sys.stdin.read().strip()
    if message:
        post_to_discord(message)
    else:
        print("No message provided via stdin.")