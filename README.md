# Multi-Source Web Scraping & Data Consolidation

A Python ETL pipeline that scrapes **Books to Scrape** and **Quotes to Scrape**, cleans and validates
the data, removes duplicates, and writes one CSV plus a JSON summary and a log.

```
Scrape (both sites) -> Clean -> Validate -> Deduplicate -> Consolidate -> Save files
```

## Python version
3.10 – 3.12 (developed/tested logic on Python 3.12).

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Dependencies: `requests`, `beautifulsoup4`, `lxml`, `pytest` (tests only). Re-pin exact versions with
`pip freeze > requirements.txt` after your own install if you want a strict lock.

## How to run
```bash
python main.py                 # full run (visits each book detail page; ~10-15 min at 0.5 s delay)
python main.py --no-details    # fast run: skips detail pages (category/description left empty)
python main.py --max-pages 2   # quick smoke test
python main.py --delay 1.0     # slower / politer
python -m pytest               # unit tests (no internet needed)
```
Outputs: `output/final_dataset.csv`, `output/summary_report.json`, `logs/scraper.log`.

## Step 1 – Website observations
| Item | Books to Scrape | Quotes to Scrape |
| --- | --- | --- |
| One record | `article.product_pod` | `div.quote` |
| Main text | `h3 > a` (full title in `title` attribute; visible text is truncated) | `span.text` (wrapped in curly quotes) |
| Price | `p.price_color` (`£51.77`) | none |
| Rating | class on `p.star-rating` (`Three`) | none |
| Author | none | `small.author` |
| Tags | none | `a.tag` (0..n) |
| Link | `h3 > a[href]` (relative) | page URL used (see model) |
| Next page | `li.next > a` | `li.next > a` |
| Category / description | only on the book detail page (breadcrumb / `#product_description + p`) | none |

Both sites are server-rendered HTML, so **Requests + BeautifulSoup (lxml)** is sufficient; Selenium/Playwright would only add overhead.

## How pagination works
`BaseScraper.scrape_all()` starts at the home page, parses it, then looks for `li.next > a`. If present, the
relative `href` is converted with `urljoin` and the loop repeats; if absent, it stops. No page numbers are hard-coded,
so the scraper adapts if the site gains or loses pages.

## Data model
| Column | Books | Quotes |
| --- | --- | --- |
| source | Books to Scrape | Quotes to Scrape |
| source_url | Book detail page URL | URL of the listing page where the quote appeared |
| name_or_title | Book title | Quote text (curly quotes removed) |
| category | Detail-page breadcrumb (empty with `--no-details`) | empty |
| price | float (e.g. 51.77) | empty |
| rating | int 1–5 | empty |
| author | empty | Author name |
| tags | empty | `tag1;tag2` (lowercase, sorted, unique) |
| description | Detail-page description (may be empty) | empty |
| scraped_at | UTC ISO timestamp | UTC ISO timestamp |

Non-applicable fields are left empty; nothing is invented (e.g. quotes do not get a price of 0).

## Cleaning approach (`processing/cleaning.py`, `processing/transform.py`)
Small pure functions: `clean_text` (collapses whitespace incl. `\xa0`, empty -> None), `strip_quotes`, `clean_price`
(`£51.77` -> 51.77), `clean_rating` (`Three` -> 3), `clean_tags`, `normalize_url`. Responses are decoded as UTF-8 so `£` is not corrupted.

## Validation approach (`processing/validation.py`)
Returns a *list of reasons* per record: `unknown_source`, `missing_name`, `invalid_url`, `invalid_price`,
`invalid_rating`, plus `missing_author` for quotes. Invalid records are logged (WARNING), counted by reason in the
summary, and excluded; the run continues.

## Deduplication approach (`processing/deduplication.py`)
Fingerprint = SHA-256 of normalised identifying fields (lowercase, punctuation removed, whitespace collapsed):
- **Books:** source + title
- **Quotes:** source + author + first 50 characters of the (normalised) quote text

The first occurrence is kept; later ones are **removed** (not flagged) so the final CSV is directly usable and the count is
reported in the summary and log. Both sites contain unique items, so a real run is expected to find ~0 duplicates; the logic is
proven by `tests/test_deduplication.py`.

## Error-handling approach
- `requests.Session` with timeout and automatic retries (429/500/502/503/504) using exponential backoff.
- Failed page after retries: logged as ERROR, that source stops, records already collected are kept, the other source still runs.
- Failed book detail page: WARNING, that book keeps empty category/description.
- Each record is parsed/cleaned inside `try/except`; missing HTML elements give `None`, never a crash.
- Each source is wrapped in its own `try/except` in `main.py`.

## Output description
- `final_dataset.csv` – unique valid records, fixed column order, UTF-8.
- `summary_report.json` – per source: raw collected, after cleaning, rejected (with reasons), duplicates removed, final count;
  totals with a `reconciles` flag (raw − rejected − duplicates = final); start/end time and duration.
- `logs/scraper.log` – every page, warning and error.

## Assumptions
- Quote `source_url` is the listing page (quotes have no individual page).
- "Rejected" counts records; `rejected_by_reason` may sum to more than `rejected_total` because one record can fail several rules.
- A quote without an author is invalid.

## Known limitations
- Scraping is sequential (no async/parallel), so a full run with detail pages takes ~10–15 minutes.
- If a listing page fails after retries, the rest of that source is skipped rather than guessing the next URL.
- Availability is scraped raw but not part of the output schema.
- No incremental/checkpoint support.

## Project structure
```
main.py  config.py  requirements.txt
scrapers/    base_scraper.py  books_scraper.py  quotes_scraper.py
processing/  cleaning.py  transform.py  validation.py  deduplication.py
tests/       test_cleaning.py  test_validation.py  test_deduplication.py  test_scrapers.py  test_pipeline.py
output/  logs/
```

## AI usage summary
See `AI_USAGE.md`.
