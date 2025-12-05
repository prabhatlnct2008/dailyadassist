"""Product and page-product association models."""
from datetime import datetime
from uuid import uuid4
from ..extensions import db


class Product(db.Model):
    """Product model for workspace products."""
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)

    # Core fields
    name = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    long_description = db.Column(db.Text, nullable=True)

    # Pricing
    price = db.Column(db.Float, nullable=True)
    price_range_min = db.Column(db.Float, nullable=True)
    price_range_max = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='INR')

    # Marketing
    usp = db.Column(db.Text, nullable=True)  # Unique Selling Proposition
    target_audience = db.Column(db.Text, nullable=True)
    seasonality = db.Column(db.String(100), nullable=True)

    # Media (1-3 images, all optional)
    primary_image_url = db.Column(db.String(500), nullable=True)
    image_url_2 = db.Column(db.String(500), nullable=True)
    image_url_3 = db.Column(db.String(500), nullable=True)

    # Tags for filtering
    tags = db.Column(db.JSON, default=list)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    page_products = db.relationship('PageProduct', backref='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'


class PageProduct(db.Model):
    """Associates products with specific pages."""
    __tablename__ = 'page_products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_page_id = db.Column(db.String(36), db.ForeignKey('workspace_pages.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: one product-page combination
    __table_args__ = (
        db.UniqueConstraint('workspace_page_id', 'product_id', name='uq_page_product'),
    )

    def __repr__(self):
        return f'<PageProduct page={self.workspace_page_id[:8]} product={self.product_id[:8]}>'
