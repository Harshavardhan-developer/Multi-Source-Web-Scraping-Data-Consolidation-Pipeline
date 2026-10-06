"""Central settings so nothing is hard-coded inside the scrapers."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

BOOKS_URL = "https://books.toscrape.com/"
QUOTES_URL = "https://quotes.toscrape.com/"

BOOKS_SOURCE = "Books to Scrape"
QUOTES_SOURCE = "Quotes to Scrape"
VALID_SOURCES = {BOOKS_SOURCE, QUOTES_SOURCE}

REQUEST_DELAY = 0.5      # seconds between requests (be polite)
REQUEST_TIMEOUT = 10     # seconds
USER_AGENT = "ScrapingAssignment/1.0 (learning project)"

COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at",
]
