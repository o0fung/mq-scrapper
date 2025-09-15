import requests

from bs4 import BeautifulSoup
from rich import print

# set a maximum crawl limit
max_crawl = 20

# initialize the list of discovered URLs
target_url = "https://www.scrapingcourse.com/ecommerce/"
urls_to_visit = [target_url]


def crawler():
    # set a crawl counter to track the crawl depth
    crawl_count = 0

    while urls_to_visit and crawl_count < max_crawl:

        # get the page to visit from the list
        current_url = urls_to_visit.pop(0)

        print(current_url)

        # request the target URL
        response = requests.get(current_url)
        response.raise_for_status()
        print(response.text)

        # parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # collect all the links
        link_elements = soup.select("a[href]")
        for link_element in link_elements:
            url = link_element["href"]

            # convert links to absolute URLs
            if not url.startswith("http"):
                absolute_url = requests.compat.urljoin(target_url, url)
            else:
                absolute_url = url

            # ensure the crawled link belongs to the target domain and hasn't been visited
            if absolute_url.startswith(target_url) and absolute_url not in urls_to_visit:
                urls_to_visit.append(url)

        # Update the crawl counter
        crawl_count += 1

    print(urls_to_visit)


# execute the crawler
crawler()
