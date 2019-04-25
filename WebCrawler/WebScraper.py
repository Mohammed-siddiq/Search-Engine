from bs4 import BeautifulSoup
from urllib.request import urlopen
from bs4.element import Comment
import requests

'''
Parses the Html and returns all the available links in the 
'''
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def scrape_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    return links


def scrape_info(html, url, filecounter):
    create_document(html, "UIC Web Pages/" + str(filecounter) + ".txt")
    doc_text = text_from_html(html)
    create_document(doc_text, "UIC Documents/" + str(filecounter) + ".txt", url)
    return doc_text


def create_document(text, filename, url=None):
    with open(filename, 'w') as f:
        if url is not None:
            f.writelines("URL : " + url + "\n")
        f.write(text)


def scrape_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=(3, 30))
        return res, url
    except requests.RequestException:
        return
