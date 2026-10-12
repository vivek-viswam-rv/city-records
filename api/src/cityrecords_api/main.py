import os
from datetime import date

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import db, queries
from .auth import ApiKeyMiddleware
from .mcp_server import mcp
from .schemas import Filters, Notice, NoticeList, Stats, VendorDetail

if os.environ.get("HONEYBADGER_API_KEY"):
    from honeybadger import honeybadger

    # Honeybadger environments are used per component (frontend / backend / pipeline), not per stage.
    honeybadger.configure(api_key=os.environ["HONEYBADGER_API_KEY"], environment="backend")
else:
    honeybadger = None

mcp_app = mcp.http_app(path="/mcp", stateless_http=True)
app = FastAPI(title="city-records API", lifespan=mcp_app.lifespan)


ERROR_TAGS = ["backend", "bug"]  # Honeybadger's GitHub integration turns these into issue labels


@app.exception_handler(Exception)
async def _catch_all(request: Request, exc: Exception):
    if honeybadger:
        honeybadger.notify(exc, context={"path": request.url.path, "method": request.method}, tags=ERROR_TAGS)
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)


@app.get("/debug/raise", include_in_schema=False)
async def debug_raise():
    """Error-reporting smoke test (needs the API key like every other route): raises so the
    catch-all handler reports a tagged fault to Honeybadger. Harmless, and it never touches the DB."""
    raise RuntimeError("Honeybadger smoke test from /debug/raise")


@app.get("/health")
def health():
    return {"status": "ok", "db": db.db_ok()}


@app.get("/filters", response_model=Filters)
def filters():
    return queries.list_filters()


@app.get("/notices", response_model=NoticeList)
def notices(
    q: str | None = None, agency: str | None = None, notice_type: str | None = None,
    category: str | None = None, product_category: str | None = None,
    is_software: bool | None = None, min_amount: float | None = None,
    from_: date | None = Query(None, alias="from"), to: date | None = None,
    limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0),
):
    r = queries.search_notices(
        q=q, agency=agency, notice_type=notice_type, category=category,
        product_category=product_category, is_software=is_software, min_amount=min_amount,
        from_date=from_, to_date=to, limit=limit, offset=offset)
    return NoticeList(items=[Notice.from_row(i) for i in r["items"]],
                      total=r["total"], has_more=r["has_more"])


@app.get("/notices/{request_id}", response_model=Notice)
def notice(request_id: str):
    n = queries.get_notice(request_id)
    if not n:
        raise HTTPException(404, "Notice not found")
    return Notice.from_row(n)


@app.get("/vendors/{vendor_id}", response_model=VendorDetail)
def vendor(vendor_id: int):
    v = queries.get_vendor(vendor_id)
    if not v:
        raise HTTPException(404, "Vendor not found")
    return VendorDetail(**{**v, "notices": [Notice.from_row(n) for n in v["notices"]]})


@app.get("/stats", response_model=Stats)
def stats(from_: date | None = Query(None, alias="from"), to: date | None = None):
    return queries.stats(from_, to)


# MCP at /mcp (mounted last so REST routes take precedence).
app.mount("/", mcp_app)

app.add_middleware(ApiKeyMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], expose_headers=["mcp-session-id"])
