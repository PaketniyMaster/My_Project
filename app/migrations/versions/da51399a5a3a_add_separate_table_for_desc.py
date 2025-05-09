"""Add separate table for desc

Revision ID: da51399a5a3a
Revises: bfba1b46d497
Create Date: 2025-04-20 13:06:15.159512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'da51399a5a3a'
down_revision: Union[str, None] = 'bfba1b46d497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game_descriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_descriptions_id'), 'game_descriptions', ['id'], unique=False)
    op.drop_column('games', 'search_vector')
    op.drop_column('games', 'description_ru')
    op.drop_column('games', 'description_en')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('description_en', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('games', sa.Column('description_ru', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('games', sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_game_descriptions_id'), table_name='game_descriptions')
    op.drop_table('game_descriptions')
    # ### end Alembic commands ###
