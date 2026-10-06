from processing.cleaning import (clean_price, clean_rating, clean_tags, clean_text,
                                 normalize_url, strip_quotes)


def test_clean_text():
    assert clean_text("  Hello \n\t World\xa0! ") == "Hello World !"
    assert clean_text("   ") is None
    assert clean_text(None) is None


def test_strip_quotes():
    assert strip_quotes("\u201cThe world.\u201d") == "The world."
    assert strip_quotes("\u201c\u201d") is None


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("Â£1,051.77") == 1051.77
    assert clean_price("free") is None
    assert clean_price(None) is None


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating("Five") == 5
    assert clean_rating("star-rating") is None
    assert clean_rating(None) is None


def test_clean_tags():
    assert clean_tags(["Love", " books ", "love"]) == "books;love"
    assert clean_tags([]) is None


def test_normalize_url():
    assert normalize_url(" https://a.com/x ") == "https://a.com/x"
    assert normalize_url("/relative/path") is None
    assert normalize_url("ftp://a.com") is None
