#test_service.py
import unittest
from unittest.mock import patch, MagicMock
from app.services import CartService
from app.models import CartItem
import json

class TestCartService(unittest.TestCase):
    def setUp(self):
        self.cart_service = CartService()
        self.redis_mock = MagicMock()
        self.cart_service.redis = self.redis_mock

    def test_add_new_item(self):
        self.redis_mock.hget.return_value = None
        
        item = self.cart_service.add_item(
            user_id=1,
            product_id=1,
            price=99.99,
            quantity=2
        )
        
        self.assertEqual(item.product_id, 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 99.99)
        
        self.redis_mock.hset.assert_called_once()

    def test_add_existing_item(self):
        existing_item = {
            'product_id': 1,
            'price': 99.99,
            'quantity': 1
        }
        self.redis_mock.hget.return_value = json.dumps(existing_item)
        
        item = self.cart_service.add_item(
            user_id=1,
            product_id=1,
            price=99.99,
            quantity=1
        )
        
        self.assertEqual(item.quantity, 2)

    def test_get_cart_items(self):
        items = {
            '1': json.dumps({'product_id': 1, 'price': 99.99, 'quantity': 2}),
            '2': json.dumps({'product_id': 2, 'price': 49.99, 'quantity': 1})
        }
        self.redis_mock.hgetall.return_value = items
        
        cart_items = self.cart_service.get_cart_items(1)
        
        self.assertEqual(len(cart_items), 2)
        self.assertEqual(cart_items[0].quantity, 2)
        self.assertEqual(cart_items[1].price, 49.99)

    def test_update_quantity(self):
        existing_item = {
            'product_id': 1,
            'price': 99.99,
            'quantity': 1
        }
        self.redis_mock.hget.return_value = json.dumps(existing_item)
        
        updated_item = self.cart_service.update_quantity(1, 1, 3)
        
        self.assertEqual(updated_item.quantity, 3)

    def test_clear_cart(self):
        self.redis_mock.delete.return_value = 1
        result = self.cart_service.clear_cart(1)
        self.assertTrue(result)
        self.redis_mock.delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()