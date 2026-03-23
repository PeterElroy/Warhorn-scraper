import sys
import re

# Use this script with the command python compose_message.py | python discord_to_whatsapp.py

# Ensure stdin and stdout use UTF-8
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def convert_discord_to_whatsapp(text):
    """Convert Discord markdown to WhatsApp format."""
    
    # Replace headers (# Header -> *HEADER IN ALL CAPS*)
    # Match lines starting with # or ## followed by text
    text = re.sub(r'^#+\s*(.+)$', lambda m: f"*{m.group(1).upper()}*", text, flags=re.MULTILINE)
    
    # Bold: **text** -> *text*
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    
    # Italic: *text* -> _text_
    # Be careful not to match bold (**text**) or headers
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'_\1_', text)
    
    # Strikethrough: ~~text~~ -> ~text~
    text = re.sub(r'~~(.*?)~~', r'~\1~', text)
    
    # Code blocks: ```text``` -> ```text``` (WhatsApp supports this)
    # Inline code: `text` -> `text` (WhatsApp supports this)
    # Links: [text](url) -> [text](url) (WhatsApp supports this)
    # Lists: - item -> - item (Already compatible)
    
    return text

if __name__ == "__main__":
    # Read all input from stdin
    input_text = sys.stdin.read()
    
    # Convert and print
    output_text = convert_discord_to_whatsapp(input_text)
    print(output_text)