"""initial commit

Revision ID: 9364209de6b7
Revises: 
Create Date: 2024-06-08 00:59:34.668689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9364209de6b7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_lines',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sku', sa.String(length=255), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.Column('orderid', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product',
    sa.Column('sku', sa.String(length=255), autoincrement=False, nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('sku')
    )
    op.create_table('batch',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reference', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('_purchased_quantity', sa.Integer(), nullable=True),
    sa.Column('eta', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['reference'], ['product.sku'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('allocations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('orderline_id', sa.Integer(), nullable=True),
    sa.Column('batch_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['batch_id'], ['batch.id'], ),
    sa.ForeignKeyConstraint(['orderline_id'], ['order_lines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('allocations')
    op.drop_table('batch')
    op.drop_table('product')
    op.drop_table('order_lines')
    # ### end Alembic commands ###
