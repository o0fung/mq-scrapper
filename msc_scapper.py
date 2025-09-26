# pip3 install requests beautifulsoup4 tenacity
import requests
import re
import csv
import threading
import math
from tenacity import RetryError

from bs4 import BeautifulSoup
from queue import Queue
from tenacity import retry, stop_after_attempt, wait_exponential

from rich import print


target_url = "https://portal.hku.hk/tpg-admissions/programme-listing"

# instantiate the queues
high_priority_queue = Queue()
low_priority_queue = Queue()

# add the initial URL to the queues
high_priority_queue.put(target_url)
low_priority_queue.put(target_url)

# define a thread-safe set for visited URLs
visited_urls = set()
visited_lock = threading.Lock()

# set maximum crawl limit
max_crawl = math.inf

# create a regex pattern for product page URLs
url_pattern = re.compile(r"/page/\d+/")

# list to store scraped data
product_data = []

# activate thread lock to prevent race conditions
data_lock = threading.Lock()

# initialize session
session = requests.Session()


# implement a request retry
@retry(
    stop=stop_after_attempt(4),  # max retries
    wait=wait_exponential(multiplier=5, min=4, max=5),  # exponential backoff
)
def fetch_url(url):
    """Fetch a URL with retries.

    Returns:
        Response | None: None is returned if the page is a 404 so the caller can skip it.
    """
    try:
        response = session.get(url, timeout=15)
        # If it's a 404, don't raise / retry, just skip.
        if response.status_code == 404:
            print(f"[yellow]Skip 404:[/] {url}")
            return None
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        # If somehow a 404 sneaks here (race condition), just skip.
        if getattr(e.response, "status_code", None) == 404:
            print(f"[yellow]Skip 404 (raised):[/] {url}")
            return None
        # Re-raise other HTTP errors to trigger retry logic.
        raise
    except requests.exceptions.RequestException as e:
        # Other network issues will be retried by tenacity (since we re-raise)
        print(f"[red]Request error:[/] {url} -> {e}")
        raise


def get_soup(response):
    # Improve encoding detection
    if not response.encoding or response.encoding.lower() in ("iso-8859-1", "utf-8 guessed"):
        apparent = response.apparent_encoding
        if apparent:
            response.encoding = apparent
    html = response.text  # Now decoded using the (possibly updated) encoding
    return BeautifulSoup(html, "html.parser")


def crawler():
    # set a crawl counter to track the crawl depth
    crawl_count = 0

    while (not high_priority_queue.empty() or not low_priority_queue.empty()) and crawl_count < max_crawl:

        # update the priority queue
        if not high_priority_queue.empty():
            current_url = high_priority_queue.get()
        elif not low_priority_queue.empty():
            current_url = low_priority_queue.get()
        else:
            break

        with visited_lock:
            # check and skip if the current url has been visited before
            if current_url in visited_urls:
                continue

            # add the current URL to the URL set
            visited_urls.add(current_url)

            print(current_url)

        # request the target URL (may return None if 404)
        try:
            response = fetch_url(current_url)
        except RetryError as e:
            # Underlying fetch kept failing (e.g., invalid schema); skip
            print(f"[red]Skip after retries:[/] {current_url} -> {e}")
            continue
        except requests.exceptions.RequestException as e:
            # Any other non-retried request exception
            print(f"[red]Skip request error:[/] {current_url} -> {e}")
            continue
        if response is None:
            continue  # skip 404 pages

        print(response.content)

        # parse the HTML
        soup = get_soup(response)

        # collect all the links
        for link_element in soup.find_all("a", href=True):
            url = link_element["href"].strip()

            # skip empty or non-navigational links
            if not url or url.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            # check if the URL is absolute or relative
            if not url.startswith("http"):
                absolute_url = requests.compat.urljoin(target_url, url)
            else:
                absolute_url = url

            with visited_lock:
                # ensure the crawled link belongs to the target domain and hasn't been visited
                if absolute_url not in visited_urls:
                    # prioritize product pages 
                    if url_pattern.search(absolute_url):
                        high_priority_queue.put(absolute_url)
                    else:
                        low_priority_queue.put(absolute_url)

            # extract content only if the current URL matches the regex page pattern
        if url_pattern.search(current_url):
            # get the parent element
            product_containers = soup.find_all("li", class_="product")

            # scrape product data
            for product in product_containers:

                data = {
                    "Url": product.find("a", class_="woocommerce-LoopProduct-link")[
                        "href"
                    ],
                    "Image": product.find("img", class_="product-image")["src"],
                    "Name": product.find("h2", class_="product-name").get_text(),
                    "Price": product.find("span", class_="price").get_text(),
                }
                with data_lock:
                    # append extracted data
                    product_data.append(data)

        # update the crawl count
        crawl_count += 1


# specify the number of threads to use
num_workers = 4
threads = []

# start worker threads
for _ in range(num_workers):
    thread = threading.Thread(target=crawler, daemon=True)
    threads.append(thread)
    thread.start()

# wait for all threads to finish
for thread in threads:
    thread.join()

# save data to CSV
csv_filename = "products.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Url", "Image", "Name", "Price"])
    writer.writeheader()
    writer.writerows(product_data)
