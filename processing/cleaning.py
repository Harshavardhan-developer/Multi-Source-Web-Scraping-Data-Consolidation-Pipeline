"""Small pure cleaning functions: value in, value out. No internet, no files."""
import re
from urllib.parse import urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
_QUOTE_CHARS = "\u201c\u201d\u2018\u2019\"'"


def clean_text(value):
    """Collapse all whitespace (incl. \\xa0). Empty -> None."""
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    """Remove curly/straight quotation marks around a quote."""
    text = clean_text(value)
    if text is None:
        return None
    text = text.strip(_QUOTE_CHARS).strip()
    return text or None


def clean_price(raw):
    """'£51.77' -> 51.77. Unparsable -> None."""
    if not raw:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw):
    """'star-rating Three' / 'Three' -> 3. Unknown -> None."""
    for word in (raw or "").lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    """Lowercase, de-duplicate, sort, join with ';'. None/empty -> None."""
    if not tags:
        return None
    cleaned = {clean_text(t).lower() for t in tags if clean_text(t)}
    return ";".join(sorted(cleaned)) or None


def normalize_url(url):
    """Return a stripped URL if it is http(s) with a host, else None."""
    url = clean_text(url)
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url
    return None
