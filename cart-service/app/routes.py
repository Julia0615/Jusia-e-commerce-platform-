
#routes.py
from flask import Blueprint, request, jsonify
from .services import CartService
from .utils import token_required

cart_bp = Blueprint('cart', __name__)
cart_service = CartService()

@cart_bp.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    items = cart_service.get_cart_items(user_id)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': cart_service.calculate_total(user_id)
    })

@cart_bp.route('/api/cart/<int:user_id>', methods=['DELETE'])
def clear_cart(user_id):
    if cart_service.clear_cart(user_id):
        return jsonify({'message': 'Cart cleared'}), 200
    return jsonify({'error': 'Failed to clear cart'}), 500