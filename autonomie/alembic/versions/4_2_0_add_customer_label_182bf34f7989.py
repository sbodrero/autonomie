"""4.2.0 Add customer label column

Revision ID: 182bf34f7989
Revises: 2793f8d2e33e
Create Date: 2018-09-04 15:56:12.174179

"""

# revision identifiers, used by Alembic.
revision = '182bf34f7989'
down_revision = '2793f8d2e33e'

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customer', sa.Column('label', sa.String(length=255), nullable=True))


def migrate_datas():
    from autonomie_base.models.base import DBSESSION
    session = DBSESSION()
    from autonomie.models.customer import Customer
    for customer in Customer.query().options(
        sa.orm.load_only(
            "id", "name", "lastname", "firstname", "civilite", "type_"
        )
    ):
        customer.label = customer._get_label()
        session.merge(customer)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customer', 'label')