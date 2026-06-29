# RPG Night Utrecht Scraper

A small Python project that scrapes the Warhorn page for RPG Night Utrecht and
produces a nicely formatted Markdown message suitable for Discord/Warhorn
announcements.

## Files

* `scraper.py` – contains `scrape_rpg_night_sessions()`, the Playwright/BeautifulSoup
  code that fetches and parses session data from the Warhorn agenda.
* `discord_message.py` – generates the formatted Markdown message from scraped data.
* `discord_poster.py` – posts a message to Discord via webhook.

## Usage

To generate and print the message:

```bash
python discord_message.py
```

To generate the message and post to Discord:

```bash
python discord_message.py | python discord_poster.py
```

**Windows users:** Double-click `post_to_discord.bat` to run the full pipeline and post to Discord.

To automatically post to Discord, set the `DISCORD_WEBHOOK_URL` environment variable:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"
python discord_message.py | python discord_poster.py
```

**Note:** The script has a default webhook URL configured. If no environment variable is set, it will use the default webhook. You can override this by setting the `DISCORD_WEBHOOK_URL` environment variable.

or from another script:

```python
from scraper import scrape_rpg_night_sessions
from discord_message import create_warhorn_message, post_to_discord

sessions = scrape_rpg_night_sessions()
message = create_warhorn_message(sessions)
print(message)
post_to_discord(message)
```

## Requirements

* Python 3.11+ (the workspace uses 3.13)
* [Playwright](https://playwright.dev) and a browser driver
* `beautifulsoup4`
* `requests`
* `pytest` (for running tests)

Install dependencies with `pip install -r requirements.txt`.

Note that Playwright may require additional browser installation via `playwright install` after pip installation.

## Notes

This scraper is specific to the HTML structure of the Warhorn schedule page and
may break if the site layout changes. The scraping logic is intentionally
isolated so the message formatting can be reused independently.