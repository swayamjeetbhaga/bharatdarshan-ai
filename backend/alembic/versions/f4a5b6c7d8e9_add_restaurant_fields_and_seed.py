"""add restaurant fields and seed chandrapur restaurants

Adds phone/price_tier/specialty plus an external_rating snapshot (kept
separate from avg_rating/review_count, which are always our own reviews
aggregate) so imported ratings never get silently overwritten by the first
in-app review. Seeds 29 Chandrapur city restaurants from a Google-Maps-
sourced directory.

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-09-03 15:00:00.000000

"""
from datetime import date, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.data.chandrapur_restaurants import CHANDRAPUR_RESTAURANTS, DATASET_PREPARED_ON, EXTERNAL_RATING_SOURCE


revision: str = 'f4a5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = 'e3f4a5b6c7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

attractions_table = sa.table(
    'attractions',
    sa.column('external_id', sa.String),
    sa.column('source', sa.String),
    sa.column('name', sa.String),
    sa.column('district', sa.String),
    sa.column('state', sa.String),
    sa.column('category', sa.String),
    sa.column('area', sa.String),
    sa.column('lat', sa.Float),
    sa.column('lng', sa.Float),
    sa.column('coordinates_verified', sa.Boolean),
    sa.column('opening_access', sa.String),
    sa.column('entry_fee_status', sa.String),
    sa.column('data_quality_note', sa.Text),
    sa.column('source_urls', postgresql.JSONB),
    sa.column('dataset_prepared_on', sa.Date),
    sa.column('phone', sa.String),
    sa.column('price_tier', sa.String),
    sa.column('specialty', sa.String),
    sa.column('external_rating', sa.Float),
    sa.column('external_rating_count', sa.Integer),
    sa.column('external_rating_source', sa.String),
    sa.column('photo_urls', postgresql.JSONB),
    sa.column('avg_rating', sa.Float),
    sa.column('review_count', sa.Integer),
    sa.column('created_at', sa.DateTime),
    sa.column('updated_at', sa.DateTime),
)


def _slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").replace(".", "").replace("'", "")


def upgrade() -> None:
    op.add_column('attractions', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('attractions', sa.Column('price_tier', sa.String(), nullable=True))
    op.add_column('attractions', sa.Column('specialty', sa.String(), nullable=True))
    op.add_column('attractions', sa.Column('external_rating', sa.Float(), nullable=True))
    op.add_column('attractions', sa.Column('external_rating_count', sa.Integer(), nullable=True))
    op.add_column('attractions', sa.Column('external_rating_source', sa.String(), nullable=True))

    prepared_on = date.fromisoformat(DATASET_PREPARED_ON)
    now = datetime.utcnow()

    rows = [
        {
            "external_id": f"curated:restaurant:{_slugify(r['name'])}",
            "source": "curated",
            "name": r["name"],
            "district": "Chandrapur",
            "state": "Maharashtra",
            "category": r["category"],
            "area": r.get("area"),
            "lat": r["lat"],
            "lng": r["lng"],
            "coordinates_verified": False,
            "opening_access": r.get("opening_access"),
            "entry_fee_status": r.get("entry_fee_status"),
            "data_quality_note": r.get("data_quality_note"),
            "source_urls": [],
            "dataset_prepared_on": prepared_on,
            "phone": r.get("phone"),
            "price_tier": r.get("price_tier"),
            "specialty": r.get("specialty"),
            "external_rating": r.get("external_rating"),
            "external_rating_count": r.get("external_rating_count"),
            "external_rating_source": EXTERNAL_RATING_SOURCE,
            "photo_urls": [],
            "avg_rating": None,
            "review_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        for r in CHANDRAPUR_RESTAURANTS
    ]

    op.bulk_insert(attractions_table, rows)


def downgrade() -> None:
    conn = op.get_bind()
    names = [r["name"] for r in CHANDRAPUR_RESTAURANTS]
    conn.execute(attractions_table.delete().where(attractions_table.c.name.in_(names)))

    op.drop_column('attractions', 'external_rating_source')
    op.drop_column('attractions', 'external_rating_count')
    op.drop_column('attractions', 'external_rating')
    op.drop_column('attractions', 'specialty')
    op.drop_column('attractions', 'price_tier')
    op.drop_column('attractions', 'phone')
