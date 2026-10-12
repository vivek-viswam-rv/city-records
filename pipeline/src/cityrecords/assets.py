
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor

import dagster as dg
from sqlalchemy import text

from . import enrich as enrich_mod
from .resources import Bedrock, ObjectStore, Postgres, Socrata
from .text import normalize_vendor, row_to_notice
from .vendors_util import match_vendor

daily_partitions = dg.DailyPartitionsDefinition(start_date="2026-09-01")
GROUP = "cityrecord"

NOTICE_COLS = [
    "request_id", "published_on", "end_date", "section", "notice_type", "agency", "category", "title",
    "description", "selection_method", "pin", "contact_name", "contact_email", "contract_amount",
    "vendor_name_raw", "event_date", "content_sha256", "s3_key",
]
UPSERT_NOTICE = text(
    f"insert into cr.notices ({', '.join(NOTICE_COLS)}) values ({', '.join(':' + c for c in NOTICE_COLS)}) "
    "on conflict (request_id) do update set "
    + ", ".join(f"{c} = excluded.{c}" for c in NOTICE_COLS if c != "request_id")
)


@dg.asset(partitions_def=daily_partitions, group_name=GROUP, kinds={"python", "postgres", "s3"},
          description="Raw City Record procurement notices for the day, stored in S3 and upserted into cr.notices.")
def raw_notices(context: dg.AssetExecutionContext, socrata: Socrata, store: ObjectStore, db: Postgres) -> dg.MaterializeResult:
    day = context.partition_key
    rows = socrata.fetch_day(day)
    key = f"notices/{day}.json"
    store.put_json(key, rows)
    notices = {}
    for r in rows:
        if r.get("request_id"):
            n = row_to_notice(r)
            n["s3_key"] = key
            notices[n["request_id"]] = n
    new = changed = 0
    engine = db.engine()
    with engine.begin() as conn:
        if notices:
            existing = dict(conn.execute(
                text("select request_id, content_sha256 from cr.notices where request_id = any(:ids)"),
                {"ids": list(notices)},
            ).all())
            for rid, n in notices.items():
                if rid not in existing:
                    new += 1
                elif existing[rid] != n["content_sha256"]:
                    changed += 1
            conn.execute(UPSERT_NOTICE, list(notices.values()))
    return dg.MaterializeResult(metadata={"rows": len(rows), "new": new, "changed": changed, "s3_key": key})


class EnrichConfig(dg.Config):
    """only_missing=True enriches just the notices that have no row yet, skipping rows whose content or
    prompt version changed. Used to backfill gaps without paying to re-enrich a whole day."""

    only_missing: bool = False


MAX_UNENRICHED_RATIO = 0.05


