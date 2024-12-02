#services.py
# app/services.py
from flask import current_app
import redis
from typing import List, Optional
from .models import db, CartItem

class CartService:
    def __init__(self):
        redis_url = current_app.config['REDIS_URL']
        self.redis = redis.from_url(redis_url)

    def add_item(self, user_id: int, product_id: int, price: float, quantity: int = 1) -> Optional[CartItem]:
        try:
            cart_key = self._get_cart_key(user_id)
            
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                price=price,
                session_id=cart_key
            )
            
            db.session.add(cart_item)
            db.session.commit()
            
            # Cache in Redis
            item_data = {
                'id': cart_item.id,
                'product_id': product_id,
                'price': price,
                'quantity': quantity
            }
            self.redis.hset(cart_key, str(product_id), str(item_data))
            
            return cart_item
            
        except Exception as e:
            current_app.logger.error(f"Error adding item to cart: {str(e)}")
            db.session.rollback()
            raise

    def _get_cart_key(self, user_id: int) -> str:
        return f"cart:{user_id}"

    def get_cart_items(self, user_id: int) -> List[CartItem]:
        return CartItem.query.filter_by(user_id=user_id).all()

    def clear_cart(self, user_id: int) -> bool:
        try:
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            
            cart_key = self._get_cart_key(user_id)
            self.redis.delete(cart_key)
            return True
        except Exception as e:
            current_app.logger.error(f"Error clearing cart: {str(e)}")
            db.session.rollback()
            return False