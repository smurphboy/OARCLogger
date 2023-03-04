"""empty message

Revision ID: 28a8f318e77d
Revises: 7e5522e73e7b
Create Date: 2023-03-04 22:16:50.628578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28a8f318e77d'
down_revision = '7e5522e73e7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('QSO', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prop_mode', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('ant_path', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('ms_shower', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('nr_pings', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nr_bursts', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('max_bursts', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('force_init', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('QSO', schema=None) as batch_op:
        batch_op.drop_column('force_init')
        batch_op.drop_column('max_bursts')
        batch_op.drop_column('nr_bursts')
        batch_op.drop_column('nr_pings')
        batch_op.drop_column('ms_shower')
        batch_op.drop_column('ant_path')
        batch_op.drop_column('prop_mode')

    # ### end Alembic commands ###
