"""seed chandrapur attractions

Revision ID: d2e3f4a5b6c7
Revises: c1a2b3d4e5f6
Create Date: 2026-09-03 00:05:00.000000

"""
from datetime import date, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.data.chandrapur_places import CHANDRAPUR_ATTRACTIONS, DATASET_PREPARED_ON


# revision identifiers, used by Alembic.
revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

attractions_table = sa.table(
    'attractions',
    sa.column('name', sa.String),
    sa.column('district', sa.String),
    sa.column('state', sa.String),
    sa.column('category', sa.String),
    sa.column('area', sa.String),
    sa.column('lat', sa.Float),
    sa.column('lng', sa.Float),
    sa.column('coordinates_verified', sa.Boolean),
    sa.column('distance_from_chandrapur_km', sa.Float),
    sa.column('distance_from_nagpur_km', sa.Float),
    sa.column('opening_access', sa.String),
    sa.column('entry_fee_status', sa.String),
    sa.column('transportation', sa.String),
    sa.column('data_quality_note', sa.Text),
    sa.column('source_urls', postgresql.JSONB),
    sa.column('dataset_prepared_on', sa.Date),
    sa.column('photo_urls', postgresql.JSONB),
    sa.column('avg_rating', sa.Float),
    sa.column('review_count', sa.Integer),
    sa.column('created_at', sa.DateTime),
    sa.column('updated_at', sa.DateTime),
)


def upgrade() -> None:
    """Seed the pilot Chandrapur district attraction records."""
    prepared_on = date.fromisoformat(DATASET_PREPARED_ON)
    now = datetime.utcnow()

    rows = [
        {
            "name": place["name"],
            "district": "Chandrapur",
            "state": "Maharashtra",
            "category": place["category"],
            "area": place.get("area"),
            "lat": place["lat"],
            "lng": place["lng"],
            "coordinates_verified": False,
            "distance_from_chandrapur_km": place.get("distance_from_chandrapur_km"),
            "distance_from_nagpur_km": place.get("distance_from_nagpur_km"),
            "opening_access": place.get("opening_access"),
            "entry_fee_status": place.get("entry_fee_status"),
            "transportation": place.get("transportation"),
            "data_quality_note": place.get("data_quality_note"),
            "source_urls": place.get("source_urls", []),
            "dataset_prepared_on": prepared_on,
            "photo_urls": [],
            "avg_rating": None,
            "review_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        for place in CHANDRAPUR_ATTRACTIONS
    ]

    op.bulk_insert(attractions_table, rows)


def downgrade() -> None:
    """Remove the seeded pilot Chandrapur district records."""
    conn = op.get_bind()
    names = [place["name"] for place in CHANDRAPUR_ATTRACTIONS]
    conn.execute(
        attractions_table.delete().where(attractions_table.c.name.in_(names))
    )
