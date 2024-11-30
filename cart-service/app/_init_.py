#_init_.py
from flask import Flask
from flask_session import Session
from redis import Redis
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    # Initialize Redis for session
    redis = Redis.from_url(app.config['REDIS_URL'])
    Session(app)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Register blueprints
    from app.routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
    
    return app