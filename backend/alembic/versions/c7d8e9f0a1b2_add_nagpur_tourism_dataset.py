"""add Nagpur tourism dataset

Revision ID: c7d8e9f0a1b2
Revises: b6c7d8e9f0a1
Create Date: 2026-09-10 23:00:00.000000
"""

from collections.abc import Sequence
from datetime import UTC, date, datetime

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.data.nagpur_places import DATASET_PREPARED_ON, NAGPUR_ATTRACTIONS

revision: str = "c7d8e9f0a1b2"
down_revision: str | Sequence[str] | None = "b6c7d8e9f0a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

attractions = sa.table(
    "attractions",
    sa.column("external_id", sa.String),
    sa.column("source", sa.String),
    sa.column("name", sa.String),
    sa.column("district", sa.String),
    sa.column("state", sa.String),
    sa.column("category", sa.String),
    sa.column("area", sa.String),
    sa.column("lat", sa.Float),
    sa.column("lng", sa.Float),
    sa.column("coordinates_verified", sa.Boolean),
    sa.column("distance_from_nagpur_km", sa.Float),
    sa.column("distance_from_nagpur_airport_km", sa.Float),
    sa.column("opening_access", sa.String),
    sa.column("entry_fee_status", sa.String),
    sa.column("transportation", sa.String),
    sa.column("data_quality_note", sa.Text),
    sa.column("source_urls", postgresql.JSONB),
    sa.column("dataset_prepared_on", sa.Date),
    sa.column("amenities", postgresql.JSONB),
    sa.column("photo_urls", postgresql.JSONB),
    sa.column("review_count", sa.Integer),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)


def _slugify(name: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in name.lower()).split())


def upgrade() -> None:
    op.add_column(
        "attractions",
        sa.Column("distance_from_nagpur_airport_km", sa.Float(), nullable=True),
    )
    prepared_on = date.fromisoformat(DATASET_PREPARED_ON)
    now = datetime.now(UTC).replace(tzinfo=None)
    op.bulk_insert(
        attractions,
        [
            {
                "external_id": f"curated:nagpur:{_slugify(place['name'])}",
                "source": "curated",
                "name": place["name"],
                "district": "Nagpur",
                "state": "Maharashtra",
                "category": place["category"],
                "area": place["area"],
                "lat": place["lat"],
                "lng": place["lng"],
                "coordinates_verified": False,
                "distance_from_nagpur_km": place["distance_from_nagpur_km"],
                "distance_from_nagpur_airport_km": place[
                    "distance_from_nagpur_airport_km"
                ],
                "opening_access": place["opening_access"],
                "entry_fee_status": place["entry_fee_status"],
                "transportation": place["transportation"],
                "data_quality_note": place["data_quality_note"],
                "source_urls": place["source_urls"],
                "dataset_prepared_on": prepared_on,
                "amenities": [],
                "photo_urls": [],
                "review_count": 0,
                "created_at": now,
                "updated_at": now,
            }
            for place in NAGPUR_ATTRACTIONS
        ],
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        attractions.delete().where(attractions.c.external_id.like("curated:nagpur:%"))
    )
    op.drop_column("attractions", "distance_from_nagpur_airport_km")
