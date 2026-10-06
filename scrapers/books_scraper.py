"""Books to Scrape: selectors, detail-page enrichment."""
import logging
from urllib.parse import urljoin

import config
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    name = config.BOOKS_SOURCE
    start_url = config.BOOKS_URL

    def __init__(self, *args, fetch_details=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetch_details = fetch_details

    def parse_book(self, article, page_url):
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        avail = article.select_one("p.availability")
        return {
            "title": link.get("title") if link else None,
            "href": urljoin(page_url, link["href"]) if link and link.get("href") else None,
            "price_raw": price.get_text() if price else None,
            "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            "availability_raw": avail.get_text() if avail else None,
            "category_raw": None,
            "description_raw": None,
        }

    def parse_detail(self, soup):
        """Category (breadcrumb) and description from a detail page."""
        crumbs = soup.select("ul.breadcrumb li a")
        category = crumbs[-1].get_text() if len(crumbs) >= 3 else None
        desc = soup.select_one("#product_description ~ p")
        return category, desc.get_text() if desc else None

    def parse_page(self, soup, page_url):
        records = []
        for article in soup.select("article.product_pod"):
            try:
                rec = self.parse_book(article, page_url)
            except Exception:
                logger.exception("[%s] Skipping unparsable book on %s", self.name, page_url)
                continue
            if self.fetch_details and rec["href"]:
                detail = self.fetch_soup(rec["href"])
                if detail is not None:
                    try:
                        rec["category_raw"], rec["description_raw"] = self.parse_detail(detail)
                    except Exception:
                        logger.exception("[%s] Bad detail page %s", self.name, rec["href"])
                else:
                    logger.warning("[%s] Detail page missing, category/description left empty: %s",
                                   self.name, rec["href"])
            records.append(rec)
        return records
