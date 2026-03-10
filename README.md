# RPG Night Utrecht Scraper

A small Python project that scrapes the Warhorn page for RPG Night Utrecht and
produces a nicely formatted Markdown message suitable for Discord/Warhorn
announcements.

## Files

* `scraper.py` – contains `scrape_rpg_night_sessions()`, the Playwright/BeautifulSoup
  code that fetches and parses session data from the Warhorn agenda.
* `warhorn_message.py` – imports the scraper and exposes helper functions to
  clean and format the session list into a Markdown message. Can also be run
  directly from the command line to print the message.

## Usage

```bash
python warhorn_message.py
```

or from another script:

```python
from scraper import scrape_rpg_night_sessions
from warhorn_message import create_warhorn_message

sessions = scrape_rpg_night_sessions()
print(create_warhorn_message(sessions))
```

## Requirements

* Python 3.11+ (the workspace uses 3.13)
* [Playwright](https://playwright.dev) and a browser driver
* `beautifulsoup4`
* `pytest` (for running tests)

Install dependencies with `pip install -r requirements.txt`.

Note that Playwright may require additional browser installation via `playwright install` after pip installation.

## Notes

This scraper is specific to the HTML structure of the Warhorn schedule page and
may break if the site layout changes. The scraping logic is intentionally
isolated so the message formatting can be reused independently.