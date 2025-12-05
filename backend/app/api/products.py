"""Products API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from uuid import uuid4

from ..extensions import db
from ..models.product import Product, PageProduct
from ..models.workspace import Workspace, WorkspacePage
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, PageTagRequest

bp = Blueprint('products', __name__)


def validate_workspace_access(workspace_id, user_id):
    """Validate that the user owns the workspace."""
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return None, jsonify({'error': 'Workspace not found or access denied'}), 404
    return workspace, None, None


@bp.route('/workspaces/<workspace_id>/products', methods=['GET'])
@jwt_required()
def list_products(workspace_id):
    """List all products for a workspace."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Get products
    products = Product.query.filter_by(workspace_id=workspace_id).order_by(Product.created_at.desc()).all()

    return jsonify([
        ProductResponse.model_validate(product).model_dump()
        for product in products
    ])


@bp.route('/workspaces/<workspace_id>/products', methods=['POST'])
@jwt_required()
def create_product(workspace_id):
    """Create a new product for a workspace."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Parse and validate request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        product_data = ProductCreate(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400

    # Create product
    product = Product(
        id=str(uuid4()),
        workspace_id=workspace_id,
        **product_data.model_dump()
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(ProductResponse.model_validate(product).model_dump()), 201


@bp.route('/workspaces/<workspace_id>/products/<product_id>', methods=['GET'])
@jwt_required()
def get_product(workspace_id, product_id):
    """Get a specific product."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Get product
    product = Product.query.filter_by(id=product_id, workspace_id=workspace_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify(ProductResponse.model_validate(product).model_dump())


@bp.route('/workspaces/<workspace_id>/products/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(workspace_id, product_id):
    """Update a product."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Get product
    product = Product.query.filter_by(id=product_id, workspace_id=workspace_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Parse and validate request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        update_data = ProductUpdate(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400

    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    product.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(ProductResponse.model_validate(product).model_dump())


@bp.route('/workspaces/<workspace_id>/products/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(workspace_id, product_id):
    """Delete a product."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Get product
    product = Product.query.filter_by(id=product_id, workspace_id=workspace_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Delete product (cascade will handle PageProduct associations)
    db.session.delete(product)
    db.session.commit()

    return '', 204


@bp.route('/workspaces/<workspace_id>/products/<product_id>/tag-pages', methods=['POST'])
@jwt_required()
def tag_pages(workspace_id, product_id):
    """Tag a product to specific pages."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace, error_response, error_code = validate_workspace_access(workspace_id, user_id)
    if error_response:
        return error_response, error_code

    # Get product
    product = Product.query.filter_by(id=product_id, workspace_id=workspace_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Parse and validate request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        tag_request = PageTagRequest(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400

    # Validate all page_ids belong to the workspace
    workspace_pages = WorkspacePage.query.filter(
        WorkspacePage.workspace_id == workspace_id,
        WorkspacePage.id.in_(tag_request.page_ids)
    ).all()

    if len(workspace_pages) != len(tag_request.page_ids):
        return jsonify({'error': 'One or more page IDs are invalid for this workspace'}), 400

    # Clear existing page-product associations for this product
    PageProduct.query.filter_by(product_id=product_id).delete()

    # Create new associations
    for page_id in tag_request.page_ids:
        is_default = (page_id == tag_request.set_default_for)

        page_product = PageProduct(
            id=str(uuid4()),
            workspace_page_id=page_id,
            product_id=product_id,
            is_default=is_default
        )
        db.session.add(page_product)

    # If set_default_for is provided, ensure only one default per page
    if tag_request.set_default_for:
        # Clear other defaults for this page
        PageProduct.query.filter(
            PageProduct.workspace_page_id == tag_request.set_default_for,
            PageProduct.product_id != product_id,
            PageProduct.is_default == True
        ).update({'is_default': False})

    db.session.commit()

    # Return updated product
    return jsonify(ProductResponse.model_validate(product).model_dump())
