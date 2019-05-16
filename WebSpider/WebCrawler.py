from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import itertools

from WebSpider.AtomicCounter import Counter
from WebSpider.WebScraper import scrape_page, scrape_links, scrape_info






def persist_links(node_link, linked_urls, id):
    with open("uic-web-graph/" + str(id), "w") as f:
        f.write(node_link + "::")
        f.writelines(','.join(linked_urls))


'''

The Crawler crawls the UIC domain starting from the URL https://cs.uic.edu, 
multi-threaded crawle simultaneously 10 worker threads scrape the UIC domain

'''


class WebCrawler:

    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.domain = 'uic.edu'
        self.atomicCounter = Counter(0)
        self.invalid_extensions = ["pdf", "jpg", "jpeg", "doc", "docx", "ppt", "pptx", "png", "txt", "exe", "ps", "psb"]
        # All the scraped pages
        self.crawled_pages = set([])
        self.cont = itertools.count()
        self.counter = 0
        # A queue representing the urls fetched and yet to be scraped
        self.to_crawl = Queue()

        # Adding the base url to the queue
        self.to_crawl.put(self.base_url)

    def is_valid_extension(self, url):
        if True in [ext in url for ext in self.invalid_extensions]:
            return False
        return True

    def parse_links(self, html, node_link):
        links = scrape_links(html)
        linked_urls = set()
        for link in links:
            url = link['href']
            if (url.startswith('/') or self.domain in url) and ('.com' not in url):  # run only in the uic.edu domain
                url = urljoin(self.root_url, url)
                # url = re.search('.+?uic.edu', url).group(0)
                if url not in self.crawled_pages and '@' not in url and self.is_valid_extension(url):
                    if not url.endswith("/"):
                        url = url + "/"  # appending / in the end to avoid duplicate runs
                    if "https" not in url:
                        url = url.replace("http", "https")
                    self.to_crawl.put(url)
                    linked_urls.add(url)

        # print("---------------------")
        # print(node_link)
        # print("::")
        # print(linked_urls)
        # print("---------------------")
        self.atomicCounter.increment()
        persist_links(node_link, linked_urls, self.atomicCounter.value())

    def post_scrape_callback(self, res):
        if res is not None:
            # result = res
            result = res.result()
            if result[0] and result[
                0].status_code == 200:  # only if the http request was successful get the text and other links
                self.parse_links(result[0].text, result[1])
                scrape_info(result[0].text, result[1], self.atomicCounter.value())

    def run_scraper(self):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=120)  # wait for 60 sec for a page to add a url to be parsed
                if target_url not in self.crawled_pages:  # Avoiding cycles ->if page is
                    # already scraped then donot continue
                    print(" Scraping URL: {}".format(target_url))
                    self.crawled_pages.add(target_url)
                    job = self.pool.submit(scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

    def store_crawled_pages(self):
        with open("uic-web-graph/crawled_pages.txt", "w") as f:
            f.write("\n".join(self.crawled_pages))


if __name__ == '__main__':
    s = WebCrawler("https://cs.uic.edu")
    s.run_scraper()
    # s.store_crawled_pages()
    # res =  scrape_page("http://engineering.uic.edu/student-news-2017/")
    # s.post_scrape_callback(res)
