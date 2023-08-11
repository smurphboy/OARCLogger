"""clubcall added to event

Revision ID: 17f893357ecb
Revises: 8487586f6258
Create Date: 2023-08-11 15:27:43.915056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17f893357ecb'
down_revision = '8487586f6258'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('clubcall', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('clubcall')

    # ### end Alembic commands ###
