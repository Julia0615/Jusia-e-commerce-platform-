#test_service.py
import unittest
from unittest.mock import patch, MagicMock
from app.services import CartService
from app.models import CartItem
import json
import jwt

class TestCartService(unittest.TestCase):
    def setUp(self):
        self.cart_service = CartService()
        self.redis_mock = MagicMock()
        self.cart_service.redis = self.redis_mock
        
        # Create test JWT token
        self.test_token = jwt.encode(
            {'user_id': 1},
            'test-key',
            algorithm='HS256'
        )

    def test_add_new_item(self):
        self.redis_mock.hget.return_value = None
        
        item = self.cart_service.add_item(
            user_id=1,
            product_id=1,
            price=99.99,
            quantity=2,
            token=self.test_token
        )
        
        self.assertEqual(item.product_id, 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(float(item.price), 99.99)
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
            quantity=1,
            token=self.test_token
        )
        
        self.assertEqual(item.quantity, 2)

    def test_get_cart_items(self):
        items = {
            '1': json.dumps({'product_id': 1, 'price': 99.99, 'quantity': 2}),
            '2': json.dumps({'product_id': 2, 'price': 49.99, 'quantity': 1})
        }
        self.redis_mock.hgetall.return_value = items
        
        cart_items = self.cart_service.get_cart_items(1, self.test_token)
        
        self.assertEqual(len(cart_items), 2)
        self.assertEqual(cart_items[0].quantity, 2)
        self.assertEqual(float(cart_items[1].price), 49.99)

    def test_update_quantity(self):
        existing_item = {
            'product_id': 1,
            'price': 99.99,
            'quantity': 1
        }
        self.redis_mock.hget.return_value = json.dumps(existing_item)
        
        updated_item = self.cart_service.update_quantity(
            user_id=1,
            product_id=1,
            quantity=3,
            token=self.test_token
        )
        
        self.assertEqual(updated_item.quantity, 3)

    def test_clear_cart(self):
        self.redis_mock.delete.return_value = 1
        result = self.cart_service.clear_cart(1, self.test_token)
        self.assertTrue(result)
        self.redis_mock.delete.assert_called_once()

    def test_invalid_token(self):
        invalid_token = "invalid.token.here"
        
        with self.assertRaises(jwt.InvalidTokenError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=1,
                token=invalid_token
            )

    def test_expired_token(self):
        import time
        expired_token = jwt.encode(
            {
                'user_id': 1,
                'exp': int(time.time()) - 300  # Token expired 5 minutes ago
            },
            'test-key',
            algorithm='HS256'
        )
        
        with self.assertRaises(jwt.ExpiredSignatureError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=1,
                token=expired_token
            )

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=0,
                token=self.test_token
            )

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=-99.99,
                quantity=1,
                token=self.test_token
            )

if __name__ == '__main__':
    unittest.main()