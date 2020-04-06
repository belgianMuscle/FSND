"""empty message

Revision ID: a8291be5873b
Revises: 2f0b019042ff
Create Date: 2020-03-29 16:38:29.610170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8291be5873b'
down_revision = '2f0b019042ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('available_from', sa.DateTime(), nullable=True))
    op.add_column('Artist', sa.Column('available_to', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'available_to')
    op.drop_column('Artist', 'available_from')
    # ### end Alembic commands ###