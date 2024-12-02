
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
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        item = cart_service.add_item(
            user_id=current_user['id'],
            product_id=data['product_id'],
            price=float(data['price']),
            quantity=data.get('quantity', 1)
        )
        
        return jsonify(item.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error in add_item route: {str(e)}")
        return jsonify({'error': str(e)}), 500