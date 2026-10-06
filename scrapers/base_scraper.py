"""Shared networking: session, retries, timeout, polite delay, pagination loop."""
import logging
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import config

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """Session with User-Agent and exponential-backoff retries (1s, 2s, 4s)."""
    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT})
    retries = Retry(total=3, backoff_factor=1.0,
                    status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class BaseScraper:
    """Subclasses set `name`, `start_url` and implement `parse_page`."""

    name = "base"
    start_url = ""

    def __init__(self, session=None, delay=config.REQUEST_DELAY,
                 timeout=config.REQUEST_TIMEOUT, max_pages=None):
        self.session = session or create_session()
        self.delay = delay
        self.timeout = timeout
        self.max_pages = max_pages

    # -- networking ---------------------------------------------------
    def fetch_soup(self, url):
        """Download a URL and return a BeautifulSoup, or None on failure."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"          # keeps the £ symbol correct
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as exc:
            logger.error("[%s] Failed to fetch %s: %s", self.name, url, exc)
            return None
        finally:
            if self.delay:
                time.sleep(self.delay)

    # -- to be implemented by subclasses --------------------------------
    def parse_page(self, soup, page_url):
        raise NotImplementedError

    # -- pagination -------------------------------------------------------
    def scrape_all(self):
        """Follow the 'next' link until there is none. Returns raw dicts."""
        url, page, records = self.start_url, 1, []
        while url:
            if self.max_pages and page > self.max_pages:
                logger.info("[%s] max_pages=%d reached, stopping", self.name, self.max_pages)
                break
            logger.info("[%s] Page %d: %s", self.name, page, url)
            soup = self.fetch_soup(url)
            if soup is None:
                logger.error("[%s] Stopping source after page failure at %s", self.name, url)
                break
            try:
                page_records = self.parse_page(soup, url)
            except Exception:
                logger.exception("[%s] Could not parse page %s", self.name, url)
                page_records = []
            logger.info("[%s] Page %d yielded %d records", self.name, page, len(page_records))
            records.extend(page_records)

            next_link = soup.select_one("li.next > a")
            href = next_link.get("href") if next_link else None
            url = urljoin(url, href) if href else None
            page += 1
        logger.info("[%s] Done: %d raw records over %d page(s)", self.name, len(records), page - 1)
        return records
