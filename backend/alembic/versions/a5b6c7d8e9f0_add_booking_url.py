"""add booking_url for places with an official booking portal

Revision ID: a5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-09-03 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.data.chandrapur_places import CHANDRAPUR_ATTRACTIONS


revision: str = 'a5b6c7d8e9f0'
down_revision: Union[str, Sequence[str], None] = 'f4a5b6c7d8e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

attractions = sa.table(
    'attractions',
    sa.column('name', sa.String),
    sa.column('booking_url', sa.String),
)


def upgrade() -> None:
    op.add_column('attractions', sa.Column('booking_url', sa.String(), nullable=True))

    # Backfill from the seed dataset for any curated place that carries one
    # (Tadoba's safari permit portal today).
    conn = op.get_bind()
    for place in CHANDRAPUR_ATTRACTIONS:
        url = place.get("booking_url")
        if url:
            conn.execute(
                attractions.update()
                .where(attractions.c.name == place["name"])
                .values(booking_url=url)
            )


def downgrade() -> None:
    op.drop_column('attractions', 'booking_url')
