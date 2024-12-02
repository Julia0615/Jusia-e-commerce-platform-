
#routes.py
from flask import Blueprint, request, jsonify, current_app
from .services import CartService
from .models import db
from .utils import token_required

# Define the blueprint
cart_bp = Blueprint('cart', __name__)
cart_service = CartService()

@cart_bp.route('/api/cart/items', methods=['POST'])
@token_required
def add_item(current_user):
    """
    Add an item to the user's cart.
    """
    try:
        # Parse and validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['product_id', 'price']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validate input types
        try:
            product_id = int(data['product_id'])
            price = float(data['price'])
            quantity = int(data.get('quantity', 1))
        except ValueError:
            return jsonify({'error': 'Invalid data type for product_id, price, or quantity'}), 400

        # Ensure positive values for price and quantity
        if price <= 0 or quantity <= 0:
            return jsonify({'error': 'Price and quantity must be greater than 0'}), 400

        # Add the item to the cart
        item = cart_service.add_item(
            user_id=current_user['id'],
            product_id=product_id,
            price=price,
            quantity=quantity
        )
        
        return jsonify(item.to_dict()), 201

    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error in add_item route: {str(e)}")
        return jsonify({'error': 'An internal server error occurred'}), 500
