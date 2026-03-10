import sys
import os
import requests

# Ensure stdin and stdout use UTF-8
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def post_to_discord(message, webhook_url=None):
    """Post the message to Discord using a webhook."""
    if not webhook_url:
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or "https://discord.com/api/webhooks/1480921849381785686/esID1T0ky83CEPv5isqZwjEYtPJLs_r8hC5J89ktlojqjiBmiyyVqc7V39Hbh8HSn6aV"
    if not webhook_url:
        print("No Discord webhook URL provided.")
        return False
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    data = {"content": message}
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code == 204:
        print("Message posted to Discord successfully.")
        return True
    else:
        print(f"Failed to post message: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    # Read all input from stdin
    input_lines = sys.stdin.read().strip().split('\n')
    
    # The last line should be the temp file path
    if input_lines:
        file_path = input_lines[-1].strip()
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    message = f.read().strip()
                
                # Clean up temp file
                os.unlink(file_path)
                
                if message:
                    post_to_discord(message)
                else:
                    print("Message file was empty.")
            except Exception as e:
                print(f"Error reading message file: {e}")
        else:
            print("No valid file path found in input.")
    else:
        print("No input provided via stdin.")