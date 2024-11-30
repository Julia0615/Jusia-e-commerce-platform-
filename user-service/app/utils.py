## user-service utils.py
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from app.models import User

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
            
        try:
            data = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated