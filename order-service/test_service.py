#test_service.py
import unittest
from unittest.mock import Mock, patch
from app.services import OrderService
from app.models import Order, OrderItem

class TestOrderServiceUnit(unittest.TestCase):
    def setUp(self):
        self.service = OrderService()
        self.mock_client = Mock()
        self.service.client = self.mock_client

    @patch('app.services.db.session')
    def test_create_order_success(self, mock_session):
        # Arrange
        user_id = 1
        token = "test-token"
        cart_items = [
            {"product_id": 1, "quantity": 2, "price": 10.00}
        ]
        
        # Mock client responses
        self.mock_client.validate_user.return_value = True
        self.mock_client.get_cart_items.return_value = cart_items
        self.mock_client.clear_cart.return_value = True
        
        # Mock Order creation
        mock_order = Mock()
        mock_order.items = []
        # Mock the Order constructor
        with patch('app.services.Order') as mock_order_class:
            mock_order_class.return_value = mock_order
            
            # Act
            order = self.service.create_order(user_id, token)
            
            # Assert
            self.mock_client.validate_user.assert_called_once_with(user_id, token)
            self.mock_client.get_cart_items.assert_called_once_with(user_id, token)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @patch('app.services.db.session')
    def test_create_order_invalid_user(self, mock_session):
        # Arrange
        self.mock_client.validate_user.return_value = False
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.create_order(1, "invalid-token")
        
        self.assertEqual(str(context.exception), "Invalid user or token")
        mock_session.add.assert_not_called()

    @patch('app.services.db.session')
    def test_create_order_empty_cart(self, mock_session):
        # Arrange
        self.mock_client.validate_user.return_value = True
        self.mock_client.get_cart_items.return_value = []
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.create_order(1, "token")
        
        self.assertEqual(str(context.exception), "Cart is empty")
        mock_session.add.assert_not_called()

    def test_get_order(self):
        # Arrange
        mock_order = Mock()
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_order
        Order.query = mock_query
        
        # Act
        result = self.service.get_order(1, 1)
        
        # Assert
        self.assertEqual(result, mock_order)
        mock_query.filter_by.assert_called_once_with(id=1, user_id=1)

    @patch('app.services.Order.query')
    def test_get_user_orders(self, mock_query):
        # Arrange
        mock_orders = [Mock(), Mock()]
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = mock_orders
        
        # Act
        result = self.service.get_user_orders(1)
        
        # Assert
        self.assertEqual(result, mock_orders)
        mock_query.filter_by.assert_called_once_with(user_id=1)

if __name__ == '__main__':
    unittest.main()