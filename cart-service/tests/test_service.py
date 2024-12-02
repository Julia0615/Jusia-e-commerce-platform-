#test_service.py
import unittest
from unittest.mock import patch, MagicMock
from app.services import CartService
from app.models import CartItem, db

class TestCartService(unittest.TestCase):
    def setUp(self):
        self.cart_service = CartService()
        self.redis_mock = MagicMock()
        self.cart_service.redis = self.redis_mock

    def test_add_new_item(self):
        with patch('app.models.CartItem.query') as query_mock:
            query_mock.filter_by.return_value.first.return_value = None
            
            item = self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=2
            )
            
            self.assertEqual(item.product_id, 1)
            self.assertEqual(item.quantity, 2)
            self.assertEqual(float(item.price), 99.99)

    def test_add_existing_item(self):
        with patch('app.models.CartItem.query') as query_mock:
            existing_item = CartItem(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=1,
                session_id='cart:1'
            )
            query_mock.filter_by.return_value.first.return_value = existing_item
            
            item = self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=1
            )
            
            self.assertEqual(item.quantity, 2)

    def test_get_cart_items(self):
        with patch('app.models.CartItem.query') as query_mock:
            items = [
                CartItem(user_id=1, product_id=1, price=99.99, quantity=2, session_id='cart:1'),
                CartItem(user_id=1, product_id=2, price=49.99, quantity=1, session_id='cart:1')
            ]
            query_mock.filter_by.return_value.all.return_value = items
            
            cart_items = self.cart_service.get_cart_items(1)
            
            self.assertEqual(len(cart_items), 2)
            self.assertEqual(cart_items[0].quantity, 2)
            self.assertEqual(float(cart_items[1].price), 49.99)

    def test_update_quantity(self):
        with patch('app.models.CartItem.query') as query_mock:
            item = CartItem(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=1,
                session_id='cart:1'
            )
            query_mock.filter_by.return_value.first.return_value = item
            
            updated_item = self.cart_service.update_quantity(
                user_id=1,
                product_id=1,
                quantity=3
            )
            
            self.assertEqual(updated_item.quantity, 3)

    def test_clear_cart(self):
        with patch('app.models.CartItem.query') as query_mock:
            result = self.cart_service.clear_cart(1)
            self.assertTrue(result)
            query_mock.filter_by.return_value.delete.assert_called_once()

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=99.99,
                quantity=0
            )

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            self.cart_service.add_item(
                user_id=1,
                product_id=1,
                price=-99.99,
                quantity=1
            )

    def test_get_cart_key(self):
        cart_key = self.cart_service._get_cart_key(1)
        self.assertEqual(cart_key, 'cart:1')

    def test_redis_connection(self):
        self.cart_service._get_redis()
        self.assertIsNotNone(self.cart_service.redis)

if __name__ == '__main__':
    unittest.main()