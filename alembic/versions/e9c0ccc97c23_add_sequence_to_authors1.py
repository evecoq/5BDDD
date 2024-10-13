"""add sequence to authors1

Revision ID: e9c0ccc97c23
Revises: 0ca7132de356
Create Date: 2024-10-13 13:14:07.778239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9c0ccc97c23'
down_revision: Union[str, None] = '0ca7132de356'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Créer une séquence pour la table 'author'
    op.execute("""
        CREATE SEQUENCE author_id_seq
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    """)

    # Associer la séquence à la colonne 'id' de la table 'author'
    op.execute("""
        ALTER TABLE author
        MODIFY id DEFAULT author_id_seq.NEXTVAL
    """)

def downgrade():
    # Supprimer la séquence lors du downgrade
    op.execute("DROP SEQUENCE author_id_seq")
