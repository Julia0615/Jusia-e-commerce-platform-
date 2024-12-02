#__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import redis
from flask import current_app

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Configure the app
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@cart-db:5432/carts',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'REDIS_URL': 'redis://cart-cache:6379/0',  # Ensure Redis URL is set correctly
        'JWT_SECRET_KEY': 'e1a00e39bd827b47334cff98872e82ac4568ea673115f88b04769f89714d6a1a'
    })
    
    # Initialize extensions with app
    db.init_app(app)

    # Initialize Redis client
    with app.app_context():
        redis_url = app.config['REDIS_URL']
        app.redis = redis.from_url(redis_url)  # Initialize Redis connection

        # Import models to ensure they are registered with SQLAlchemy
        from .models import CartItem
        
        # Create all database tables
        db.create_all()
        
        # Import and register blueprints
        from .routes import cart_bp
        app.register_blueprint(cart_bp)
        
        @app.route('/health')
        def health_check():
            return {"status": "healthy"}, 200
    
    return app
