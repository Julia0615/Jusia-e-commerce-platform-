#conftest.py
import pytest
from app import create_app
from app.models import db
import os
import jwt

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'REDIS_URL': 'redis://localhost:6379/1',
        'JWT_SECRET_KEY': 'test-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    # Create a test JWT token
    token = jwt.encode(
        {'user_id': 1},
        'test-key',
        algorithm='HS256'
    )
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }