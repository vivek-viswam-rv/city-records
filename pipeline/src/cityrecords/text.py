"""Pure helpers: HTML stripping, hashing, row normalisation, vendor normalisation."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

VENDOR_SUFFIXES = {"inc", "llc", "ltd", "corp", "corporation", "co", "company", "the"}


def strip_html(html: str | None) -> str:
    if not html:
        return ""
    text = BeautifulSoup(html, "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def content_sha256(title: str | None, description: str | None) -> str:
    return hashlib.sha256(f"{title or ''}\n{description or ''}".encode()).hexdigest()


def normalize_vendor(name: str | None) -> str:
    if not name:
        return ""
    s = re.sub(r"[^\w\s]", " ", name.lower())
    tokens = [t for t in s.split() if t not in VENDOR_SUFFIXES]
    return " ".join(tokens)


def _date(v: Any) -> str | None:
    return v[:10] if isinstance(v, str) and len(v) >= 10 else None


def _ts(v: Any) -> datetime | None:
    if not isinstance(v, str):
        return None
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None


def _num(v: Any) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def row_to_notice(row: dict[str, Any]) -> dict[str, Any]:
    """Map a raw Socrata row to a cr.notices row dict."""
    title = (row.get("short_title") or "").strip() or None
    description = strip_html(row.get("additional_description_1"))
    return {
        "request_id": row["request_id"],
        "published_on": _date(row.get("start_date")),
        "end_date": _date(row.get("end_date")),
        "section": row.get("section_name"),
        "notice_type": row.get("type_of_notice_description"),
        "agency": row.get("agency_name"),
        "category": row.get("category_description"),
        "title": title,
        "description": description,
        "selection_method": row.get("selection_method_description"),
        "pin": row.get("pin"),
        "contact_name": row.get("contact_name"),
        "contact_email": row.get("email"),
        "contract_amount": _num(row.get("contract_amount")),
        "vendor_name_raw": (row.get("vendor_name") or "").strip() or None,
        "event_date": _ts(row.get("event_date")),
        "content_sha256": content_sha256(title, description),
    }
