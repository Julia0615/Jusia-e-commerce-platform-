#user-service services.py
from typing import Optional, List
from .models import db, User
import jwt
from datetime import datetime, timedelta
from flask import current_app

class UserService:
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
        return db.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    def get_all_users(self) -> List[User]:
        return User.query.filter_by(is_active=True).all()

    def update_user(self, user_id: int, data: dict) -> Optional[User]:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None

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
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            user.is_active = False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def authenticate(self, email: str, password: str) -> Optional[str]:
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(days=1)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
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