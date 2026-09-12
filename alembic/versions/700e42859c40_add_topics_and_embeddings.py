"""add topics and embeddings

Revision ID: 700e42859c40
Revises: 699e42859c40
Create Date: 2026-09-12 19:10:24.528193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '700e42859c40'
down_revision: Union[str, Sequence[str], None] = '699e42859c40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # 2. Create topics table
    op.create_table('topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=False),
        sa.Column('is_outlier', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Add columns to social_events
    op.add_column('social_events', sa.Column('embedding', Vector(dim=384), nullable=True))
    op.add_column('social_events', sa.Column('topic_id', sa.Integer(), nullable=True))
    # We must provide an explicit name for the foreign key constraint
    op.create_foreign_key('fk_social_events_topic_id', 'social_events', 'topics', ['topic_id'], ['id'])
    op.create_index(op.f('ix_social_events_topic_id'), 'social_events', ['topic_id'], unique=False)

    # 4. Create HNSW index for the embedding column
    op.execute("CREATE INDEX ON social_events USING hnsw (embedding vector_cosine_ops);")


def downgrade() -> None:
    # 1. Drop HNSW index
    op.execute("DROP INDEX IF EXISTS social_events_embedding_idx;")

    # 2. Remove columns from social_events
    op.drop_constraint('fk_social_events_topic_id', 'social_events', type_='foreignkey')
    op.drop_index(op.f('ix_social_events_topic_id'), table_name='social_events')
    op.drop_column('social_events', 'topic_id')
    op.drop_column('social_events', 'embedding')

    # 3. Drop topics table
    op.drop_table('topics')

    # 4. Drop pgvector extension (optional, usually left alone as it might be used elsewhere)
    # op.execute('DROP EXTENSION IF EXISTS vector;')
