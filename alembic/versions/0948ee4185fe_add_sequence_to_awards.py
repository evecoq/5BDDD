"""add sequence to awards

Revision ID: 0948ee4185fe
Revises: adf2be6d233b
Create Date: 2024-10-13 13:15:55.758237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0948ee4185fe'
down_revision: Union[str, None] = 'adf2be6d233b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Créer une séquence pour la table 'awards'
    op.execute("""
        CREATE SEQUENCE awards_id_seq
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    """)

    # Associer la séquence à la colonne 'id' de la table 'awards'
    op.execute("""
        ALTER TABLE awards
        MODIFY id DEFAULT awards_id_seq.NEXTVAL
    """)

def downgrade():
    # Supprimer la séquence lors du downgrade
    op.execute("DROP SEQUENCE awards_id_seq")

