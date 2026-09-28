from playwright.sync_api import sync_playwright
import re
from urllib.parse import urljoin


URL = "https://warhorn.net/events/rpg-night-utrecht/schedule/agenda"
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "]+"
)


def clean(text):
    """Normalize whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def parse_count(text, kind):
    """
    Extract a count such as:
        1 of 1 GM
        6 of 6 players

    Returns (current, total), or (None, None) if not found.
    """
    pattern = rf"(\d+)\s+of\s+(\d+)\s+{kind}s?"
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None, None

    return int(match.group(1)), int(match.group(2))


def scrape_sessions():
    print("[status] Starting browser.", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print(f"[status] Loading {URL}.", flush=True)
        page.goto(URL, wait_until="networkidle")

        # Allow any remaining client-side rendering to finish.
        print("[status] Waiting for page rendering to finish.", flush=True)
        page.wait_for_timeout(1000)

        # ---------------------------------------------------------
        # Every Warhorn session card has:
        #
        #     <div data-listing="..." class="... card">
        #
        # This is our structural anchor.
        # ---------------------------------------------------------
        cards = page.locator('div[data-listing].card')
        card_count = cards.count()
        print(f"[status] Found {card_count} session cards.", flush=True)

        sessions = []
        target_date = None

        for i in range(card_count):
            card = cards.nth(i)

            # -----------------------------------------------------
            # Date and time
            #
            # The date is the link whose href points to:
            # /schedule/YYYY/MM/DD#session-...
            # -----------------------------------------------------
            date_link = card.locator(
                'a[href*="/schedule/20"][href*="#session-"]'
            ).first

            if date_link.count() == 0:
                print(
                    f"[status] Skipping card {i + 1}: no date found.",
                    flush=True,
                )
                continue

            date = clean(date_link.inner_text())

            if target_date is None:
                target_date = date
                print(
                    f"[status] Parsing cards for date: {target_date}.",
                    flush=True,
                )
            elif date != target_date:
                print(
                    f"[status] Reached later date ({date}); stopping.",
                    flush=True,
                )
                break

            # The date/time container also contains the time:
            #
            # Wednesday, 23 Sep 7-10pm (GMT+02)
            #
            # Get the parent div's complete text.
            date_time = clean(
                date_link.locator("..").inner_text()
            )

            # -----------------------------------------------------
            # Session title
            #
            # The session title has a href containing:
            # /schedule/sessions/
            # -----------------------------------------------------
            title_link = card.locator(
                'a[href*="/schedule/sessions/"]'
            ).first
            has_title = title_link.count() > 0

            title = (
                clean(title_link.inner_text())
                if has_title
                else None
            )
            session_url = (
                urljoin(URL, title_link.get_attribute("href"))
                if has_title
                else None
            )

            # -----------------------------------------------------
            # Location
            #
            # The card structure is:
            #
            # <div>
            #     <div class="text-nowrap ...">
            #         DATE
            #     </div>
            #
            #     <div class="h5 mb-0">
            #         SESSION TITLE
            #     </div>
            #
            #     <div>
            #         LOCATION
            #     </div>
            # </div>
            #
            # We therefore find the title's parent and take its
            # following sibling.
            # -----------------------------------------------------
            location = None

            if has_title:
                title_container = title_link.locator("..")

                location_element = title_container.locator(
                    "xpath=following-sibling::div[1]"
                )

                if location_element.count():
                    location = clean(
                        location_element.inner_text()
                    )

            # -----------------------------------------------------
            # Language
            #
            # The language is represented by a badge-secondary.
            # -----------------------------------------------------
            language_element = card.locator(
                ".badge.badge-secondary"
            ).first

            language = (
                clean(language_element.inner_text())
                if language_element.count()
                else None
            )

            # -----------------------------------------------------
            # Full status
            #
            # "Full" is inside the warning badge.
            # -----------------------------------------------------
            full_element = card.locator(
                ".badge.badge-warning"
            ).first

            full = False

            if full_element.count():
                full = bool(
                    re.search(
                        r"\bFull\b",
                        full_element.inner_text(),
                        re.IGNORECASE,
                    )
                )

            # -----------------------------------------------------
            # Scenario thumbnail
            # -----------------------------------------------------
            image = card.locator(
                'img[alt]'
            ).first

            scenario_thumbnail = None
            scenario_thumbnail_alt = None

            if image.count():
                scenario_thumbnail = image.get_attribute("src")
                scenario_thumbnail_alt = image.get_attribute("alt")

            # -----------------------------------------------------
            # Scenario title
            #
            # In the supplied HTML this is the <h6>.
            # -----------------------------------------------------
            scenario_element = card.locator("h6").first

            scenario_title = (
                clean(scenario_element.inner_text())
                if scenario_element.count()
                else None
            )

            # -----------------------------------------------------
            # Game title/system
            #
            # The game system is linked through:
            # /game-systems/...
            # -----------------------------------------------------
            game_element = card.locator(
                'a[href*="/game-systems/"]'
            ).first

            game_title = (
                clean(game_element.inner_text())
                if game_element.count()
                else None
            )

            # -----------------------------------------------------
            # GM and player counts
            #
            # The supplied structure contains:
            #
            # <div class="align-items-center d-flex text-muted">
            #     1 of 1 GM • 6 of 6 players
            # </div>
            #
            # Locate it structurally rather than searching the
            # entire card's text.
            # -----------------------------------------------------
            counts_element = card.locator(
                "div.align-items-center.d-flex.text-muted"
            ).first

            counts_text = (
                clean(counts_element.inner_text())
                if counts_element.count()
                else ""
            )

            current_gms, total_gms = parse_count(
                counts_text,
                "GM",
            )

            current_players, total_players = parse_count(
                counts_text,
                "player",
            )

            # -----------------------------------------------------
            # Difference between current and total players.
            #
            # Example:
            #     4 of 6 players -> 2
            # -----------------------------------------------------
            player_difference = None

            if (
                current_players is not None
                and total_players is not None
            ):
                player_difference = (
                    total_players - current_players
                )

            sessions.append(
                {
                    "date": date,
                    "date_time": date_time,
                    "language": language,
                    "title": title,
                    "session_url": session_url,
                    "location": location,
                    "full": full,
                    "scenario_thumbnail": scenario_thumbnail,
                    "scenario_thumbnail_alt": scenario_thumbnail_alt,
                    "scenario_title": scenario_title,
                    "game_title": game_title,
                    "current_gms": current_gms,
                    "total_gms": total_gms,
                    "current_players": current_players,
                    "total_players": total_players,
                    "player_difference": player_difference,
                }
            )

            print(
                f"[status] Parsed card {i + 1}/{card_count}: {title}.",
                flush=True,
            )

        print("[status] Closing browser.", flush=True)
        browser.close()

    print(f"[status] Parsed {len(sessions)} sessions.", flush=True)
    return sessions


def clean_sessions(sessions):
    """Normalize locations and remove emojis from session titles."""
    for session in sessions:
        if session["location"]:
            session["location"] = re.sub(
                r"^Subcultures\s*@\s*",
                "",
                session["location"],
                flags=re.IGNORECASE,
            ).strip()

        if session["title"]:
            session["title"] = clean(
                EMOJI_PATTERN.sub("", session["title"])
            )

    return sessions


def main():
    print("[status] Scraping sessions.", flush=True)
    sessions = scrape_sessions()
    print("[status] Cleaning session locations and titles.", flush=True)
    sessions = clean_sessions(sessions)

    if not sessions:
        print("No session cards found.")
        return

    # -------------------------------------------------------------
    # 1. Sort cards by available player spaces, then location.
    #
    # Higher player differences come first. casefold() makes the
    # location sort case-insensitive. Cards without a location or
    # player difference go last within their respective sort keys.
    # -------------------------------------------------------------
    sessions.sort(
        key=lambda session: (
            -session["player_difference"]
            if session["player_difference"] is not None
            else float("inf"),
            session["location"] is None,
            (session["location"] or "").casefold(),
        )
    )
    print("[status] Sorted sessions by player difference and location.", flush=True)

    # -------------------------------------------------------------
    # 2. Print Markdown grouped by location.
    # -------------------------------------------------------------
    print("[status] Printing session results.", flush=True)
    header_date = re.sub(
        r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
        r"January|February|March|April|May|June|July|August|September|"
        r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|"
        r"Sept|Oct|Nov|Dec)\b",
        lambda match: match.group(0).capitalize(),
        sessions[0]["date"],
        flags=re.IGNORECASE,
    )
    print()
    print("--- Discord version ---")
    print(f"# RPG Night Utrecht - {header_date}")
    print("Games for @everyone. All levels of experience welcome. Session full? Join the waitlist or request another session.")
    print()
    sessions_by_location = {}

    for session in sessions:
        location = session["location"] or "Unknown location"
        sessions_by_location.setdefault(location, []).append(session)

    for location, location_sessions in sessions_by_location.items():
        print(f"### 📍 {location}")

        for session in location_sessions:
            title = session["title"] or "Untitled session"
            difference = session["player_difference"]

            if difference == 0:
                availability = "FULL"
            else:
                availability = f"{difference} spots left"
                if session["session_url"]:
                    title = f"[{title}]({session['session_url']})"

            print(f"- {title} — {availability}")

    print()
    print("--- WhatsApp version ---")
    print(f"*RPG Night Utrecht - {header_date}*")
    print(
        "Games for everyone. All levels of experience welcome. Session full? "
        "Join the waitlist or request another session."
    )
    print()

    for location, location_sessions in sessions_by_location.items():
        print(f"*📍 {location}*")

        for session in location_sessions:
            title = session["title"] or "Untitled session"
            difference = session["player_difference"]
            availability = (
                "FULL" if difference == 0 else f"{difference} spots left"
            )
            print(f"• {title} — {availability}")

        print()

    print(f"Agenda: {URL}")


if __name__ == "__main__":
    main()