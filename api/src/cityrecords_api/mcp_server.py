from datetime import date

from fastmcp import FastMCP

from . import queries
from .schemas import Notice, Stats

mcp = FastMCP("city-records")


def _d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def _compact(n: dict) -> dict:
    return Notice.from_row(n).model_dump(mode="json", exclude_none=True)


@mcp.tool
def search_notices(
    q: str | None = None, agency: str | None = None, notice_type: str | None = None,
    product_category: str | None = None, is_software: bool | None = None,
    min_amount: float | None = None, from_date: str | None = None,
    to_date: str | None = None, limit: int = 20,
) -> dict:
    """Search NYC City Record procurement notices (solicitations, awards, etc.).

    q is a web-style full-text query (quoted phrases, OR, -exclude). Other args are
    exact-match filters (agency, notice_type such as 'Solicitation' or 'Award',
    product_category, is_software) or ranges (min_amount in USD; from_date/to_date as
    YYYY-MM-DD on publication date). Returns {items, total, has_more}; limit max 100.
    """
    r = queries.search_notices(
        q=q, agency=agency, notice_type=notice_type, product_category=product_category,
        is_software=is_software, min_amount=min_amount, from_date=_d(from_date),
        to_date=_d(to_date), limit=max(1, min(limit, 100)), offset=0)
    return {"items": [_compact(n) for n in r["items"]], "total": r["total"], "has_more": r["has_more"]}


@mcp.tool
def get_notice(request_id: str) -> dict:
    """Get one notice by its request_id, including vendor, AI enrichment and source_url.
    Returns {"error": "not found"} if absent."""
    n = queries.get_notice(request_id)
    return _compact(n) if n else {"error": "not found"}


@mcp.tool
def vendor_history(vendor_name: str) -> list[dict]:
    """Find vendors whose name contains vendor_name (case-insensitive) and return each
    vendor (id, name, address, first_seen) with their notices, newest first."""
    out = []
    for v in queries.find_vendors(vendor_name):
        out.append({**{k: (str(v[k]) if k == "first_seen" and v[k] else v[k])
                       for k in ("id", "name", "address", "first_seen")},
                    "notices": [_compact(n) for n in v["notices"]]})
    return out


@mcp.tool
def stats(from_date: str | None = None, to_date: str | None = None) -> dict:
    """Aggregate statistics: total notices, open solicitations, awarded USD, distinct
    vendors, weekly series by notice type, top 10 agencies, and product-category counts.
    Optional from_date/to_date (YYYY-MM-DD) filter on publication date."""
    return Stats(**queries.stats(_d(from_date), _d(to_date))).model_dump(mode="json")
