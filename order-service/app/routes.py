# app/routes.py

from flask import Blueprint, request, jsonify, abort
from .services import OrderService
from .models import db

orders_bp = Blueprint('orders', __name__)
order_service = OrderService()

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order for the user.
    """
    try:
        user_id = request.json.get('user_id')
        token = request.headers.get('Authorization')
        
        if not user_id or not token:
            return jsonify({'status': 'error', 'message': 'Missing user_id or authorization token'}), 400
        
        order = order_service.create_order(user_id, token)
        return jsonify({'status': 'success', 'data': order.to_dict()}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Retrieve a specific order by order_id for a user.
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Missing user_id parameter'}), 400
        
        # Fetch the order
        order = order_service.get_order(order_id, int(user_id))
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        
        return jsonify({'status': 'success', 'data': order.to_dict()}), 200
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@orders_bp.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """
    Retrieve all orders for a specific user.
    """
    try:
        orders = order_service.get_user_orders(user_id)
        return jsonify({'status': 'success', 'data': [order.to_dict() for order in orders]}), 200
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
