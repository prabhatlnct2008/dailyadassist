"""Add active_product_id to conversations

Revision ID: c2fda79d2be5
Revises: b1edf68c1ae4
Create Date: 2025-12-05 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'c2fda79d2be5'
down_revision = 'b1edf68c1ae4'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add active_product_id to conversations if it doesn't exist
    if not column_exists('conversations', 'active_product_id'):
        with op.batch_alter_table('conversations', schema=None) as batch_op:
            batch_op.add_column(sa.Column('active_product_id', sa.String(length=36), nullable=True))


def downgrade():
    # Remove active_product_id from conversations if it exists
    if column_exists('conversations', 'active_product_id'):
        with op.batch_alter_table('conversations', schema=None) as batch_op:
            batch_op.drop_column('active_product_id')
