#services.py
# app/services.py
from flask import current_app
import redis
import json
from typing import List, Optional
from .models import CartItem, db
import jwt

class CartService:
    def __init__(self):
        # Initialize Redis connection from Flask's current_app context
        self.redis = self._init_redis()

    def _init_redis(self):
        redis_url = current_app.config.get('REDIS_URL')
        if redis_url:
            return redis.from_url(redis_url)
        return None

    def add_item(self, user_id: int, product_id: int, price: float, quantity: int = 1) -> Optional[CartItem]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        try:
            cart_key = self._get_cart_key(user_id)
            existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
            
            if existing_item:
                existing_item.quantity += quantity
                db.session.commit()
                return existing_item

            cart_item = CartItem(
                session_id=cart_key,
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            
            db.session.add(cart_item)
            db.session.commit()
            return cart_item
        except Exception as e:
            db.session.rollback()
            raise

    def get_cart_items(self, user_id: int) -> List[CartItem]:
        return CartItem.query.filter_by(user_id=user_id).all()

    def update_quantity(self, user_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if item:
            item.quantity = quantity
            db.session.commit()
        return item

    def clear_cart(self, user_id: int) -> bool:
        try:
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def _get_cart_key(self, user_id: int) -> str:
        return f"cart:{user_id}"
