import sys
import re
import os
import tempfile
from collections import defaultdict
from datetime import datetime

# when running from the command line we want emoji to work
sys.stdout.reconfigure(encoding='utf-8')

from scrape_sessions import scrape_sessions

def get_available_seats(player_info):
    """Extract available seats from player info like '6 of 6 players'.

    If `player_info` is falsy or not a string, return ``None`` rather than
    raising an exception.
    """
    if not player_info:
        return None
    try:
        match = re.search(r"(\d+)\s+of\s+(\d+)\s+players", player_info)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            return total - current
    except (ValueError, AttributeError):
        pass
    return None


def clean_session_name(name):
    """Remove common site prefixes from session titles."""
    if name.startswith('Indie RPG - '):
        return name[12:]
    return name


def clean_location(location):
    """Trim the venue prefix from location strings.

    Always strip the result to remove any leading/trailing whitespace that may
    have been introduced during slicing.
    """
    if location.startswith('Subcultures @'):
        return location[13:].strip()
    return location


def compose_message(sessions):
    """Given a list of session dicts, return the formatted Markdown message."""
    if not sessions:
        return "No sessions found."

    # determine first upcoming date
    unique_dates = []
    for session in sessions:
        date_match = re.search(
            r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            session['date'],
        )
        date_simple = date_match.group(0) if date_match else session['date']
        if date_simple not in unique_dates:
            unique_dates.append(date_simple)

    first_date = unique_dates[0] if unique_dates else None
    if not first_date:
        return "No dates found."

    # filter and group
    first_date_sessions = [s for s in sessions if first_date in s['date']]
    by_location = defaultdict(list)
    for s in first_date_sessions:
        by_location[s['location']].append(s)

    lines = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines.append(f"# RPG Night Utrecht - {first_date}")
    lines.append("")
    lines.append(f"*Last checked {now_str}*")
    lines.append("")
    lines.append(
        "Great games for @everyone! Looking for a different game? Let us know in #⁠rpg-night-tavern and a GM might pick it up!"
    )
    lines.append("")

    first_loc = True
    for location in sorted(by_location.keys()):
        clean_loc = clean_location(location)
        if not first_loc:
            lines.append("")
        first_loc = False
        lines.append(f"## 📍 {clean_loc}")
        lines.append("")

        sorted_sessions = sorted(
            by_location[location],
            key=lambda s: (
                get_available_seats(s['players']) is None,
                -(get_available_seats(s['players']) or -1),
            ),
        )

        for session in sorted_sessions:
            clean_name = clean_session_name(session['name'])
            available = get_available_seats(session['players'])
            if available is not None:
                if available == 0:
                    line = f"- {clean_name} — **FULL**"
                else:
                    line = (
                        f"- [{clean_name}]({session['url']}) — **{available} seat{'s' if available != 1 else ''} available**"
                    )
            else:
                line = (
                    f"- [{clean_name}]({session['url']}) — **{session['players']}**"
                )
            lines.append(line)

    lines.append("")
    lines.append(
        " [Find our latest upcoming games here.](https://warhorn.net/events/rpg-night-utrecht/schedule/agenda)"
    )
    return "\n".join(lines)

if __name__ == "__main__":
    print("Starting script...", file=sys.stderr)  # Debug output to stderr
    sessions = scrape_sessions()
    message = compose_message(sessions)
    
    # Print message to terminal
    print(message)
    
    # If output is being piped, also write to temp file and print path
    if not sys.stdout.isatty():
        # Write message to a temporary file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write(message)
            temp_file = f.name
        
        # Print the temp file path so it can be read by discord_poster.py
        print(temp_file)