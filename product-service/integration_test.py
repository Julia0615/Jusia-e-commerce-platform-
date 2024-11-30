# integration_test.py
import pytest
from flask import Flask
from app.models import db, Product

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_and_retrieve_product(app):
    with app.app_context():
        # Create test product
        test_product = Product(
            name="Test Laptop",
            description="Test Description",
            price=999.99,
            stock=10,
            category="Electronics"
        )
        
        # Save to database
        db.session.add(test_product)
        db.session.commit()
        
        # Retrieve and verify
        retrieved_product = db.session.get(Product, test_product.id)
        assert retrieved_product is not None
        assert retrieved_product.name == "Test Laptop"
        assert float(retrieved_product.price) == 999.99
        assert retrieved_product.stock == 10
        assert retrieved_product.category == "Electronics"

def test_product_to_dict(app):
    with app.app_context():
        test_product = Product(
            name="Test Laptop",
            description="Test Description",
            price=999.99,
            stock=10,
            category="Electronics"
        )
        
        db.session.add(test_product)
        db.session.commit()
        
        product_dict = test_product.to_dict()
        assert product_dict['name'] == "Test Laptop"
        assert product_dict['price'] == 999.99
        assert product_dict['stock'] == 10
        assert product_dict['category'] == "Electronics"

if __name__ == "__main__":
    pytest.main(["-v", __file__])


