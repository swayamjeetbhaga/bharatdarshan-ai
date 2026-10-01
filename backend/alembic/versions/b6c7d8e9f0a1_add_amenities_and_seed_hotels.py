"""add amenities field and seed chandrapur hotels

Adds `amenities` (a facility list — AC Rooms, Pool, Restaurant, ...), then
seeds 30 Chandrapur district hotels/resorts/Tadoba safari lodges from a
Google-Maps-sourced directory across three categories: city_hotel,
resort_farm_stay, and tadoba_safari_resort.

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-09-03 20:00:00.000000

"""
from datetime import date, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.data.chandrapur_hotels import CHANDRAPUR_HOTELS, DATASET_PREPARED_ON, EXTERNAL_RATING_SOURCE


revision: str = 'b6c7d8e9f0a1'
down_revision: Union[str, Sequence[str], None] = 'a5b6c7d8e9f0'
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
    sa.column('data_quality_note', sa.Text),
    sa.column('source_urls', postgresql.JSONB),
    sa.column('dataset_prepared_on', sa.Date),
    sa.column('phone', sa.String),
    sa.column('specialty', sa.String),
    sa.column('external_rating', sa.Float),
    sa.column('external_rating_count', sa.Integer),
    sa.column('external_rating_source', sa.String),
    sa.column('amenities', postgresql.JSONB),
    sa.column('photo_urls', postgresql.JSONB),
    sa.column('avg_rating', sa.Float),
    sa.column('review_count', sa.Integer),
    sa.column('created_at', sa.DateTime),
    sa.column('updated_at', sa.DateTime),
)


def _slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").replace(".", "").replace("'", "").replace("×", "x")


def upgrade() -> None:
    op.add_column('attractions', sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.execute("UPDATE attractions SET amenities = '[]'::jsonb WHERE amenities IS NULL")
    op.alter_column('attractions', 'amenities', nullable=False, server_default=sa.text("'[]'::jsonb"))

    prepared_on = date.fromisoformat(DATASET_PREPARED_ON)
    now = datetime.utcnow()

    rows = [
        {
            "external_id": f"curated:hotel:{_slugify(h['name'])}",
            "source": "curated",
            "name": h["name"],
            "district": "Chandrapur",
            "state": "Maharashtra",
            "category": h["category"],
            "area": h.get("area"),
            "lat": h["lat"],
            "lng": h["lng"],
            "coordinates_verified": False,
            "opening_access": h.get("opening_access"),
            "data_quality_note": h.get("data_quality_note"),
            "source_urls": [],
            "dataset_prepared_on": prepared_on,
            "phone": h.get("phone"),
            "specialty": h.get("specialty"),
            "external_rating": h.get("external_rating"),
            "external_rating_count": h.get("external_rating_count"),
            "external_rating_source": EXTERNAL_RATING_SOURCE,
            "amenities": h.get("amenities", []),
            "photo_urls": [],
            "avg_rating": None,
            "review_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        for h in CHANDRAPUR_HOTELS
    ]

    op.bulk_insert(attractions_table, rows)


def downgrade() -> None:
    conn = op.get_bind()
    names = [h["name"] for h in CHANDRAPUR_HOTELS]
    conn.execute(attractions_table.delete().where(attractions_table.c.name.in_(names)))
    op.drop_column('attractions', 'amenities')
