"""empty message

Revision ID: 136cffc6bfb6
Revises: a8291be5873b
Create Date: 2020-03-29 17:26:13.004434

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '136cffc6bfb6'
down_revision = 'a8291be5873b'
branch_labels = None
depends_on = None


def upgrade():

    op.execute("UPDATE \"Artist\" SET available_from = TIMESTAMP '2020-01-01 00:00:00' WHERE available_from IS NULL;")
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'available_from',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.execute("UPDATE \"Artist\" SET available_to = TIMESTAMP '2020-01-01 00:00:00' WHERE available_to IS NULL;")
    op.alter_column('Artist', 'available_to',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'available_to',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('Artist', 'available_from',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###