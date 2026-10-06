"""Quotes to Scrape: selectors."""
import logging

import config
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    name = config.QUOTES_SOURCE
    start_url = config.QUOTES_URL

    def parse_quote(self, div, page_url):
        text = div.select_one("span.text")
        author = div.select_one("small.author")
        return {
            "text_raw": text.get_text() if text else None,
            "author_raw": author.get_text() if author else None,
            "tags_raw": [t.get_text() for t in div.select("a.tag")],
            "page_url": page_url,
        }

    def parse_page(self, soup, page_url):
        records = []
        for div in soup.select("div.quote"):
            try:
                records.append(self.parse_quote(div, page_url))
            except Exception:
                logger.exception("[%s] Skipping unparsable quote on %s", self.name, page_url)
        return records
