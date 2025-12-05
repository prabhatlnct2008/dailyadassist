"""Add workspace, product, workspace_page models and conversation updates

Revision ID: b1edf68c1ae4
Revises:
Create Date: 2025-12-05 06:50:42.333574

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'b1edf68c1ae4'
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Create workspaces table if not exists
    if not table_exists('workspaces'):
        op.create_table('workspaces',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('ad_account_id', sa.String(length=36), nullable=True),
            sa.Column('default_daily_budget', sa.Float(), nullable=True),
            sa.Column('default_currency', sa.String(length=10), nullable=True),
            sa.Column('default_objective', sa.String(length=50), nullable=True),
            sa.Column('timezone', sa.String(length=50), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('facebook_connected', sa.Boolean(), nullable=True),
            sa.Column('setup_completed', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['ad_account_id'], ['ad_accounts.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create workspace_pages table if not exists
    if not table_exists('workspace_pages'):
        op.create_table('workspace_pages',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('workspace_id', sa.String(length=36), nullable=False),
            sa.Column('facebook_page_id', sa.String(length=36), nullable=False),
            sa.Column('default_tone', sa.String(length=50), nullable=True),
            sa.Column('default_cta_style', sa.String(length=50), nullable=True),
            sa.Column('target_markets', sa.JSON(), nullable=True),
            sa.Column('is_included', sa.Boolean(), nullable=True),
            sa.Column('is_primary', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['facebook_page_id'], ['facebook_pages.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('workspace_id', 'facebook_page_id', name='uq_workspace_page')
        )

    # Create products table if not exists
    if not table_exists('products'):
        op.create_table('products',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('workspace_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('short_description', sa.Text(), nullable=True),
            sa.Column('long_description', sa.Text(), nullable=True),
            sa.Column('price', sa.Float(), nullable=True),
            sa.Column('price_range_min', sa.Float(), nullable=True),
            sa.Column('price_range_max', sa.Float(), nullable=True),
            sa.Column('currency', sa.String(length=10), nullable=True),
            sa.Column('usp', sa.Text(), nullable=True),
            sa.Column('target_audience', sa.Text(), nullable=True),
            sa.Column('seasonality', sa.String(length=100), nullable=True),
            sa.Column('primary_image_url', sa.String(length=500), nullable=True),
            sa.Column('image_url_2', sa.String(length=500), nullable=True),
            sa.Column('image_url_3', sa.String(length=500), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create page_products table if not exists
    if not table_exists('page_products'):
        op.create_table('page_products',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('workspace_page_id', sa.String(length=36), nullable=False),
            sa.Column('product_id', sa.String(length=36), nullable=False),
            sa.Column('is_default', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['workspace_page_id'], ['workspace_pages.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('workspace_page_id', 'product_id', name='uq_page_product')
        )

    # Add columns to conversations table if they don't exist
    conversations_columns = [
        ('workspace_id', sa.String(length=36)),
        ('workspace_page_id', sa.String(length=36)),
        ('chat_type', sa.String(length=20)),  # Using String instead of Enum for SQLite compatibility
        ('is_archived', sa.Boolean()),
        ('archived_at', sa.DateTime()),
        ('archive_summary', sa.Text()),
        ('is_pinned', sa.Boolean()),
        ('pinned_content', sa.Text()),
    ]

    for col_name, col_type in conversations_columns:
        if not column_exists('conversations', col_name):
            with op.batch_alter_table('conversations', schema=None) as batch_op:
                batch_op.add_column(sa.Column(col_name, col_type, nullable=True))

    # Add active_workspace_id to users if it doesn't exist
    if not column_exists('users', 'active_workspace_id'):
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('active_workspace_id', sa.String(length=36), nullable=True))


def downgrade():
    # Remove columns from users
    if column_exists('users', 'active_workspace_id'):
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.drop_column('active_workspace_id')

    # Remove columns from conversations
    conversations_columns = [
        'pinned_content', 'is_pinned', 'archive_summary', 'archived_at',
        'is_archived', 'chat_type', 'workspace_page_id', 'workspace_id'
    ]
    for col_name in conversations_columns:
        if column_exists('conversations', col_name):
            with op.batch_alter_table('conversations', schema=None) as batch_op:
                batch_op.drop_column(col_name)

    # Drop new tables if they exist
    for table_name in ['page_products', 'products', 'workspace_pages', 'workspaces']:
        if table_exists(table_name):
            op.drop_table(table_name)
