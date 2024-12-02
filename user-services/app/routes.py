## user-service routes.py
from flask import Blueprint, request, jsonify
from .models import User
from .services import UserService
from .utils import token_required

users_bp = Blueprint('users', __name__)
user_service = UserService()

@users_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    user = user_service.register_user(data['username'], data['email'], data['password'])
    return jsonify(user.to_dict()), 201

@users_bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    token = user_service.login(data['email'], data['password'])
    if token:
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@users_bp.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = user_service.get_all_users()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    data = request.json
    user = user_service.update_user(user_id, data)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if user_service.delete_user(user_id):
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404