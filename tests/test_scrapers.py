"""Offline scraper tests using canned HTML and a fake session (no internet)."""
import requests
from bs4 import BeautifulSoup

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BOOK_PAGE = """
<html><body><ol>
<li><article class="product_pod">
  <p class="star-rating Three"></p>
  <h3><a href="a-light_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
  <div><p class="price_color">\u00a351.77</p><p class="availability"> In stock </p></div>
</article></li>
<li><article class="product_pod"><h3></h3></article></li>
</ol>%s</body></html>"""
NEXT = '<ul><li class="next"><a href="page-2.html">next</a></li></ul>'

QUOTE_PAGE = """
<html><body>
<div class="quote"><span class="text">\u201cHello world.\u201d</span>
 <span>by <small class="author">Ann</small></span>
 <div class="tags"><a class="tag">Life</a><a class="tag">love</a></div></div>
<div class="quote"><span class="text">\u201cNo author or tags\u201d</span></div>
%s</body></html>"""


class FakeResponse:
    def __init__(self, text, status=200):
        self.text, self.status, self.encoding = text, status, None

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status}")


class FakeSession:
    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def get(self, url, timeout=None):
        self.calls.append(url)
        page = self.pages.get(url)
        if page is None:
            raise requests.ConnectionError("boom")
        return FakeResponse(page) if isinstance(page, str) else page


def test_books_parse_and_missing_elements():
    scraper = BooksScraper(session=FakeSession({}), delay=0, fetch_details=False)
    recs = scraper.parse_page(BeautifulSoup(BOOK_PAGE % "", "lxml"), "https://books.toscrape.com/")
    assert len(recs) == 2
    assert recs[0]["title"] == "A Light in the Attic"
    assert recs[0]["href"] == "https://books.toscrape.com/a-light_1000/index.html"
    assert recs[0]["rating_raw"] == "star-rating Three"
    assert recs[1]["title"] is None and recs[1]["price_raw"] is None   # no crash


def test_quotes_parse_missing_author_and_tags():
    scraper = QuotesScraper(session=FakeSession({}), delay=0)
    recs = scraper.parse_page(BeautifulSoup(QUOTE_PAGE % "", "lxml"), "https://quotes.toscrape.com/")
    assert recs[0]["author_raw"] == "Ann" and recs[0]["tags_raw"] == ["Life", "love"]
    assert recs[1]["author_raw"] is None and recs[1]["tags_raw"] == []


def test_pagination_follows_next_links():
    s = QuotesScraper(session=FakeSession({
        "https://quotes.toscrape.com/": QUOTE_PAGE % NEXT.replace("page-2.html", "/page/2/"),
        "https://quotes.toscrape.com/page/2/": QUOTE_PAGE % "",
    }), delay=0)
    assert len(s.scrape_all()) == 4


def test_page_failure_stops_source_but_keeps_earlier_records():
    s = QuotesScraper(session=FakeSession({
        "https://quotes.toscrape.com/": QUOTE_PAGE % NEXT.replace("page-2.html", "/page/2/"),
        # page 2 missing -> ConnectionError
    }), delay=0)
    assert len(s.scrape_all()) == 2


def test_http_error_returns_none():
    s = QuotesScraper(session=FakeSession({"u": FakeResponse("", 500)}), delay=0)
    assert s.fetch_soup("u") is None


def test_book_detail_enrichment():
    detail = """<ul class="breadcrumb"><li><a>Home</a></li><li><a>Books</a></li>
      <li><a>Poetry</a></li><li>Title</li></ul>
      <div id="product_description"></div><p>A nice  description.</p>"""
    base = "https://books.toscrape.com/"
    s = BooksScraper(session=FakeSession({
        base: BOOK_PAGE % "",
        base + "a-light_1000/index.html": detail,
    }), delay=0)
    recs = s.scrape_all()
    assert recs[0]["category_raw"] == "Poetry"
    assert "nice" in recs[0]["description_raw"]
