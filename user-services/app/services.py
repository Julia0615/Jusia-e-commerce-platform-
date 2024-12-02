#user-service services.py
from typing import Optional, List
from .models import db, User
from .utils import generate_token
from flask import current_app

class UserService:
    def register_user(self, username: str, email: str, password: str) -> User:
        if self.get_user_by_email(email):
            raise ValueError("Email already registered")
        return self.create_user(username, email, password)
    
    def create_user(self, username: str, email: str, password: str) -> User:
        try:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User.query.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()
        
    def get_all_users(self) -> List[User]:
        return User.query.all()
        
    def update_user(self, user_id: int, data: dict) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        try:
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'password' in data:
                user.set_password(data['password'])
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def login(self, email: str, password: str) -> Optional[str]:
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return generate_token(user.id, current_app.config['SECRET_KEY']) 
        return None

    def validate_token(self, token: str) -> Optional[int]:
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return data['user_id']
        except:
            return None