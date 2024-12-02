## user-service utils.py
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from .services import UserService

def generate_token(user_id: int, secret_key: str) -> str:
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        },
        secret_key,
        algorithm='HS256'
    )

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        user_service = UserService()
        user_id = user_service.validate_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
            
        current_user = user_service.get_user_by_id(user_id)
        return f(current_user, *args, **kwargs)
    
    return decorated