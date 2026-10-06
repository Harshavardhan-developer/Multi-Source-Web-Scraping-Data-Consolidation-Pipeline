"""Run the whole pipeline:  python main.py

Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save files
"""
import argparse
import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone

import config
from processing.deduplication import find_duplicates
from processing.transform import CLEANERS
from processing.validation import validate_record
from scrapers.base_scraper import create_session
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

logger = logging.getLogger("pipeline")


def setup_logging():
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    for handler in (logging.StreamHandler(),
                    logging.FileHandler(config.LOG_DIR / "scraper.log", mode="w", encoding="utf-8")):
        handler.setFormatter(fmt)
        root.addHandler(handler)


def parse_args():
    p = argparse.ArgumentParser(description="Multi-source scraping & consolidation pipeline")
    p.add_argument("--no-details", action="store_true",
                   help="Skip book detail pages (faster; category/description stay empty)")
    p.add_argument("--delay", type=float, default=config.REQUEST_DELAY,
                   help="Seconds to pause between requests (default 0.5)")
    p.add_argument("--max-pages", type=int, default=None,
                   help="Limit pages per source (for quick test runs)")
    return p.parse_args()


def clean_and_validate(source_name, raw_records):
    """Clean + validate one source. Returns (valid_records, stats)."""
    cleaner = CLEANERS[source_name]
    valid, cleaned_count, rejected = [], 0, Counter()
    for raw in raw_records:
        try:
            rec = cleaner(raw)
        except Exception:
            logger.exception("[%s] Cleaning crashed for record %r", source_name, raw)
            rejected["cleaning_error"] += 1
            continue
        cleaned_count += 1
        problems = validate_record(rec)
        if problems:
            logger.warning("[%s] Rejected %s: %s", source_name, problems, rec.get("name_or_title"))
            for reason in problems:
                rejected[reason] += 1
            rejected["_records"] += 1
            continue
        valid.append(rec)
    rejected_total = len(raw_records) - len(valid)
    rejected_by_reason = {k: v for k, v in rejected.items() if k != "_records"}
    return valid, {
        "raw_collected": len(raw_records),
        "after_cleaning": cleaned_count,
        "rejected_total": rejected_total,
        "rejected_by_reason": rejected_by_reason,  # a record can have >1 reason
    }


def write_csv(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=config.COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def write_summary(stats, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


def main():
    args = parse_args()
    setup_logging()
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    session = create_session()

    scrapers = [
        BooksScraper(session=session, delay=args.delay, max_pages=args.max_pages,
                     fetch_details=not args.no_details),
        QuotesScraper(session=session, delay=args.delay, max_pages=args.max_pages),
    ]

    all_valid, per_source = [], {}
    for scraper in scrapers:
        try:                                    # one source failing must not stop the other
            raw = scraper.scrape_all()
        except Exception:
            logger.exception("[%s] Source failed completely", scraper.name)
            raw = []
        valid, stats = clean_and_validate(scraper.name, raw)
        per_source[scraper.name] = stats
        all_valid.extend(valid)

        unique, dupes = find_duplicates(all_valid)
    dupe_counts = Counter(d["source"] for d in dupes)

    for d in dupes:
        logger.warning(
            "Duplicate removed: [%s] %s | %s | price=%s",
            d["source"],
            d["name_or_title"],
            d["source_url"],
            d["price"],
        )

    for name, stats in per_source.items():
        stats["duplicates_removed"] = dupe_counts.get(name, 0)
        stats["final_count"] = stats["raw_collected"] - stats["rejected_total"] - stats["duplicates_removed"]

    write_csv(unique, config.OUTPUT_DIR / "final_dataset.csv")

    totals = {
        "raw_collected": sum(s["raw_collected"] for s in per_source.values()),
        "after_cleaning": sum(s["after_cleaning"] for s in per_source.values()),
        "rejected_total": sum(s["rejected_total"] for s in per_source.values()),
        "duplicates_removed": len(dupes),
        "final_record_count": len(unique),
    }
    totals["reconciles"] = (totals["raw_collected"] - totals["rejected_total"]
                            - totals["duplicates_removed"] == totals["final_record_count"])
    ended = datetime.now(timezone.utc)
    summary = {
        "per_source": per_source,
        "totals": totals,
        "run": {
            "start_time": started.isoformat(timespec="seconds"),
            "end_time": ended.isoformat(timespec="seconds"),
            "duration_seconds": round(time.perf_counter() - t0, 2),
            "book_detail_pages_fetched": not args.no_details,
        },
    }
    write_summary(summary, config.OUTPUT_DIR / "summary_report.json")
    logger.info("Finished: %d final rows (reconciles=%s)", len(unique), totals["reconciles"])


if __name__ == "__main__":
    main()
