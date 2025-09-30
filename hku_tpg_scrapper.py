"""
Scrape taught postgraduate programme listings (with pagination) into a list of dictionaries
and write them to a CSV file.

Overview:
- Open the HKU TPG listing page.
- Paginate through all pages until the "next" control disappears or becomes disabled.
- Extract core programme fields from each listing card.
- (Optional) For each programme, open the detail page in a temporary new tab and collect "highlight" data.
- Write the aggregated results to a CSV file.

Key robustness features:
- Explicit waits for elements (Selenium WebDriverWait).
- Safe element/text/attribute access helpers.
- Retry logic for detail pages.
- Graceful stop when pagination ends.
"""

import csv
import sys
from rich import print
from contextlib import suppress
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from time import sleep

import typer  # CLI framework (Typer) for easy command definition

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)

# ------------- Configuration Constants -------------

# Base listing URL (can be overridden via CLI argument)
URL_DEFAULT = "https://portal.hku.hk/tpg-admissions/programme-listing"

# Wait (seconds) for listing page elements (pagination items)
WAIT_SECONDS_PAGES = 15
# Wait (seconds) for detail page highlight elements
WAIT_SECONDS_DETAILS = 10

# CSS selector for each programme entry anchor element in the listing results container
PROGRAMME_ITEM_SELECTOR = "#programme-listing-results > a"
# Pagination "next" list item selector
NEXT_LI_SELECTOR = "li.J-paginationjs-next"
# Selector indicating the active page number (helps detect page change)
ACTIVE_PAGE_SELECTOR = "li.J-paginationjs-page.active"

# Typer application entry (groups CLI commands)
app = typer.Typer(help="Scrape HKU TPG programme listings to CSV.")


@dataclass
class Programme:
    """
    Data structure representing a single programme row.

    Fields:
        abbr        Short abbreviation (may be empty if site omits).
        university  Label/tag for the institution (supplied via CLI).
        faculty     Faculty / School name.
        title       Programme title.
        mode        Study mode (e.g., Full-time, Part-time).
        link        URL to programme detail page.
        duration    (Detail) Duration text.
        fees        (Detail) Fees text.
        start       (Detail) Start date / period.
        deadline    (Detail) Application deadline.
        description (Detail) Short description / overview.
    """
    abbr: str
    university: str
    faculty: str
    title: str
    mode: str
    link: str
    duration: str = ""
    fees: str = ""
    start: str = ""
    deadline: str = ""
    description: str = ""


# ------------- Helper Functions -------------


def _safe_text(parent, by, selector) -> str:
    """
    Safely locate a child element and return stripped text.
    Returns empty string if element is absent or goes stale.
    """
    with suppress(NoSuchElementException, StaleElementReferenceException):
        return parent.find_element(by, selector).text.strip()
    return ""


def _safe_attr(element, attr: str) -> str:
    """
    Safely fetch an attribute value from an element.
    Returns empty string if the attribute or element is not accessible.
    """
    with suppress(Exception):
        v = element.get_attribute(attr)
        return v.strip() if v else ""
    return ""


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Selenium Chrome WebDriver.

    Attempts:
        1. Use Selenium Manager (automatic driver resolution).
        2. If that fails, fallback to webdriver-manager (downloads driver binary).

    Args:
        headless: Run without a visible browser window if True.

    Returns:
        Configured Chrome WebDriver instance.

    Raises:
        RuntimeError if both approaches fail.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # newer headless mode
    # Common flags for container / CI stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    try:
        # Preferred: rely on Selenium Manager
        return webdriver.Chrome(options=options)
    except WebDriverException as e:
        print("[yellow]Selenium Manager failed, trying webdriver-manager fallback...[/]")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as inner:
            raise RuntimeError(
                "Could not start Chrome via Selenium Manager or webdriver-manager.\n"
                f"Selenium error: {e}\nFallback error: {inner}"
            )


