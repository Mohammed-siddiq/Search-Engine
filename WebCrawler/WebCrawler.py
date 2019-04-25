import re

import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import itertools
import threading

from WebCrawler.AtomicCounter import Counter
from WebCrawler.WebScraper import scrape_page, scrape_links, scrape_info


class WebCrawler:

    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=40)
        self.domain = 'uic.edu'
        self.atomicCounter = Counter(0)

        # All the scraped pages
        self.crawled_pages = set([])
        self.cont = itertools.count()
        self.counter = 0
        # A queue representing the urls fetched and yet to be scraped
        self.to_crawl = Queue()

        # Adding the base url to the queue
        self.to_crawl.put(self.base_url)

    def parse_links(self, html):
        links = scrape_links(html)
        for link in links:
            url = link['href']
            if url.startswith('/') or self.domain in url and '.com' not in url:
                url = urljoin(self.root_url, url)
                # url = re.search('.+?uic.edu', url).group(0)
                if url not in self.crawled_pages and '@' not in url:  # If not already crawled
                    self.to_crawl.put(url)

    def post_scrape_callback(self, res):
        if res is not None:
            # result = res
            result = res.result()
            if result[0] and result[
                0].status_code == 200:  # only if the http request was successful get the text and other links
                self.parse_links(result[0].text)
                self.atomicCounter.increment()
                scrape_info(result[0].text, result[1], self.atomicCounter.value())

    def run_scraper(self):
        while True:
            try:
                if self.atomicCounter.value() >= 3000:
                    return
                target_url = self.to_crawl.get(timeout=60)  # wait for 60 sec for a page to add a url to be parsed
                if target_url not in self.crawled_pages:  # Avoiding cycles ->if page is already scraped then donot continue
                    print(" Scraping URL: {}".format(target_url))
                    self.crawled_pages.add(target_url)
                    job = self.pool.submit(scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    s = WebCrawler("https://cs.uic.edu")
    s.run_scraper()
    # res =  scrape_page("https://cs.uic.edu/~balajee/cs594-s17/")
    # s.post_scrape_callback(res)
