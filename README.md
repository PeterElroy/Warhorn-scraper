# RPG Night Utrecht Warhorn Scraper

A small Python scraper for the [RPG Night Utrecht Warhorn agenda](https://warhorn.net/events/rpg-night-utrecht/schedule/agenda). It collects the sessions listed for the first date on the agenda and prints two ready-to-share message formats:

- **Discord:** Markdown headings, links on session titles, and availability counts.
- **WhatsApp:** Bold event and location headings, a plain-text session list, and one link to the agenda at the end.

Sessions are grouped by location and sorted by available player spaces.

## Requirements

- Python 3
- The packages listed in `requirements.txt`
- Chromium installed through Playwright

## Setup

Create and activate a virtual environment, then install the Python dependency and browser.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Run

With the virtual environment activated:

```bash
python RPGNightUtrechtWarhornScraper.py
```

The script runs Chromium in headless mode and prints status messages followed by sections labeled `--- Discord version ---` and `--- WhatsApp version ---`. Copy the message content after the corresponding label when sharing it.

## Notes

- The scraper is tailored to the current Warhorn agenda page structure; changes to that page may require selector updates.
- No Discord or Warhorn credentials are required. The script reads the public agenda and prints text; it does not post messages automatically.

## AI Disclaimer

The first release was generated with Claude. Later increments made use of the standard agent of Visual Studio Code.