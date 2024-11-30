# app/utils.py
from functools import wraps
from flask import request, jsonify
import jwt
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Decode token
            data = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY', 'your-secret-key'),
                algorithms=["HS256"]
            )
            current_user = {'id': data['user_id']}
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def create_response(data=None, message=None, status_code=200):
    """Utility function to create a standardized response"""
    response = {
        'success': 200 <= status_code < 300,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code