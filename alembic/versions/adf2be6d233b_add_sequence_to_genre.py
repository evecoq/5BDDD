"""add sequence to genre

Revision ID: adf2be6d233b
Revises: e9c0ccc97c23
Create Date: 2024-10-13 13:15:18.331313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adf2be6d233b'
down_revision: Union[str, None] = 'e9c0ccc97c23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Créer une séquence pour la table 'genre'
    op.execute("""
        CREATE SEQUENCE genre_id_seq
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    """)

    # Associer la séquence à la colonne 'id' de la table 'genre'
    op.execute("""
        ALTER TABLE genre
        MODIFY id DEFAULT genre_id_seq.NEXTVAL
    """)

def downgrade():
    # Supprimer la séquence lors du downgrade
    op.execute("DROP SEQUENCE genre_id_seq")