import os
from datetime import date

import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "k"
from cityrecords_api import queries  # noqa: E402
from cityrecords_api.main import app  # noqa: E402

H = {"x-api-key": "k"}
NOTICE = {
    "request_id": "R1", "published_on": date(2026, 1, 2), "end_date": None, "section": "s",
    "notice_type": "Award", "agency": "DOT", "category": "c", "title": "t", "description": "d",
    "selection_method": None, "pin": None, "contact_name": None, "contact_email": None,
    "contract_amount": 12.5, "vendor_name_raw": "Acme", "vendor": {"id": 1, "name": "Acme"},
    "event_date": None, "enrichment": None,
}


@pytest.fixture(scope="module")
def client():
    # The MCP session manager's lifespan can only run once per process: single module-scoped client.
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(queries, "list_filters", lambda: {
        "agencies": ["DOT"], "notice_types": ["Award"], "categories": [], "product_categories": []})
    monkeypatch.setattr(queries, "search_notices", lambda **k: {"items": [NOTICE], "total": 1, "has_more": False})
    monkeypatch.setattr(queries, "get_notice", lambda rid: NOTICE if rid == "R1" else None)
    monkeypatch.setattr(queries, "get_vendor", lambda i: {
        "id": 1, "name": "Acme", "address": None, "first_seen": date(2026, 1, 1), "notices": [NOTICE]} if i == 1 else None)
    monkeypatch.setattr(queries, "stats", lambda f=None, t=None: {
        "notices": 1, "open_solicitations": 0, "awarded_usd": 12.5, "vendors": 1,
        "by_week": [{"week": date(2025, 12, 29), "notice_type": "Award", "usd": 12.5, "count": 1}],
        "by_agency": [{"agency": "DOT", "count": 1, "usd": 12.5}],
        "by_product_category": []})
    with TestClient(app) as c:
        yield c
    monkeypatch.undo()


def test_health_open(client):
    assert client.get("/health").json()["status"] == "ok"


@pytest.mark.parametrize("p", ["/filters", "/notices", "/notices/R1", "/vendors/1", "/stats", "/mcp"])
def test_auth_required(client, p):
    assert client.get(p).status_code == 401
    assert client.get(p, headers={"x-api-key": "bad"}).status_code == 401


def test_notices_shape(client):
    r = client.get("/notices?limit=2", headers=H).json()
    assert set(r) == {"items", "total", "has_more"}
    n = r["items"][0]
    assert n["published_on"] == "2026-01-02" and n["contract_amount"] == 12.5
    assert n["source_url"].endswith("/RequestDetail/R1") and n["vendor"] == {"id": 1, "name": "Acme"}


def test_404s(client):
    assert client.get("/notices/nope", headers=H).status_code == 404
    assert client.get("/vendors/9", headers=H).status_code == 404


def test_vendor_stats_filters(client):
    assert client.get("/vendors/1", headers=H).json()["notices"][0]["request_id"] == "R1"
    s = client.get("/stats", headers=H).json()
    assert s["by_week"][0]["week"] == "2025-12-29" and s["awarded_usd"] == 12.5
    assert client.get("/filters", headers=H).json()["agencies"] == ["DOT"]


def test_limit_max(client):
    assert client.get("/notices?limit=101", headers=H).status_code == 422


@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("DATABASE_POOL_URL"), reason="no DATABASE_POOL_URL")
def test_real_db():
    import importlib

    q = importlib.reload(queries)  # undo any stubs
    assert {"items", "total", "has_more"} <= set(q.search_notices(limit=2))
    q.stats()
    q.list_filters()
