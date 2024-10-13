"""drop tables

Revision ID: 5be46905780b
Revises: e0eead039ddc
Create Date: 2024-10-13 12:04:55.564240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5be46905780b'
down_revision: Union[str, None] = 'e0eead039ddc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Drop the author, awards, rating, and books tables
    op.drop_table('author')
    op.drop_table('awards')
    op.drop_table('rating')
    op.drop_table('books')



def downgrade() -> None:
    # Recreate the dropped tables
    op.create_table('books',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('book_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_id')
    )
    
    op.create_table('awards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('award', sa.String(length=500), nullable=True),
        sa.Column('book_id', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.book_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('author',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=500), nullable=True),
        sa.Column('book_id', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.book_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('rating',
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('num_ratings', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('book_id')
    )

