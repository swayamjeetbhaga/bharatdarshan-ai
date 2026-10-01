"""create attractions and reviews tables

Revision ID: c1a2b3d4e5f6
Revises: 8a9054d8f0dd
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8a9054d8f0dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('attractions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('district', sa.String(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('area', sa.String(), nullable=True),
    sa.Column('lat', sa.Float(), nullable=False),
    sa.Column('lng', sa.Float(), nullable=False),
    sa.Column('coordinates_verified', sa.Boolean(), nullable=False),
    sa.Column('distance_from_chandrapur_km', sa.Float(), nullable=True),
    sa.Column('distance_from_nagpur_km', sa.Float(), nullable=True),
    sa.Column('opening_access', sa.String(), nullable=True),
    sa.Column('entry_fee_status', sa.String(), nullable=True),
    sa.Column('transportation', sa.String(), nullable=True),
    sa.Column('data_quality_note', sa.Text(), nullable=True),
    sa.Column('source_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('dataset_prepared_on', sa.Date(), nullable=True),
    sa.Column('photo_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('avg_rating', sa.Float(), nullable=True),
    sa.Column('review_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint(
        "category IN ('wildlife', 'lake_nature', 'religious_heritage', 'historical_fort', 'social_educational')",
        name='ck_attraction_category',
    ),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attractions_id'), 'attractions', ['id'], unique=False)
    op.create_index(op.f('ix_attractions_name'), 'attractions', ['name'], unique=False)
    op.create_index(op.f('ix_attractions_category'), 'attractions', ['category'], unique=False)

    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('attraction_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_review_rating_range'),
    sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attraction_id', 'user_id', name='uq_review_attraction_user'),
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_attraction_id'), 'reviews', ['attraction_id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_reviews_user_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_attraction_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_table('reviews')

    op.drop_index(op.f('ix_attractions_category'), table_name='attractions')
    op.drop_index(op.f('ix_attractions_name'), table_name='attractions')
    op.drop_index(op.f('ix_attractions_id'), table_name='attractions')
    op.drop_table('attractions')
