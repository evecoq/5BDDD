"""add sequence to book

Revision ID: acef0251556e
Revises: ada9f7bc3781
Create Date: 2024-10-13 13:03:55.231243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acef0251556e'
down_revision: Union[str, None] = 'ada9f7bc3781'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Utiliser une instruction SQL brute pour créer la séquence
    op.execute("""
        CREATE SEQUENCE book_id_seq
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    """)

    # Associer la séquence à la colonne id de la table books
    op.execute("""
        ALTER TABLE books
        MODIFY id DEFAULT book_id_seq.NEXTVAL
    """)

def downgrade():
    # Supprimer la séquence lors du downgrade
    op.execute("DROP SEQUENCE book_id_seq")
