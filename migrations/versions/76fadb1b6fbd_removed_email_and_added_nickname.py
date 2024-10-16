"""Removed email and added nickname

Revision ID: 76fadb1b6fbd
Revises: 79483074ce3a
Create Date: 2024-10-15 10:21:53.810584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76fadb1b6fbd'
down_revision = '79483074ce3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nickname', sa.String(length=64), nullable=False))
        batch_op.drop_index('ix_user_email')
        batch_op.create_index(batch_op.f('ix_user_nickname'), ['nickname'], unique=True)
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=120), nullable=False))
        batch_op.drop_index(batch_op.f('ix_user_nickname'))
        batch_op.create_index('ix_user_email', ['email'], unique=1)
        batch_op.drop_column('nickname')

    # ### end Alembic commands ###
