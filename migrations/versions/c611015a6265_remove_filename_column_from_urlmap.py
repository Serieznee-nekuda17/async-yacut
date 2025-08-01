"""Remove filename column from URLMap

Revision ID: c611015a6265
Revises: 340fbd70d9d0
Create Date: 2025-07-24 21:14:41.385317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c611015a6265'
down_revision = '340fbd70d9d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('url_map', schema=None) as batch_op:
        batch_op.drop_column('filename')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('url_map', schema=None) as batch_op:
        batch_op.add_column(sa.Column('filename', sa.VARCHAR(length=256), nullable=True))

    # ### end Alembic commands ###
