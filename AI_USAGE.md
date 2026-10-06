# AI Usage

## Tool used
- **Claude (Anthropic)** was used to generate the first draft of the project from the assignment brief.

## What AI helped with
- Project structure and data model
- Scrapers for Books to Scrape and Quotes to Scrape (pagination, selectors)
- Cleaning, validation and deduplication modules
- `main.py`, unit tests and this README

## Prompts I used
1. "Build the project from the assignment: scrape Books to Scrape and Quotes to Scrape, clean, validate, deduplicate, and output a CSV, a JSON summary and a log."

## What I changed after reviewing
- [e.g. adjusted request delay, changed the quote `source_url`, fixed selectors after inspecting the sites]

## Problems I found in the AI output
- A shell command with brace expansion failed under `/bin/sh` and had to be rerun.
- The first `clean_tags` expression was overly complicated, so it was simplified.
- [Add anything you find in your own review or live run]

## How I tested
- **Unit tests:** `python -m pytest` runs 20 offline tests covering cleaning, validation, deduplication, HTML parsing, pagination, page-failure handling and count reconciliation.
- **Dry run:** `main.py` was run against a fake in-memory session. CSV and JSON were written and the counts matched.
- **Live run:** not possible in the generation environment (no access to the real sites), so I ran it myself:
  - `python main.py`
  - Check that both sources appear in the CSV (about 1,000 books and 100 quotes)
  - Prices are numeric and ratings are 1 to 5
  - `final_record_count` in the JSON equals the CSV row count
  - `reconciles` is `true`
