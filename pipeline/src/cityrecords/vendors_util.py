"""Fuzzy vendor matching against a preloaded set of normalized names."""
from __future__ import annotations

from rapidfuzz import fuzz, process

THRESHOLD = 92


def match_vendor(normalized: str, known: dict[str, int], threshold: int = THRESHOLD) -> int | None:
    """Return the id of the best matching known vendor, or None."""
    if not normalized or not known:
        return None
    if normalized in known:
        return known[normalized]
    hit = process.extractOne(normalized, known.keys(), scorer=fuzz.token_set_ratio, score_cutoff=threshold)
    return known[hit[0]] if hit else None
