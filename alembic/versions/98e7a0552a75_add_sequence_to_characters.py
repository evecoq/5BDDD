"""add sequence to characters

Revision ID: 98e7a0552a75
Revises: 0948ee4185fe
Create Date: 2024-10-13 13:17:34.375596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98e7a0552a75'
down_revision: Union[str, None] = '0948ee4185fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Créer une séquence pour la table 'characters'
    op.execute("""
        CREATE SEQUENCE characters_id_seq
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    """)

    # Associer la séquence à la colonne 'id' de la table 'characters'
    op.execute("""
        ALTER TABLE characters
        MODIFY id DEFAULT characters_id_seq.NEXTVAL
    """)

def downgrade():
    # Supprimer la séquence lors du downgrade
    op.execute("DROP SEQUENCE characters_id_seq")
