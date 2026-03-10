from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import defaultdict
import re
from datetime import datetime
import sys

# ensure UTF-8 output for emoji
sys.stdout.reconfigure(encoding='utf-8')

def scrape_rpg_night_sessions():
    """
    Scrape RPG Night Utrecht event page and display first upcoming date's sessions,
    grouped by location with available player seats.
    """
    url = "https://warhorn.net/events/rpg-night-utrecht/schedule/agenda"
    
    print("Initializing Playwright browser...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"Loading page: {url}")
            page.goto(url, wait_until="networkidle")
            
            print("Waiting for content to load...")
            # Wait for session links to appear
            page.wait_for_selector("a[href*='/schedule/sessions/']", timeout=15000)
            
            print("Content loaded! Parsing...")
            
            # Get the rendered HTML
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all session data
            sessions = []
            
            # Find all card bodies (each contains session info and player count)
            card_bodies = soup.find_all('div', class_='card-body')
            
            print(f"Found {len(card_bodies)} card bodies")
            
            for card in card_bodies:
                # Extract session info from the card
                session_link = card.find('a', href=lambda x: x and '/schedule/sessions/' in x)
                if not session_link:
                    continue
                
                session_name = session_link.get_text(strip=True)
                session_url = session_link.get('href')
                
                # Find date - look for the date link
                date_link = card.find('a', href=lambda x: x and '/schedule/2026' in x)
                date_text = None
                if date_link:
                    date_text = date_link.get_text(strip=True)
                
                # Find location - look for the div with @  
                location = None
                for div in card.find_all('div'):
                    div_text = div.get_text(strip=True)
                    if '@' in div_text and not date_text in div_text:
                        location = div_text
                        break
                
                # Find player info - look for text with "of" and "players"
                player_info = None
                player_text_nodes = []
                for elem in card.find_all(string=True):
                    text = elem.strip()
                    if 'of' in text and 'players' in text and 'GM' in text:
                        player_info = text
                        break
                
                if session_name and date_text and location and player_info:
                    session_url_full = "https://warhorn.net" + session_url if not session_url.startswith('http') else session_url
                    sessions.append({
                        'name': session_name,
                        'url': session_url_full,
                        'date': date_text,
                        'location': location,
                        'players': player_info
                    })
            
            print(f"Successfully parsed {len(sessions)} sessions\n")
            
            if not sessions:
                print("No sessions found.")
                return
            
            # Find the first upcoming date
            unique_dates = []
            for session in sessions:
                # Extract just the date part (e.g., "Wednesday, 4 Mar")
                date_match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', session['date'])
                if date_match:
                    date_simple = date_match.group(0)
                else:
                    date_simple = session['date']
                
                if date_simple not in unique_dates:
                    unique_dates.append(date_simple)
            
            if not unique_dates:
                print("No dates found.")
                return
            
            first_date = unique_dates[0]
            
            # Filter sessions for the first upcoming date
            first_date_sessions = [s for s in sessions if first_date in s['date']]
            
            # Group by location
            by_location = defaultdict(list)
            for session in first_date_sessions:
                by_location[session['location']].append(session)
            
            # Calculate available seats
            def get_available_seats(player_info):
                """Extract available seats from player info like '6 of 6 players'"""
                try:
                    # Look for "X of Y players" pattern
                    match = re.search(r'(\d+)\s+of\s+(\d+)\s+players', player_info)
                    if match:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        return total - current
                except (ValueError, AttributeError):
                    pass
                return None
            
            def clean_session_name(name):
                """Remove 'Indie RPG - ' prefix from session name"""
                if name.startswith('Indie RPG - '):
                    return name[12:]  # Remove 'Indie RPG - ' (12 characters)
                return name
            
            def clean_location(location):
                """Remove 'Subcultures @' prefix from location"""
                if location.startswith('Subcultures @'):
                    return location[13:]  # Remove 'Subcultures @' (13 characters)
                return location
            
            # Display results in Markdown format for Discord
            agenda_url = "https://warhorn.net/events/rpg-night-utrecht/schedule/agenda"
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            print(f"\n# RPG Night Utrecht - {first_date}\n")
            print(f"*Last checked {now_str}*\n")
            print("Great games for @everyone! Looking for a different game? Let us know in #⁠🍺-rpg-night-tavern and perhaps a GM will pick it up!\n")
            first_loc = True
            for location in sorted(by_location.keys()):
                clean_loc = clean_location(location)
                if not first_loc:
                    print()
                first_loc = False
                print(f"## 📍 {clean_loc}\n")
                
                # Sort sessions by available seats (high to low)
                sorted_sessions = sorted(
                    by_location[location],
                    key=lambda s: (get_available_seats(s['players']) is None, 
                                   -(get_available_seats(s['players']) or -1))
                )
                
                for session in sorted_sessions:
                    clean_name = clean_session_name(session['name'])
                    available = get_available_seats(session['players'])
                    
                    if available is not None:
                        if available == 0:
                            seat_text = "**FULL**"
                            line = f"- {clean_name} — {seat_text}"
                        else:
                            seat_text = f"**{available} seat{'s' if available != 1 else ''} available**"
                            line = f"- [{clean_name}]({session['url']}) — {seat_text}"
                    else:
                        seat_text = f"**{session['players']}**"
                        line = f"- [{clean_name}]({session['url']}) — {seat_text}"
                    
                    print(line)
                # end sessions loop
            # append footer message
            print()
            print("Find our all upcoming games here: https://warhorn.net/events/rpg-night-utrecht/schedule/agenda")        
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_rpg_night_sessions()
