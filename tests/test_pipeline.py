import main
from processing.transform import clean_book, clean_quote


def test_clean_and_validate_counts_reconcile():
    raw = [
        {"title": " Good  Book ", "href": "https://b.com/1", "price_raw": "£5.00", "rating_raw": "star-rating Two"},
        {"title": None, "href": "https://b.com/2", "price_raw": "£1", "rating_raw": "One"},   # missing name
        {"title": "Bad URL", "href": None, "price_raw": "£1", "rating_raw": "One"},          # invalid url
    ]
    valid, stats = main.clean_and_validate("Books to Scrape", raw)
    assert len(valid) == 1
    assert stats["raw_collected"] == 3 and stats["rejected_total"] == 2
    assert stats["rejected_by_reason"] == {"missing_name": 1, "invalid_url": 1}


def test_common_schema_keys():
    import config
    b = clean_book({"title": "T", "href": "https://x.com", "price_raw": "£1", "rating_raw": "One"})
    q = clean_quote({"text_raw": "\u201cQ\u201d", "author_raw": "A", "tags_raw": ["x"], "page_url": "https://x.com"})
    assert set(b) == set(q) == set(config.COLUMNS)
    assert q["price"] is None and b["author"] is None
