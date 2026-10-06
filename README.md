# Multi-Source Web Scraper

A Python pipeline that scrapes **Books to Scrape** and **Quotes to Scrape**, cleans and validates the data, removes duplicates, and saves one CSV, a JSON summary and a log file.

**Flow:** Scrape → Clean → Validate → Deduplicate → Save

## Requirements
- Python 3.10 – 3.12
- Libraries: `requests`, `beautifulsoup4`, `lxml`, `pytest` (tests only)

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## How to run
```bash
python main.py                  # full run (~10-15 min, visits every book page)
python main.py --no-details     # fast run, skips book detail pages
python main.py --max-pages 2    # quick test
python main.py --delay 1.0      # slower, politer
python -m pytest                # unit tests (no internet needed)
```

## Output files
| File | Contents |
| --- | --- |
| `output/final_dataset.csv` | Clean, unique records from both sites |
| `output/summary_report.json` | Counts per source: collected, rejected, duplicates, final |
| `logs/scraper.log` | Every page visited, warning and error |

## How it works

**Websites:** Both sites are plain server-rendered HTML, so `requests` + BeautifulSoup is enough. No Selenium needed.

**Pagination:** The scraper follows the "next" link (`li.next > a`) on each page until there isn't one. No page numbers are hard-coded.

**Data columns:** `source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `tags`, `description`, `scraped_at`.
Fields that don't apply are left empty (for example, quotes have no price). Nothing is invented.

**Cleaning:** Extra whitespace removed, `£51.77` becomes `51.77`, "Three" becomes `3`, quote marks stripped, tags lowercased and sorted.

**Validation:** Records are rejected if they have a missing name, invalid URL, invalid price or rating, or (for quotes) a missing author. Rejections are logged and counted by reason, and the run continues.

**Deduplication:** Each record gets a fingerprint (SHA-256 of normalised fields). Books use source + title. Quotes use source + author + first 50 characters of the text. The first copy is kept and later ones are removed.

**Error handling:**
- Requests use a timeout and retry with backoff on 429/500/502/503/504 errors.
- If a listing page fails, that source stops but already collected records are kept and the other source still runs.
- If a book detail page fails, that book just has an empty category and description.
- Missing HTML elements give empty values instead of crashing.

## Assumptions
- A quote's `source_url` is the listing page it appeared on, since quotes have no page of their own.
- `rejected_by_reason` can add up to more than `rejected_total`, because one record can fail several checks.
- A quote with no author is invalid.

## Known limitations
- Scraping is sequential, so a full run takes 10-15 minutes.
- If a listing page fails after retries, the rest of that source is skipped.
- Book availability is scraped but not included in the output.
- No resume/checkpoint support.

## Project structure
```
Multi-Source-Web-Scraping-Data-Consolidation-Pipeline/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── .gitignore
├── scrapers/
│   ├── base_scraper.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── cleaning.py
│   ├── transform.py
│   ├── validation.py
│   └── deduplication.py
├── tests/
│   ├── test_cleaning.py
│   ├── test_validation.py
│   ├── test_deduplication.py
│   ├── test_scrapers.py
│   └── test_pipeline.py
├── output/
└── logs/
```

## AI usage
See [AI_USAGE.md](AI_USAGE.md).
