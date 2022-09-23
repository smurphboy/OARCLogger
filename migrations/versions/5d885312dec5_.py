"""empty message

Revision ID: 5d885312dec5
Revises: 6ae1f21c96be
Create Date: 2022-09-23 13:26:38.831997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d885312dec5'
down_revision = '6ae1f21c96be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('configuration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('configuration', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###
