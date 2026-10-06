from processing.deduplication import find_duplicates, make_fingerprint


def test_book_duplicates_ignore_case_spaces_punctuation():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
        {**base, "name_or_title": "Example, Book Title!"},
        {**base, "name_or_title": "Another Book"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 2 and len(dupes) == 3


def test_quote_uses_author_and_first_50_chars():
    base = {"source": "Quotes to Scrape"}
    a = {**base, "author": "Albert Einstein", "name_or_title": "Imagination is more important than knowledge."}
    b = {**base, "author": "ALBERT  EINSTEIN", "name_or_title": "imagination IS more important than knowledge"}
    c = {**base, "author": "Someone Else", "name_or_title": a["name_or_title"]}
    assert make_fingerprint(a) == make_fingerprint(b)
    assert make_fingerprint(a) != make_fingerprint(c)


def test_same_text_in_different_sources_is_not_duplicate():
    a = {"source": "Books to Scrape", "name_or_title": "X", "author": None}
    b = {"source": "Quotes to Scrape", "name_or_title": "X", "author": "X"}
    assert len(find_duplicates([a, b])[0]) == 2
