import hashlib

import pytest

from cityrecords import enrich
from cityrecords.defs.automation import previous_business_day_key
from cityrecords.text import content_sha256, normalize_vendor, row_to_notice, strip_html
from cityrecords.vendors_util import match_vendor

from .fakes import GOOD, GOOD_JSON, FakeBedrock


def test_strip_html():
    assert strip_html("<p>Renewal of <b>software</b>&nbsp;licenses &amp; more</p><br/>x") == "Renewal of software licenses & more x"
    assert strip_html(None) == ""


def test_sha256():
    assert content_sha256("T", "D") == hashlib.sha256(b"T\nD").hexdigest()


def test_row_mapping(socrata_rows):
    n = [row_to_notice(r) for r in socrata_rows]
    assert n[0]["published_on"] == "2026-10-09" and n[0]["end_date"] == "2026-10-23"
    assert "<" not in n[0]["description"] and "software licenses for the student information system" in n[0]["description"]
    assert n[1]["contract_amount"] == 1250000.50 and n[1]["vendor_name_raw"] == "Acme Paving, Inc."
    assert n[2]["event_date"].year == 2026 and n[2]["contract_amount"] is None
    assert n[0]["content_sha256"] == content_sha256(n[0]["title"], n[0]["description"])


def test_vendor_normalization_and_match(socrata_rows):
    assert normalize_vendor("Acme Paving, Inc.") == "acme paving"
    assert normalize_vendor("The Foo-Bar Co.") == "foo bar"
    assert normalize_vendor("ACME PAVING INC") == "acme paving"
    known = {"acme paving": 1, "zeta corp consulting": 2}
    assert match_vendor(normalize_vendor("ACME PAVING INC"), known) == 1
    assert match_vendor("acme pavng", known) == 1  # typo, fuzzy
    assert match_vendor("totally different", known) is None
    assert match_vendor("", known) is None


def test_parse_plain_and_fenced():
    assert enrich.parse_enrichment(GOOD_JSON).product_category == "software"
    assert enrich.parse_enrichment(f"```json\n{GOOD_JSON}\n```").is_renewal is True
    assert enrich.parse_enrichment(f"Here you go: {GOOD_JSON}").confidence == 0.9


def test_reasoning_first_response_shape():
    client = FakeBedrock([GOOD_JSON], reasoning_first=True)
    enr, usage = enrich.enrich_notice(client, "m", {"request_id": "1", "title": "t"})
    assert enr.model_dump() == GOOD and usage["totalTokens"] == 150
    kw = client.calls[0]
    assert kw["inferenceConfig"] == {"maxTokens": 600, "temperature": 0} and kw["modelId"] == "m"


def test_retry_once_then_success_and_failure():
    client = FakeBedrock(["not json", f"```json\n{GOOD_JSON}\n```"])
    enr, usage = enrich.enrich_notice(client, "m", {"request_id": "1"})
    assert enr.is_software and len(client.calls) == 2 and usage["totalTokens"] == 300
    assert "invalid" in client.calls[1]["messages"][-1]["content"][0]["text"]
    bad = FakeBedrock(['{"what_is_bought": "x"}'])
    with pytest.raises(enrich.EnrichmentError):
        enrich.enrich_notice(bad, "m", {"request_id": "1"})
    assert len(bad.calls) == 2


def test_invalid_category_rejected():
    with pytest.raises(ValueError):
        enrich.parse_enrichment(GOOD_JSON.replace('"software"', '"bogus"', 1))


def test_previous_business_day():
    from datetime import datetime
    assert previous_business_day_key(datetime(2026, 10, 12)) == "2026-10-09"  # Mon -> Fri
    assert previous_business_day_key(datetime(2026, 10, 13)) == "2026-10-12"


def test_no_text_block_retries_with_bigger_budget():
    class Reasoning(FakeBedrock):
        def converse(self, **kw):
            r = super().converse(**kw)
            if len(self.calls) == 1:
                r["output"]["message"]["content"] = [{"reasoningContent": {"reasoningText": {"text": "..."}}}]
            return r
    c = Reasoning([GOOD_JSON])
    enr, _ = enrich.enrich_notice(c, "m", {"request_id": "1"})
    assert enr.is_software and c.calls[1]["inferenceConfig"]["maxTokens"] > 600


def test_repairs_stray_quote_after_number_and_trailing_comma():
    assert enrich.parse_enrichment(GOOD_JSON.replace("0.9}", '0.9"}')).confidence == 0.9
    assert enrich.parse_enrichment(GOOD_JSON.replace("0.9}", "0.9,}")).confidence == 0.9
    assert enrich.repair_json('{"a": "x"}') == '{"a": "x"}'  # quotes that close a string are left alone


def test_requests_low_reasoning_effort():
    client = FakeBedrock([GOOD_JSON])
    enrich.enrich_notice(client, "m", {"request_id": "1"})
    assert client.calls[0]["additionalModelRequestFields"] == {"reasoning_effort": "low"}


def test_empty_description_gets_explicit_placeholder():
    assert "none provided" in enrich.build_user_prompt({"title": "Lead Abatement", "description": ""})
    assert "none provided" not in enrich.build_user_prompt({"title": "t", "description": "Real text"})


def test_each_bedrock_call_is_recorded_as_a_generation(monkeypatch):
    from contextlib import contextmanager

    class Gen:
        def __init__(self):
            self.updates = []

        def update(self, **kw):
            self.updates.append(kw)

    opened, gens = [], []

    @contextmanager
    def fake_generation(**kwargs):
        opened.append(kwargs)
        g = Gen()
        gens.append(g)
        yield g

    monkeypatch.setattr(enrich, "_generation", fake_generation)
    client = FakeBedrock(["not json", GOOD_JSON])
    enrich.enrich_notice(client, "openai.gpt-oss-20b-1:0", {"request_id": "1", "title": "t"})
    assert len(opened) == 2 and len(gens) == 2
    first = opened[0]
    assert first["model"] == "openai.gpt-oss-20b-1:0"
    assert first["input"][0] == {"role": "system", "content": enrich.SYSTEM_PROMPT}
    assert first["model_parameters"] == {"max_tokens": 600, "temperature": 0, "reasoning_effort": "low"}
    assert gens[0].updates[0]["usage_details"] == {"input": 100, "output": 50, "total": 150}
    assert gens[0].updates[0]["output"] == "not json"
    assert opened[1]["metadata"]["attempt"] == 1 and opened[1]["model_parameters"]["temperature"] == 0.3
