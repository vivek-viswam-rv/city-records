"""Raw-SQL query layer over schema cr. Returns plain dicts (no pydantic)."""
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text

from .db import get_engine

ENRICH_FIELDS = (
    "what_is_bought product_category is_software is_renewal summary keywords "
    "confidence model prompt_version enriched_at"
).split()

NOTICE_SELECT = """
select n.request_id, n.published_on, n.end_date, n.section, n.notice_type, n.agency,
  n.category, n.title, n.description, n.selection_method, n.pin, n.contact_name,
  n.contact_email, n.contract_amount, n.vendor_name_raw, n.vendor_id, v.name as vendor_name,
  n.event_date, (e.request_id is not null) as has_enrichment,
  e.what_is_bought, e.product_category, e.is_software, e.is_renewal, e.summary, e.keywords,
  e.confidence, e.model, e.prompt_version, e.enriched_at
from cr.notices n
left join cr.vendors v on v.id = n.vendor_id
left join cr.enrichments e on e.request_id = n.request_id
"""


def _num(x: Any) -> Any:
    return float(x) if isinstance(x, Decimal) else x


def _notice(r: dict) -> dict:
    d = {k: _num(r[k]) for k in r if k not in ENRICH_FIELDS and k not in
         ("vendor_id", "vendor_name", "has_enrichment")}
    d["vendor"] = {"id": r["vendor_id"], "name": r["vendor_name"]} if r["vendor_id"] is not None else None
    d["enrichment"] = {k: _num(r[k]) for k in ENRICH_FIELDS} if r["has_enrichment"] else None
    return d


def _rows(sql: str, params: dict | None = None) -> list[dict]:
    with get_engine().connect() as c:
        return [dict(r) for r in c.execute(text(sql), params or {}).mappings()]


def list_filters() -> dict:
    def col(expr: str, table: str) -> list[str]:
        rows = _rows(f"select distinct {expr} as v from {table} where {expr} is not null order by 1")
        return [r["v"] for r in rows]

    return {
        "agencies": col("agency", "cr.notices"),
        "notice_types": col("notice_type", "cr.notices"),
        "categories": col("category", "cr.notices"),
        "product_categories": col("product_category", "cr.enrichments"),
    }


def search_notices(
    q: str | None = None, agency: str | None = None, notice_type: str | None = None,
    category: str | None = None, product_category: str | None = None,
    is_software: bool | None = None, min_amount: float | None = None,
    from_date: date | None = None, to_date: date | None = None,
    limit: int = 25, offset: int = 0,
) -> dict:
    where, p = [], {"limit": limit, "offset": offset}
    if q:
        where.append("n.search @@ websearch_to_tsquery('english', :q)")
        p["q"] = q
    for name, col, val in (
        ("agency", "n.agency", agency), ("notice_type", "n.notice_type", notice_type),
        ("category", "n.category", category), ("product_category", "e.product_category", product_category),
        ("is_software", "e.is_software", is_software),
    ):
        if val is not None:
            where.append(f"{col} = :{name}")
            p[name] = val
    if min_amount is not None:
        where.append("n.contract_amount >= :min_amount")
        p["min_amount"] = min_amount
    if from_date:
        where.append("n.published_on >= :from_date")
        p["from_date"] = from_date
    if to_date:
        where.append("n.published_on <= :to_date")
        p["to_date"] = to_date
    w = (" where " + " and ".join(where)) if where else ""
    if q:
        order = "ts_rank(n.search, websearch_to_tsquery('english', :q)) desc, n.published_on desc"
    else:
        order = "n.published_on desc, n.contract_amount desc nulls last"
    total = _rows(
        "select count(*) as c from cr.notices n left join cr.enrichments e on e.request_id = n.request_id" + w,
        {k: v for k, v in p.items() if k not in ("limit", "offset")},
    )[0]["c"]
    rows = _rows(f"{NOTICE_SELECT}{w} order by {order}, n.request_id limit :limit offset :offset", p)
    return {"items": [_notice(r) for r in rows], "total": total,
            "has_more": offset + len(rows) < total}


def get_notice(request_id: str) -> dict | None:
    rows = _rows(NOTICE_SELECT + " where n.request_id = :id", {"id": request_id})
    return _notice(rows[0]) if rows else None


def _vendor_with_notices(where: str, params: dict) -> list[dict]:
    vs = _rows(f"select id, name, address, first_seen from cr.vendors where {where} order by name limit 5", params)
    for v in vs:
        rows = _rows(NOTICE_SELECT + " where n.vendor_id = :vid order by n.published_on desc, n.request_id limit 200",
                     {"vid": v["id"]})
        v["notices"] = [_notice(r) for r in rows]
    return vs


def get_vendor(vendor_id: int) -> dict | None:
    vs = _vendor_with_notices("id = :id", {"id": vendor_id})
    return vs[0] if vs else None


def find_vendors(name: str) -> list[dict]:
    return _vendor_with_notices("name ilike :n", {"n": f"%{name}%"})


def stats(from_date: date | None = None, to_date: date | None = None) -> dict:
    where, p = [], {}
    if from_date:
        where.append("n.published_on >= :from_date")
        p["from_date"] = from_date
    if to_date:
        where.append("n.published_on <= :to_date")
        p["to_date"] = to_date
    w = (" where " + " and ".join(where)) if where else ""
    and_ = (w + " and ") if w else " where "
    head = _rows(
        "select count(*) as notices, "
        "count(*) filter (where n.notice_type='Solicitation' and (n.end_date is null or n.end_date >= current_date)) as open_solicitations, "
        "coalesce(sum(n.contract_amount) filter (where n.notice_type='Award'),0) as awarded_usd, "
        "count(distinct n.vendor_id) as vendors from cr.notices n" + w, p)[0]
    by_week = _rows(
        "select date_trunc('week', n.published_on)::date as week, n.notice_type, "
        "coalesce(sum(n.contract_amount),0) as usd, count(*) as count from cr.notices n"
        + and_ + "n.published_on is not null group by 1,2 order by 1,2", p)
    by_agency = _rows(
        "select n.agency, count(*) as count, coalesce(sum(n.contract_amount),0) as usd from cr.notices n"
        + w + " group by 1 order by 2 desc, 3 desc limit 10", p)
    by_pc = _rows(
        "select e.product_category, count(*) as count from cr.notices n join cr.enrichments e "
        "on e.request_id = n.request_id" + w + " group by 1 order by 2 desc", p)
    return {
        "notices": head["notices"], "open_solicitations": head["open_solicitations"],
        "awarded_usd": _num(head["awarded_usd"]), "vendors": head["vendors"],
        "by_week": [{**r, "usd": _num(r["usd"])} for r in by_week],
        "by_agency": [{**r, "usd": _num(r["usd"])} for r in by_agency],
        "by_product_category": by_pc,
    }
