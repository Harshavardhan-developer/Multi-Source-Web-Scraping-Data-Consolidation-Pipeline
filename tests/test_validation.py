from processing.validation import validate_record

GOOD_BOOK = {"source": "Books to Scrape", "name_or_title": "A", "source_url": "https://x.com/a",
             "price": 10.0, "rating": 3}


def test_valid_book():
    assert validate_record(GOOD_BOOK) == []


def test_each_rule():
    assert "unknown_source" in validate_record({**GOOD_BOOK, "source": "Other"})
    assert "missing_name" in validate_record({**GOOD_BOOK, "name_or_title": None})
    assert "invalid_url" in validate_record({**GOOD_BOOK, "source_url": "nope"})
    assert "invalid_price" in validate_record({**GOOD_BOOK, "price": -1})
    assert "invalid_price" in validate_record({**GOOD_BOOK, "price": "10"})
    assert "invalid_rating" in validate_record({**GOOD_BOOK, "rating": 6})


def test_quote_needs_author_but_not_price():
    q = {"source": "Quotes to Scrape", "name_or_title": "q", "source_url": "http://x.com",
         "price": None, "rating": None, "author": "Someone"}
    assert validate_record(q) == []
    assert validate_record({**q, "author": None}) == ["missing_author"]
