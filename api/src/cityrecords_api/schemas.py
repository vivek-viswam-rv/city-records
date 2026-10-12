from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

SOURCE_URL = "https://a856-cityrecord.nyc.gov/RequestDetail/{}"


class VendorRef(BaseModel):
    id: int
    name: str | None = None


class Enrichment(BaseModel):
    what_is_bought: str | None = None
    product_category: str | None = None
    is_software: bool | None = None
    is_renewal: bool | None = None
    summary: str | None = None
    keywords: list[str] | None = None
    confidence: float | None = None
    model: str | None = None
    prompt_version: str | None = None
    enriched_at: datetime | None = None


class Notice(BaseModel):
    request_id: str
    published_on: date | None = None
    end_date: date | None = None
    section: str | None = None
    notice_type: str | None = None
    agency: str | None = None
    category: str | None = None
    title: str | None = None
    description: str | None = None
    selection_method: str | None = None
    pin: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contract_amount: float | None = None
    vendor_name_raw: str | None = None
    vendor: VendorRef | None = None
    event_date: datetime | None = None
    enrichment: Enrichment | None = None
    source_url: str = ""

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Notice":
        d = dict(row)
        d["source_url"] = SOURCE_URL.format(d["request_id"])
        return cls(**d)


class NoticeList(BaseModel):
    items: list[Notice]
    total: int
    has_more: bool


class VendorDetail(BaseModel):
    id: int
    name: str | None = None
    address: str | None = None
    first_seen: date | None = None
    notices: list[Notice]


class Filters(BaseModel):
    agencies: list[str]
    notice_types: list[str]
    categories: list[str]
    product_categories: list[str]


class WeekPoint(BaseModel):
    week: date
    notice_type: str | None = None
    usd: float
    count: int


class AgencyPoint(BaseModel):
    agency: str | None = None
    count: int
    usd: float


class ProductPoint(BaseModel):
    product_category: str | None = None
    count: int


class Stats(BaseModel):
    notices: int
    open_solicitations: int
    awarded_usd: float
    vendors: int
    by_week: list[WeekPoint]
    by_agency: list[AgencyPoint]
    by_product_category: list[ProductPoint]
