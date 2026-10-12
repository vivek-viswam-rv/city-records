"""create cr schema, vendors, notices, enrichments

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create schema if not exists cr")
    op.execute("""
        create table cr.vendors (
            id serial primary key,
            name text,
            normalized_name text unique,
            address text,
            first_seen date
        )""")
    op.execute("""
        create table cr.notices (
            request_id text primary key,
            published_on date not null,
            end_date date,
            section text,
            notice_type text,
            agency text,
            category text,
            title text,
            description text,
            selection_method text,
            pin text,
            contact_name text,
            contact_email text,
            contract_amount numeric,
            vendor_name_raw text,
            vendor_id int null references cr.vendors(id),
            event_date timestamp,
            content_sha256 text not null,
            s3_key text,
            search tsvector generated always as (to_tsvector('english',
                coalesce(title,'') || ' ' || coalesce(description,'') || ' ' ||
                coalesce(agency,'') || ' ' || coalesce(vendor_name_raw,''))) stored
        )""")
    op.execute("create index ix_notices_published_on on cr.notices (published_on)")
    op.execute("create index ix_notices_agency on cr.notices (agency)")
    op.execute("create index ix_notices_notice_type on cr.notices (notice_type)")
    op.execute("create index ix_notices_vendor_id on cr.notices (vendor_id)")
    op.execute("create index ix_notices_search on cr.notices using gin (search)")
    op.execute("""
        create table cr.enrichments (
            request_id text primary key references cr.notices(request_id),
            what_is_bought text,
            product_category text,
            is_software boolean,
            is_renewal boolean,
            summary text,
            keywords text[],
            confidence real,
            model text,
            prompt_version text,
            content_sha256 text,
            enriched_at timestamptz default now()
        )""")
    op.execute("create index ix_enrichments_product_category on cr.enrichments (product_category)")
    op.execute("create index ix_enrichments_is_software on cr.enrichments (is_software)")


def downgrade() -> None:
    op.execute("drop table cr.enrichments")
    op.execute("drop table cr.notices")
    op.execute("drop table cr.vendors")
