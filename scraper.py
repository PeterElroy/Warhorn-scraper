from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


def scrape_rpg_night_sessions():
    """Return a list of session dictionaries scraped from the RPG Night Utrecht agenda.

    Each dictionary contains the following keys:
        - name: the title of the session
        - url: link to the session page on Warhorn
        - date: human-readable date text (e.g. "Wednesday, 4 Mar")
        - location: location string including the venue
        - players: text containing current/total player counts and GM name

    The caller is responsible for further filtering, grouping or formatting.
    """

    url = "https://warhorn.net/events/rpg-night-utrecht/schedule/agenda"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("a[href*='/schedule/sessions/']", timeout=15000)

            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            sessions = []
            card_bodies = soup.find_all('div', class_='card-body')

            for card in card_bodies:
                session_link = card.find('a', href=lambda x: x and '/schedule/sessions/' in x)
                if not session_link:
                    continue

                session_name = session_link.get_text(strip=True)
                session_url = session_link.get('href')

                date_link = card.find('a', href=lambda x: x and '/schedule/2026' in x)
                date_text = date_link.get_text(strip=True) if date_link else None

                location = None
                for div in card.find_all('div'):
                    div_text = div.get_text(strip=True)
                    if '@' in div_text and date_text not in div_text:
                        location = div_text
                        break

                player_info = None
                for elem in card.find_all(string=True):
                    text = elem.strip()
                    if 'of' in text and 'players' in text and 'GM' in text:
                        player_info = text
                        break

                if session_name and date_text and location and player_info:
                    session_url_full = (
                        "https://warhorn.net" + session_url
                        if not session_url.startswith('http')
                        else session_url
                    )
                    sessions.append({
                        'name': session_name,
                        'url': session_url_full,
                        'date': date_text,
                        'location': location,
                        'players': player_info,
                    })

            return sessions
        finally:
            browser.close()