def fetch_programme_highlights(
    driver: webdriver.Chrome,
    link: str,
    retries: int = 2,
    backoff: float = 1.5,
) -> Dict[str, str]:
    """
    Collect highlight fields from a programme detail page.

    Strategy:
        - Open detail URL in a new tab (keeps listing state pure).
        - Wait for at least one highlight block (selector assumed).
        - Extract highlight blocks and map them into standardized keys.
        - Close the tab and return to the original window.
        - Retry on timeout or WebDriver errors.

    Args:
        driver: Active Selenium driver (listing context).
        link: Detail page URL.
        retries: Number of retry attempts (in addition to first attempt).
        backoff: Linear backoff multiplier (seconds * attempt_index) between retries.

    Returns:
        Dict of highlight fields (duration/fees/start/deadline/description).
    """
    def attempt_once() -> Dict[str, str]:
        original_window = driver.current_window_handle
        local_highlights: Dict[str, str] = {
            "duration": "",
            "fees": "",
            "start": "",
            "deadline": "",
            "description": "",
        }
        try:
            # Open detail page in a separate tab
            driver.execute_script("window.open(arguments[0], '_blank');", link)
            driver.switch_to.window(driver.window_handles[-1])

            print(f"[bold cyan]>> Visiting[/] {link}")

            # Wait until at least one highlight item appears
            wait = WebDriverWait(driver, WAIT_SECONDS_DETAILS)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#FullTimeTab .highlights-item"))
            )

            # Collect highlight items (adjust selectors if the site changes)
            items = driver.find_elements(By.CSS_SELECTOR, "#FullTimeTab .highlights-item")

            for item in items:
                title = _safe_text(item, By.CSS_SELECTOR, ".highlights-item-title").lower()
                description = _safe_text(item, By.CSS_SELECTOR, ".highlights-item-description").replace('\n', ' ')
                if not title:
                    continue
                # Match broad keywords to fill standardized fields; only fill once per field
                if "duration" in title and not local_highlights["duration"]:
                    local_highlights["duration"] = description
                elif "fee" in title and not local_highlights["fees"]:
                    local_highlights["fees"] = description
                elif "start" in title and not local_highlights["start"]:
                    local_highlights["start"] = description
                elif "deadline" in title and not local_highlights["deadline"]:
                    local_highlights["deadline"] = description
                elif ("description" in title or "overview" in title) and not local_highlights["description"]:
                    local_highlights["description"] = description
        finally:
            # Clean up detail tab regardless of success/failure
            with suppress(Exception):
                driver.close()
            with suppress(Exception):
                driver.switch_to.window(original_window)
        return local_highlights

    # Retry loop
    for attempt in range(retries + 1):
        try:
            return attempt_once()
        except TimeoutException:
            print(f"[yellow]Detail timeout (attempt {attempt+1}/{retries+1}) for {link}[/]")
        except WebDriverException as e:
            print(f"[yellow]Detail page error (attempt {attempt+1}/{retries+1}) for {link}: {e}[/]")
        # Backoff before next retry (if any)
        if attempt < retries:
            sleep(backoff * (attempt + 1))

    print(f"[red]Giving up on detail page after {retries+1} attempts: {link}[/]")
    return {"duration": "", "fees": "", "start": "", "deadline": "", "description": ""}


