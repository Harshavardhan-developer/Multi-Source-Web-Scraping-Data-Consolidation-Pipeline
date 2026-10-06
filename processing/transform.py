"""Turn each source's raw dict into the common record layout."""
from datetime import datetime, timezone

import config
from processing import cleaning as c


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_book(raw):
    return {
        "source": config.BOOKS_SOURCE,
        "source_url": c.normalize_url(raw.get("href")),
        "name_or_title": c.clean_text(raw.get("title")),
        "category": c.clean_text(raw.get("category_raw")),
        "price": c.clean_price(raw.get("price_raw")),
        "rating": c.clean_rating(raw.get("rating_raw")),
        "author": None,
        "tags": None,
        "description": c.clean_text(raw.get("description_raw")),
        "scraped_at": _now(),
    }


def clean_quote(raw):
    return {
        "source": config.QUOTES_SOURCE,
        "source_url": c.normalize_url(raw.get("page_url")),
        "name_or_title": c.strip_quotes(raw.get("text_raw")),
        "category": None,
        "price": None,
        "rating": None,
        "author": c.clean_text(raw.get("author_raw")),
        "tags": c.clean_tags(raw.get("tags_raw")),
        "description": None,
        "scraped_at": _now(),
    }


CLEANERS = {config.BOOKS_SOURCE: clean_book, config.QUOTES_SOURCE: clean_quote}
