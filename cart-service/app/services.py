#services.py
import redis
import json
from typing import List, Optional
from decimal import Decimal
from .models import CartItem

class CartService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
    def _get_cart_key(self, user_id: int) -> str:
        return f"cart:{user_id}"
        
    def add_item(self, user_id: int, product_id: int, price: float, quantity: int = 1) -> CartItem:
        cart_key = self._get_cart_key(user_id)
        item_key = f"{product_id}"
        
        # Check if item exists
        existing_item = self.redis.hget(cart_key, item_key)
        if existing_item:
            item_data = json.loads(existing_item)
            item_data['quantity'] += quantity
        else:
            item_data = {
                'product_id': product_id,
                'price': price,
                'quantity': quantity
            }
        
        self.redis.hset(cart_key, item_key, json.dumps(item_data))
        return CartItem(**item_data)

    def get_cart_items(self, user_id: int) -> List[CartItem]:
        cart_key = self._get_cart_key(user_id)
        items = []
        
        for item_data in self.redis.hgetall(cart_key).values():
            item_dict = json.loads(item_data)
            items.append(CartItem(**item_dict))
            
        return items

    def update_quantity(self, user_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
        if quantity <= 0:
            return None
            
        cart_key = self._get_cart_key(user_id)
        item_key = f"{product_id}"
        
        existing_item = self.redis.hget(cart_key, item_key)
        if not existing_item:
            return None
            
        item_data = json.loads(existing_item)
        item_data['quantity'] = quantity
        
        self.redis.hset(cart_key, item_key, json.dumps(item_data))
        return CartItem(**item_data)

    def clear_cart(self, user_id: int) -> bool:
        cart_key = self._get_cart_key(user_id)
        return bool(self.redis.delete(cart_key))