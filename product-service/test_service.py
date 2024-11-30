import unittest
from unittest.mock import Mock, patch
from app.services import ProductService
from app.models import Product

class TestProductServiceUnit(unittest.TestCase):
    def setUp(self):
        self.service = ProductService()
        self.mock_s3 = Mock()
        self.service.s3 = self.mock_s3

    @patch('app.services.db.session')
    def test_create_product_success(self, mock_session):
        # Arrange
        product_data = {
            "name": "Test Laptop",
            "price": 999.99,
            "stock": 10,
            "description": "Test Description",
            "category": "Electronics"
        }
        
        # Mock Product creation
        mock_product = Mock()
        with patch('app.services.Product') as mock_product_class:
            mock_product_class.return_value = mock_product
            
            # Act
            product = self.service.create_product(product_data)
            
            # Assert
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @patch('app.services.db.session')
    def test_create_product_with_image(self, mock_session):
        # Arrange
        product_data = {
            "name": "Test Laptop",
            "price": 999.99,
            "stock": 10
        }
        mock_image = Mock()
        mock_image.filename = "test.jpg"
        mock_image.content_type = "image/jpeg"
        
        self.mock_s3.upload_fileobj.return_value = None
        
        # Act
        product = self.service.create_product(product_data, mock_image)
        
        # Assert
        self.mock_s3.upload_fileobj.assert_called_once()

    def test_get_product(self):
        # Arrange
        mock_product = Mock()
        with patch('app.services.db.session.get') as mock_get:
            mock_get.return_value = mock_product
            
            # Act
            result = self.service.get_product(1)
            
            # Assert
            self.assertEqual(result, mock_product)
            mock_get.assert_called_once_with(Product, 1)

    @patch('app.services.db.session')
    def test_update_stock(self, mock_session):
        # Arrange
        mock_product = Mock()
        mock_product.stock = 10
        
        with patch('app.services.ProductService.get_product') as mock_get:
            mock_get.return_value = mock_product
            
            # Act
            product = self.service.update_stock(1, -5)
            
            # Assert
            self.assertEqual(mock_product.stock, 5)
            mock_session.commit.assert_called_once()

    @patch('app.services.db.session')
    def test_insufficient_stock(self, mock_session):
        # Arrange
        mock_product = Mock()
        mock_product.stock = 10
        
        with patch('app.services.ProductService.get_product') as mock_get:
            mock_get.return_value = mock_product
            
            # Act & Assert
            with self.assertRaises(ValueError):
                self.service.update_stock(1, -15)
            
            mock_session.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()