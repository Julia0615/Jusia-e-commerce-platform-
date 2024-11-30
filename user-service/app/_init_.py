#user-service _init_py
from flask import Flask
from app.models import db
from app.routes import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    
    app.register_blueprint(users_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
    
    return app