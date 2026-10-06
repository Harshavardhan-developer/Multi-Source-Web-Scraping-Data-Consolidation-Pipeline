# AI Usage

> **Candidate: edit this file so it reflects what *you* actually did.** The assignment requires honesty and that you can
> explain every line. The draft below is accurate about how this code base was produced; adjust it to your own process.

## Tools used
- **Claude (Anthropic)** – generated the initial project, tests and documentation from the assignment brief.

## What it was used for
- Project structure, data model, scrapers (pagination, selectors), cleaning/validation/dedup modules, `main.py`, unit tests, README.

## Representative prompts
1. "Build the project described in the assignment documents: scrape Books to Scrape and Quotes to Scrape, clean, validate, deduplicate, output CSV + JSON summary + log."
2. (Add your own follow-up prompts here.)

## Which parts were AI-assisted
All of the code and documentation in the first draft. (State which parts you later changed yourself.)

## Changes made after reviewing AI output
- *(Fill in – e.g. adjusted delay, changed quote `source_url` choice, edited selectors after inspecting the sites.)*

## Incorrect / incomplete AI output discovered
- During generation, a shell command using brace expansion failed under `/bin/sh` and had to be rerun; an initial `clean_tags` expression was needlessly convoluted and was simplified.
- *(Add anything you find during your own review/live run.)*

## How the solution was tested
- `python -m pytest` – 20 offline unit tests (cleaning, validation, deduplication, parsing with canned HTML, pagination, page-failure handling, count reconciliation).
- An end-to-end dry run of `main.py` against a fake in-memory session confirmed CSV/JSON are written and counts reconcile.
- **Live run against the real websites was NOT possible in the generation environment (no access to those domains).**
  You must run `python main.py`, then check: both sources in the CSV, ~1,000 books + 100 quotes, prices numeric, ratings 1–5,
  JSON `final_record_count` equals the CSV row count, `reconciles: true`.
