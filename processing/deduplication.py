"""Fingerprint-based duplicate detection (duplicates are removed, not flagged).

Identity rules (must match the README):
  Books : source + title
  Quotes: source + author + first 50 chars of quote text
All fields are lowercased, punctuation removed, spaces collapsed, then SHA-256 hashed.
"""
import hashlib
import re

import config


def _norm(value):
    value = re.sub(r"[^\w\s]", "", str(value or "").lower())
    return " ".join(value.split())


def make_fingerprint(rec):
    if rec.get("source") == config.QUOTES_SOURCE:
        parts = [rec.get("source"), rec.get("author"), _norm(rec.get("name_or_title"))[:50]]
    else:
        parts = [rec.get("source"), rec.get("name_or_title")]
    key = " ".join(_norm(p) for p in parts)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records):
    """Return (unique, duplicates); first occurrence wins."""
    seen, unique, dupes = set(), [], []
    for rec in records:
        fp = make_fingerprint(rec)
        if fp in seen:
            dupes.append(rec)
        else:
            seen.add(fp)
            unique.append(rec)
    return unique, dupes
