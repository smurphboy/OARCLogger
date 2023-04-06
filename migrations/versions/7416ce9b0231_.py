"""empty message

Revision ID: 7416ce9b0231
Revises: f8eaf753a881
Create Date: 2023-04-06 20:28:00.437713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7416ce9b0231'
down_revision = 'f8eaf753a881'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('selected',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event'], ['event.id'], name=op.f('fk_selected_event_event')),
    sa.ForeignKeyConstraint(['user'], ['user.id'], name=op.f('fk_selected_user_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_selected'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('selected')
    # ### end Alembic commands ###
