#services.py
# app/services.py
from app import db
from .models import CartItem
from flask import current_app
import redis
import json

class CartService:
    def __init__(self):
        self.redis = None

    def _get_redis(self):
        if not self.redis:
            redis_url = current_app.config['REDIS_URL']
            self.redis = redis.from_url(redis_url, decode_responses=True)
        return self.redis

    def add_item(self, user_id: int, product_id: int, price: float, quantity: int = 1):
        try:
            cart_key = self._get_cart_key(user_id)

            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                price=price,
                session_id=cart_key
            )
            db.session.add(cart_item)
            db.session.commit()

            redis_client = self._get_redis()
            redis_client.hset(cart_key, str(product_id), json.dumps(cart_item.to_dict()))

            return cart_item
        except Exception as e:
            current_app.logger.error(f"Error adding item to cart: {e}")
            db.session.rollback()
            raise

    def _get_cart_key(self, user_id: int) -> str:
        return f"cart:{user_id}"