def fetch_programmes(
    label: str = '',
    url: str = URL_DEFAULT,
    headless: bool = True,
    fetch_details: bool = True,
    detail_delay: float = 0.0,
    max_details: Optional[int] = None,
    detail_retries: int = 2,
    detail_retry_backoff: float = 1.5,
) -> List[Dict[str, str]]:
    """
    Crawl the paginated listing and optionally enrich each programme with detail-page highlights.

    Pagination logic:
        - Loop until "next" pagination element is missing or disabled.

    Args:
        label: University label stored per record (e.g., 'HKU').
        url: Listing starting URL.
        headless: Run browser in headless mode.
        fetch_details: If True, open each detail page for extra fields.
        detail_delay: Seconds to sleep after each detail fetch (politeness).
        max_details: Limit number of detail pages processed (debug/testing).
        detail_retries: Retries for each detail page.
        detail_retry_backoff: Backoff multiplier for detail retries.

    Returns:
        List of dicts (each representing one programme).
    """
    driver: Optional[webdriver.Chrome] = None
    try:
        driver = create_driver(headless=headless)
        driver.get(url)

        print(f"[bold cyan]>> Visiting[/] {url}")
        print(f"[bold cyan]>> Start Scrapping Programme Details[/]")

        wait = WebDriverWait(driver, WAIT_SECONDS_PAGES)

        programmes: List[Programme] = []
        seen_links = set()          # Prevent duplicate rows if any link repeats
        details_count = 0           # Counter for number of detail pages fetched
        page_index = 1              # Human-readable page index

        while True:
            # Wait for programme items on the current page
            items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, PROGRAMME_ITEM_SELECTOR))
            )

            # Try to capture active page number (for logging)
            current_page_label = ""
            with suppress(Exception):
                current_page_label = _safe_text(driver, By.CSS_SELECTOR, ACTIVE_PAGE_SELECTOR)

            new_in_page = 0  # Count new items added for this page

            # Iterate through programme items
            for item in items:
                # The selector targets an anchor (<a>), but remain defensive
                anchor = item if item.tag_name.lower() == "a" else None
                if not anchor:
                    with suppress(NoSuchElementException):
                        anchor = item.find_element(By.TAG_NAME, "a")

                # Extract visible listing fields
                faculty = _safe_text(item, By.CSS_SELECTOR, ".programme-faculty")
                title = _safe_text(item, By.CSS_SELECTOR, ".programme-title")
                abbr = _safe_text(item, By.CSS_SELECTOR, ".abbreviation")
                mode = _safe_text(item, By.CSS_SELECTOR, ".mode-of-study")
                link = _safe_attr(anchor, "href") if anchor else ""

                # Basic validation and dedupe
                if not link or link in seen_links:
                    continue
                if not any([abbr, faculty, title, mode]):
                    # Skip entries that appear structurally empty
                    continue

                # Default empty detail fields until (optionally) filled
                duration = fees = start = deadline = description = ""

                # Detail page enrichment (if enabled and within max_details)
                if fetch_details and (max_details is None or details_count < max_details):
                    highlights = fetch_programme_highlights(
                        driver,
                        link,
                        retries=detail_retries,
                        backoff=detail_retry_backoff
                    )
                    duration = highlights["duration"]
                    fees = highlights["fees"]
                    start = highlights["start"]
                    deadline = highlights["deadline"]
                    description = highlights["description"]
                    details_count += 1

                    # Optional polite delay to avoid hammering server
                    if detail_delay > 0:
                        sleep(detail_delay)

                # Append structured programme object
                programmes.append(
                    Programme(
                        abbr=abbr,
                        university=label,
                        faculty=faculty,
                        title=title,
                        mode=mode,
                        link=link,
                        duration=duration,
                        fees=fees,
                        start=start,
                        deadline=deadline,
                        description=description,
                    )
                )
                seen_links.add(link)
                new_in_page += 1

            # Progress log line
            print(
                f"[green]Page {page_index} ({current_page_label}) -> collected {new_in_page}, "
                f"total {len(programmes)} (details: {details_count})[/]"
            )

            # Attempt to locate pagination "next" control
            try:
                next_li = driver.find_element(By.CSS_SELECTOR, NEXT_LI_SELECTOR)
            except NoSuchElementException:
                print("[yellow]No next pagination element. Stopping.[/]")
                break

            # If the "next" list item has 'disabled' class, we reached last page
            next_classes = (next_li.get_attribute("class") or "").lower()
            if "disabled" in next_classes:
                print("[yellow]Next button disabled. Reached last page.[/]")
                break

            # Get the <a> inside the pagination item
            try:
                next_a = next_li.find_element(By.TAG_NAME, "a")
            except NoSuchElementException:
                print("[yellow]Next link missing inside pagination element. Stopping.[/]")
                break

            # Keep reference to an existing element to detect staleness after page change
            first_item = items[0]

            # Navigate to the next page
            next_a.click()

            # Wait for prior page contents to become stale / page number to change
            with suppress(Exception):
                wait.until(EC.staleness_of(first_item))
            with suppress(Exception):
                old_page = current_page_label
                if old_page:
                    wait.until_not(
                        EC.text_to_be_present_in_element(
                            (By.CSS_SELECTOR, ACTIVE_PAGE_SELECTOR), old_page
                        )
                    )

            page_index += 1  # Increment manual page counter

        # Convert dataclass objects to plain dictionaries (CSV / JSON friendly)
        return [asdict(p) for p in programmes]

    except TimeoutException:
        print("[red]Timed out waiting for programme items.[/]", file=sys.stderr)
        return []
    except WebDriverException as e:
        print(f"[red]WebDriver error:[/] {e}", file=sys.stderr)
        return []
    finally:
        # Always close browser
        if driver:
            driver.quit()


def write_csv(rows: List[Dict[str, str]], filepath: str = "programmes.csv") -> None:
    """
    Write programme data to a CSV file.

    Args:
        rows: List of programme dicts.
        filepath: Output CSV path/name.
    """
    if not rows:
        print("[yellow]No data to write.[/]")
        return

    headers = [
        "abbr",
        "university",
        "faculty",
        "title",
        "mode",
        "link",
        "duration",
        "fees",
        "start",
        "deadline",
        "description",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[bold green]Wrote {len(rows)} rows to {filepath}[/]")


# ------------- CLI Commands -------------


@app.command()
def scrape(
    url: str = typer.Option(URL_DEFAULT, "--url", help="Listing URL to scrape."),
    label: str = typer.Option("HKU", "--label", help="University label stored in CSV."),
    out: str = typer.Option("programmes.csv", "--out", help="Output CSV filename."),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser in headless mode."),
    details: bool = typer.Option(True, "--details/--no-details", help="Fetch detail pages (slower)."),
    max_details: Optional[int] = typer.Option(None, "--max-details", help="Limit number of detail pages (debug)."),
    delay: float = typer.Option(0.0, "--detail-delay", help="Delay seconds between detail page fetches."),
    retries: int = typer.Option(2, "--retries", help="Retry count per detail page."),
    backoff: float = typer.Option(1.5, "--backoff", help="Backoff multiplier between detail retries."),
):
    """
    Run the full scrape and write results to CSV.

    Example:
        python hku_tpg_scrapper.py scrape --no-headless --max-details 5
    """
    rows = fetch_programmes(
        label=label,
        url=url,
        headless=headless,
        fetch_details=details,
        detail_delay=delay,
        max_details=max_details,
        detail_retries=retries,
        detail_retry_backoff=backoff,
    )
    write_csv(rows, out)


@app.command()
def version():
    """
    Show versions of key libraries (currently only Selenium reported).
    """
    import selenium
    print(f"selenium={selenium.__version__}")


# ------------- Entry Point -------------

if __name__ == "__main__":
    # Delegates to Typer CLI
    app()