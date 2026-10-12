"""LLM enrichment of notices via AWS Bedrock Converse, traced with Langfuse (optional)."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

PROMPT_VERSION = "v2"

ProductCategory = Literal[
    "software", "it_services", "professional_services", "construction", "facilities",
    "human_services", "health", "education", "transportation", "public_safety", "food",
    "equipment", "supplies", "consulting", "legal", "financial", "real_estate",
    "utilities", "marketing", "other",
]


class Enrichment(BaseModel):
    what_is_bought: str
    product_category: ProductCategory
    is_software: bool
    is_renewal: bool
    summary: str
    keywords: list[str]
    confidence: float = Field(ge=0, le=1)


SYSTEM_PROMPT = f"""You analyse NYC City Record procurement notices. Respond with ONLY one JSON object, no prose, no code fences.
Schema:
{{
  "what_is_bought": string, // short plain-English phrase: the good or service being procured
  "product_category": one of {list(ProductCategory.__args__)},
  "is_software": boolean, // true if software, SaaS, licences or software maintenance is procured
  "is_renewal": boolean, // true if this renews/extends an existing contract or licence
  "summary": string, // 1-2 sentences for a citizen
  "keywords": string[], // 3-8 lowercase keywords
  "confidence": number // 0..1 confidence in this analysis
}}"""


class EnrichmentError(Exception):
    pass


def build_user_prompt(n: dict[str, Any]) -> str:
    desc = (n.get("description") or "").strip()[:6000] or "(none provided; infer from the title, agency, category and vendor)"
    return (
        f"Agency: {n.get('agency')}\nSection: {n.get('section')}\nNotice type: {n.get('notice_type')}\n"
        f"Category: {n.get('category')}\nSelection method: {n.get('selection_method')}\n"
        f"Contract amount: {n.get('contract_amount')}\nVendor: {n.get('vendor_name_raw')}\n"
        f"Title: {n.get('title')}\nDescription: {desc}"
    )


def extract_text(response: dict[str, Any]) -> str:
    """First block may be reasoningContent; return the block that has a text key."""
    for block in response["output"]["message"]["content"]:
        if "text" in block:
            return block["text"]
    raise EnrichmentError("no text block in Bedrock response")


def repair_json(t: str) -> str:
    """Undo the small, systematic mistakes gpt-oss-20b makes with this schema.

    Observed in production: a stray quote after a bare number (`"confidence":0.95"}`) and a trailing comma
    before the closing brace. Anything else still fails validation and goes through the correction turn.
    """
    t = re.sub(r'(\d)"(\s*[,}\]])', r"\1\2", t)
    t = re.sub(r",(\s*[}\]])", r"\1", t)
    return t


def parse_enrichment(text: str) -> Enrichment:
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
    if m:
        t = m.group(1).strip()
    elif not t.startswith("{"):
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e > s:
            t = t[s : e + 1]
    try:
        data = json.loads(t)
    except ValueError:
        data = json.loads(repair_json(t))
    return Enrichment.model_validate(data)


def _call(client: Any, model_id: str, notice: dict[str, Any]) -> tuple[Enrichment, dict[str, int]]:
    messages = [{"role": "user", "content": [{"text": build_user_prompt(notice)}]}]
    usage = {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0}
    last_err: Exception | None = None
    max_tokens = 600
    for attempt in range(2):
        resp = client.converse(
            modelId=model_id,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            inferenceConfig={"maxTokens": max_tokens, "temperature": 0 if attempt == 0 else 0.3},
            # gpt-oss is a reasoning model; at default effort it can spend the whole budget thinking and never
            # emit the answer. Low effort is plenty for a fixed-schema classification task and is cheaper.
            additionalModelRequestFields={"reasoning_effort": "low"},
        )
        for k in usage:
            usage[k] += int(resp.get("usage", {}).get(k, 0))
        try:
            text = extract_text(resp)
        except (EnrichmentError, KeyError) as e:
            last_err, text = e, ""
            max_tokens = 2000  # reasoning model exhausted the 600-token budget before emitting text
        else:
            try:
                return parse_enrichment(text), usage
            except (ValueError, ValidationError) as e:  # JSONDecodeError is a ValueError
                last_err = e
        if attempt == 0:
            messages = messages + [
                {"role": "assistant", "content": [{"text": text or "(empty)"}]},
                {"role": "user", "content": [{"text": f"Your reply was invalid: {last_err}. Reply again with ONLY the corrected JSON object."}]},
            ]
    raise EnrichmentError(f"could not parse enrichment after retry: {last_err}")


def _langfuse_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


if _langfuse_enabled():
    from langfuse import get_client, observe, propagate_attributes

    @observe(name="enrich_notice")
    def enrich_notice(client: Any, model_id: str, notice: dict[str, Any]) -> tuple[Enrichment, dict[str, int]]:
        meta = {
            "request_id": str(notice["request_id"])[:200],
            "agency": str(notice.get("agency") or "")[:200],
            "prompt_version": PROMPT_VERSION,
        }
        with propagate_attributes(metadata=meta):
            result = _call(client, model_id, notice)
        get_client().update_current_span(output=result[0].model_dump(), metadata={"usage": result[1], "model": model_id})
        return result

    def flush() -> None:
        get_client().flush()
else:

    def enrich_notice(client: Any, model_id: str, notice: dict[str, Any]) -> tuple[Enrichment, dict[str, int]]:
        return _call(client, model_id, notice)

    def flush() -> None:
        pass
