from bs4 import BeautifulSoup
from urllib.request import urlopen
from bs4.element import Comment
import requests
import re
'''
The scraper also extracts the visible text from each of these pages, which are persisted in a directory uic-docs-text
Also Parses the Html and returns all the available links in the page .
'''

docs_directory = "uic-docs-text/"
web_pages_directory = "uic-docs-webpages/"

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts).encode("utf-8", errors="ignore").decode("utf-8")


def scrape_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return links


def scrape_info(html, url, filecounter):
    # create_document(html, web_pages_directory + str(filecounter) + ".txt")
    doc_text = text_from_html(html)
    create_document(doc_text, docs_directory + str(filecounter) + ".txt", url)
    return doc_text


def create_document(text, filename, url=None):
    with open(filename, 'w') as f:
        if url is not None:
            f.writelines("URL : " + url + "\n")
        f.write(text)


def scrape_page(url):
    try:
        res = requests.get(url, timeout=(3, 60))
        return res, url
    except requests.RequestException:
        return