@dg.asset(
    deps=[raw_notices], partitions_def=daily_partitions, group_name=GROUP, kinds={"python", "postgres"},
    retry_policy=dg.RetryPolicy(max_retries=3, delay=15, backoff=dg.Backoff.EXPONENTIAL),
    code_version=enrich_mod.PROMPT_VERSION,
    check_specs=[dg.AssetCheckSpec(
        name="enrichment_coverage", asset="enriched_notices",
        description=f"At most {MAX_UNENRICHED_RATIO:.0%} of the day's notices may be left without an enrichment.",
    )],
    description="LLM (Bedrock) enrichment of notices: what is bought, category, software flag, summary.",
)
def enriched_notices(
    context: dg.AssetExecutionContext, config: EnrichConfig, bedrock: Bedrock, db: Postgres,
) -> Iterator[dg.MaterializeResult | dg.AssetCheckResult]:
    stale = "e.request_id is null" if config.only_missing else (
        "e.request_id is null or e.content_sha256 <> n.content_sha256 or e.prompt_version <> :pv")
    engine = db.engine()
    with engine.connect() as conn:
        todo = [dict(r._mapping) for r in conn.execute(text(
            "select n.* from cr.notices n left join cr.enrichments e using (request_id) "
            f"where n.published_on = :d and ({stale})"),
            {"d": context.partition_key, "pv": enrich_mod.PROMPT_VERSION})]
    client = bedrock.client()
    results, failed = [], 0

    def work(n):
        try:
            return n, *enrich_mod.enrich_notice(client, bedrock.model_id, n)
        except Exception as e:  # noqa: BLE001
            context.log.warning(f"enrichment failed for {n['request_id']}: {e}")
            return n, None, None

    with ThreadPoolExecutor(max_workers=4) as ex:
        for n, enr, usage in ex.map(work, todo):
            if enr is None:
                failed += 1
            else:
                results.append({
                    "request_id": n["request_id"], **enr.model_dump(), "model": bedrock.model_id,
                    "prompt_version": enrich_mod.PROMPT_VERSION, "content_sha256": n["content_sha256"],
                })
    enrich_mod.flush()
    if results:
        with engine.begin() as conn:
            conn.execute(text(
                "insert into cr.enrichments (request_id, what_is_bought, product_category, is_software, is_renewal, "
                "summary, keywords, confidence, model, prompt_version, content_sha256, enriched_at) values "
                "(:request_id, :what_is_bought, :product_category, :is_software, :is_renewal, :summary, :keywords, "
                ":confidence, :model, :prompt_version, :content_sha256, now()) "
                "on conflict (request_id) do update set what_is_bought=excluded.what_is_bought, "
                "product_category=excluded.product_category, is_software=excluded.is_software, "
                "is_renewal=excluded.is_renewal, summary=excluded.summary, keywords=excluded.keywords, "
                "confidence=excluded.confidence, model=excluded.model, prompt_version=excluded.prompt_version, "
                "content_sha256=excluded.content_sha256, enriched_at=now()"), results)
    mean = sum(r["confidence"] for r in results) / len(results) if results else 0.0
    if todo and failed == len(todo):
        raise dg.Failure(f"all {failed} enrichment calls failed")  # triggers retry policy
    with engine.connect() as conn:
        total, unenriched = conn.execute(text(
            "select count(*), count(*) filter (where e.request_id is null) from cr.notices n "
            "left join cr.enrichments e using (request_id) where n.published_on = :d"), {"d": context.partition_key}).one()
    ratio = unenriched / total if total else 0.0
    yield dg.MaterializeResult(metadata={
        "calls": len(todo), "failed": failed, "mean_confidence": round(mean, 4),
        "notices": total, "unenriched": unenriched,
    })
    yield dg.AssetCheckResult(
        passed=ratio <= MAX_UNENRICHED_RATIO,
        metadata={"notices": total, "unenriched": unenriched, "unenriched_ratio": round(ratio, 4)},
    )


@dg.asset(deps=[enriched_notices], partitions_def=daily_partitions, group_name=GROUP, kinds={"python", "postgres"},
          description="Canonical vendor table: normalise and fuzzy-match vendor names from the day's notices.")
def vendors(context: dg.AssetExecutionContext, db: Postgres) -> dg.MaterializeResult:
    engine = db.engine()
    new = matched = 0
    with engine.begin() as conn:
        known = {r[0]: r[1] for r in conn.execute(text("select normalized_name, id from cr.vendors"))}
        pending = conn.execute(text(
            "select request_id, vendor_name_raw from cr.notices where published_on = :d "
            "and vendor_name_raw is not null and vendor_id is null"), {"d": context.partition_key}).all()
        for request_id, raw in pending:
            norm = normalize_vendor(raw)
            if not norm:
                continue
            vid = match_vendor(norm, known)
            if vid is None:
                vid = conn.execute(text(
                    "insert into cr.vendors (name, normalized_name, first_seen) values (:n, :nn, :d) "
                    "on conflict (normalized_name) do update set normalized_name = excluded.normalized_name "
                    "returning id"), {"n": raw, "nn": norm, "d": context.partition_key}).scalar_one()
                known[norm] = vid
                new += 1
            else:
                matched += 1
            conn.execute(text("update cr.notices set vendor_id = :v where request_id = :r"), {"v": vid, "r": request_id})
    return dg.MaterializeResult(metadata={"new": new, "matched": matched})
