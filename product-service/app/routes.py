#product-service routes.py
from flask import Blueprint, request, jsonify
from .services import ProductService
from .utils import token_required

products_bp = Blueprint('products', __name__)
product_service = ProductService()

@products_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@products_bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    try:
        data = request.form.to_dict()
        image_file = request.files.get('image')
        
        product = product_service.create_product(data, image_file)
        return jsonify(product.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products')
def get_all_products():
    try:
        category = request.args.get('category')
        products = product_service.get_all_products(category)
        return jsonify([p.to_dict() for p in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>')
def get_product(product_id):
    try:
        product = product_service.get_product(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    try:
        data = request.form.to_dict()
        image_file = request.files.get('image')
        
        product = product_service.update_product(product_id, data, image_file)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify(product.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>/stock', methods=['POST'])
@token_required
def check_stock(current_user, product_id):
    try:
        quantity = int(request.json.get('quantity', 1))
        available = product_service.check_stock(product_id, quantity)
        return jsonify({'available': available})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>/stock', methods=['PUT'])
@token_required
def update_stock(current_user, product_id):
    try:
        quantity = request.json.get('quantity')
        if quantity is None:
            return jsonify({'error': 'Quantity is required'}), 400
            
        product = product_service.update_stock(product_id, quantity)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify(product.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    try:
        if product_service.delete_product(product_id):
            return jsonify({'message': 'Product deleted'})
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500