
#routes.py
from flask import Blueprint, request, jsonify, current_app
from .services import CartService
from .models import db
from .utils import token_required

cart_bp = Blueprint('cart', __name__)
cart_service = CartService()

@cart_bp.route('/api/cart/items', methods=['POST'])
@token_required
def add_item(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['product_id', 'price']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

        try:
            product_id = int(data['product_id'])
            price = float(data['price'])
            quantity = int(data.get('quantity', 1))
        except ValueError:
            return jsonify({'error': 'Invalid data type for product_id, price, or quantity'}), 400

        if price <= 0 or quantity <= 0:
            return jsonify({'error': 'Price and quantity must be greater than 0'}), 400

        item = cart_service.add_item(
            user_id=current_user['id'],
            product_id=product_id,
            price=price,
            quantity=quantity
        )
        
        return jsonify(item.to_dict()), 201

    except Exception as e:
        current_app.logger.error(f"Error in add_item route: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500

@cart_bp.route('/api/cart/<int:user_id>/items', methods=['GET'])
@token_required
def get_cart_items(current_user, user_id):
    if current_user['id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    items = cart_service.get_cart_items(user_id)
    return jsonify({'items': [item.to_dict() for item in items]})

@cart_bp.route('/api/cart/<int:item_id>/update_quantity', methods=['PUT'])
@token_required
def update_item_quantity(current_user, item_id):
    data = request.get_json()
    item = cart_service.update_quantity(current_user['id'], item_id, data['quantity'])
    return jsonify(item.to_dict())

@cart_bp.route('/api/cart/<int:user_id>/clear', methods=['DELETE'])
@token_required
def clear_user_cart(current_user, user_id):
    if current_user['id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    cart_service.clear_cart(user_id)
    return jsonify({'message': 'Cart cleared'})
