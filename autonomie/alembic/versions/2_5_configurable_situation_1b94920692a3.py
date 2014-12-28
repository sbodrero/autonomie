"""2.5 : configurable_situation

Revision ID: 1b94920692a3
Revises: 46beb4c6f140
Create Date: 2014-12-28 14:56:11.070890

"""

# revision identifiers, used by Alembic.
revision = '1b94920692a3'
down_revision = '46beb4c6f140'

from alembic import op
import sqlalchemy as sa


def upgrade():
    from alembic.context import get_bind
    op.add_column(
        "user_datas",
        sa.Column(
            "situation_situation_id",
            sa.Integer,
            sa.ForeignKey("cae_situation_option.id"),
        )
    )
    from autonomie.models.user import (
        CaeSituationOption,
        SITUATION_OPTIONS,
    )
    from autonomie.models.base import DBSESSION
    temp_dict = {}
    for key, value in SITUATION_OPTIONS:
        option = CaeSituationOption(label=value)
        DBSESSION().add(option)
        DBSESSION().flush()
        temp_dict[key] = option.id

    conn = get_bind()
    query = "select id, situation_situation from user_datas"
    result = conn.execute(query)

    for id, situation in result:
        option_id = temp_dict.get(situation)
        if option_id is None:
            import warnings
            warnings.warn("We don't know about this situation : %s \
id: %s" % (situation, id))
            continue
        query = "update user_datas set situation_situation_id='{0}' \
where id='{1}'".format(option_id, id)
        op.execute(query)


def downgrade():
    op.drop_column("user_datas", "situation_situation_id")
    op.execute("delete from cae_situation_option")
