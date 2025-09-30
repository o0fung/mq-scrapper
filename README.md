# HK MSc Admission Scraper

Scrapes Hong Kong university MSc / TPG programme listings (starting with HKU) and exports data to CSV.  
Primary script currently implemented: `hku_tpg_scrapper.py` (with a Typer CLI).

---

## What It Does (HKU Module)
1. Loads the HKU Taught Postgraduate (TPG) programme listing.
2. Paginates until the last page.
3. Extracts core fields (abbr, faculty, title, mode, link).
4. (Optional) Opens each programme’s detail page to capture highlight info (duration, fees, start, deadline, description) with retries.
5. Writes everything to `programmes.csv`.

---

## Output
File: `programmes.csv`  
Open with Excel / Numbers / Google Sheets.

Columns (current HKU scraper):
- abbr
- university
- faculty
- title
- mode
- link
- duration
- fees
- start
- deadline
- description

---

## Requirements
- Python 3.9+
- Google Chrome installed
- Internet access
- No manual chromedriver step needed (Selenium Manager + fallback to webdriver-manager)

---

## Setup (One Time)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
(Reactivate later with `source .venv/bin/activate`.)

---

## Quick Start
Default scrape (headless, full details):
```bash
python hku_tpg_scrapper.py scrape
```

Show available options:
```bash
python hku_tpg_scrapper.py scrape --help
```

See Selenium version:
```bash
python hku_tpg_scrapper.py version
```

---

## Common Options (Examples)

Watch the browser:
```bash
python hku_tpg_scrapper.py scrape --no-headless
```

Skip detail pages (faster):
```bash
python hku_tpg_scrapper.py scrape --no-details
```

Limit to first 5 detail pages (test run):
```bash
python hku_tpg_scrapper.py scrape --max-details 5
```

Add polite delay (0.5s) between detail pages:
```bash
python hku_tpg_scrapper.py scrape --detail-delay 0.5
```

Custom output filename:
```bash
python hku_tpg_scrapper.py scrape --out hku_programmes_2025.csv
```

Custom listing URL (if HKU changes path):
```bash
python hku_tpg_scrapper.py scrape --url https://portal.hku.hk/tpg-admissions/programme-listing
```

---

## CLI Parameters (Scrape Command)
| Flag | Description |
|------|-------------|
| --url TEXT | Listing URL (default HKU TPG) |
| --label TEXT | University tag stored per row (default HKU) |
| --out TEXT | Output CSV filename |
| --headless / --no-headless | Run invisible / visible Chrome |
| --details / --no-details | Enable / skip detail-page scraping |
| --max-details INT | Limit number of detail pages processed |
| --detail-delay FLOAT | Delay (seconds) after each detail page |
| --retries INT | Detail page retry count |
| --backoff FLOAT | Retry backoff multiplier (linear) |

---

## Troubleshooting

| Issue | Action |
|-------|--------|
| Empty CSV | Site structure changed → update selectors in script |
| Detail timeout messages | Normal occasionally; retries applied |
| Browser never appears | You used headless mode (default) |
| Selenium Manager error | Ensure Chrome installed / updated |
| Encoding issues in Excel | Use UTF-8 import option |

Stop early: Ctrl + C

---

## Extending
To add another university:
1. Copy `hku_tpg_scrapper.py` to a new file.
2. Adjust: listing URL, item selector, highlight selectors.
3. Keep dataclass fields consistent for unified CSV.

---

## Editing Selectors
Key constants in the script:
- `PROGRAMME_ITEM_SELECTOR`
- `NEXT_LI_SELECTOR`
- `ACTIVE_PAGE_SELECTOR`
- Highlight selectors inside `fetch_programme_highlights()`

Inspect DOM (Chrome DevTools) → update selectors → rerun.

---

## Adding New Fields
1. Add field to `Programme` dataclass.
2. Populate during listing or detail extraction.
3. Add header in `write_csv`.
4. Run again.

---

## Politeness
If concerned about load:
- Use `--detail-delay 0.5`
- Limit with `--max-details`
- Avoid running in tight loops repeatedly.

---

## Roadmap (Planned)
- Support multiple HK universities via config
- JSON export
- Optional parallel detail fetch
- Unified central CLI (multi-site)

---

## License
Add a LICENSE file (e.g., MIT) if distributing.

---

## Support
Provide:
- Command used
- Console output snippet
- Python version (`python --version`)
- OS (e.g., macOS 14.x)

---

Happy scraping.
