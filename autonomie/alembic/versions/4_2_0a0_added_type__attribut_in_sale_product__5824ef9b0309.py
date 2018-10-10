"""Added type_ attribut in Sale_product_group

Revision ID: 5824ef9b0309
Revises: 182bf34f7989
Create Date: 2018-10-10 17:01:09.168288

"""

# revision identifiers, used by Alembic.
revision = '5824ef9b0309'
down_revision = '182bf34f7989'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def update_database_structure():
    op.add_column('sale_product_group', sa.Column(
        'type_',
        sa.String(length=30),
        nullable=False),
        server_default='base',
    )

def migrate_datas():
    from autonomie_base.models.base import DBSESSION
    session = DBSESSION()
    from alembic.context import get_bind
    conn = get_bind()

def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sale_product_group', 'type_')
