"""generalize attractions for india-wide places

Adds `source` (curated vs. community) and a stable `external_id` dedupe key
so any place found through live map search — not just the curated
Chandrapur pilot set — can be resolved to a reviewable/photographable row.
district/state become optional since not every geocoded place resolves one.

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4a5b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('ck_attraction_category', 'attractions', type_='check')

    op.add_column('attractions', sa.Column('source', sa.String(), nullable=True))
    op.add_column('attractions', sa.Column('external_id', sa.String(), nullable=True))

    attractions = sa.table(
        'attractions',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('source', sa.String),
        sa.column('external_id', sa.String),
    )
    conn = op.get_bind()
    for row in conn.execute(sa.select(attractions.c.id, attractions.c.name)):
        slug = row.name.strip().lower().replace(" ", "-").replace("/", "-")
        conn.execute(
            attractions.update()
            .where(attractions.c.id == row.id)
            .values(source="curated", external_id=f"curated:{slug}")
        )

    op.alter_column('attractions', 'source', nullable=False)
    op.alter_column('attractions', 'external_id', nullable=False)
    op.alter_column('attractions', 'district', nullable=True)
    op.alter_column('attractions', 'state', nullable=True)

    op.create_unique_constraint('uq_attraction_external_id', 'attractions', ['external_id'])
    op.create_index(op.f('ix_attractions_external_id'), 'attractions', ['external_id'], unique=False)
    op.create_index(op.f('ix_attractions_district'), 'attractions', ['district'], unique=False)
    op.create_check_constraint(
        'ck_attraction_source', 'attractions', "source IN ('curated', 'community')"
    )


def downgrade() -> None:
    op.drop_constraint('ck_attraction_source', 'attractions', type_='check')
    op.drop_index(op.f('ix_attractions_district'), table_name='attractions')
    op.drop_index(op.f('ix_attractions_external_id'), table_name='attractions')
    op.drop_constraint('uq_attraction_external_id', 'attractions', type_='unique')

    op.alter_column('attractions', 'state', nullable=False)
    op.alter_column('attractions', 'district', nullable=False)
    op.drop_column('attractions', 'external_id')
    op.drop_column('attractions', 'source')

    op.create_check_constraint(
        'ck_attraction_category',
        'attractions',
        "category IN ('wildlife', 'lake_nature', 'religious_heritage', 'historical_fort', 'social_educational')",
    )
