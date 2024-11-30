# app/__init__.py
from flask import Flask, jsonify
from .models import db
from .routes import orders_bp

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@order-service-postgres:5432/orders'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # Register blueprints
    app.register_blueprint(orders_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

