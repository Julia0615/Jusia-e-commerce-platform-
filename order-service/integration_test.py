# integration_test.py

import pytest
from decimal import Decimal
from flask import Flask
from app.models import db, Order, OrderItem

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

def test_create_and_retrieve_order(app):
   with app.app_context():
       test_order = Order(user_id=1, total_amount=999.99)
       
       test_item = OrderItem(
           product_id=1, 
           quantity=2,
           price=499.99
       )
       test_order.items.append(test_item)
       
       db.session.add(test_order)
       db.session.commit()
       
       retrieved_order = db.session.get(Order, test_order.id)
       assert retrieved_order is not None
       assert retrieved_order.total_amount == Decimal('999.99')
       assert retrieved_order.status == 'PENDING'
       assert len(retrieved_order.items) == 1
       
       item = retrieved_order.items[0]
       assert item.product_id == 1
       assert item.quantity == 2
       assert item.price == Decimal('499.99')

def test_order_to_dict(app):
   with app.app_context(): 
       test_order = Order(user_id=1, total_amount=999.99)
       
       test_item = OrderItem(
           product_id=1,
           quantity=2, 
           price=499.99
       )
       test_order.items.append(test_item)
       
       db.session.add(test_order)
       db.session.commit()
       
       order_dict = test_order.to_dict()
       assert order_dict['user_id'] == 1
       assert order_dict['total_amount'] == 999.99
       assert order_dict['status'] == 'PENDING'
       assert len(order_dict['items']) == 1
       
       item_dict = order_dict['items'][0]
       assert item_dict['product_id'] == 1
       assert item_dict['quantity'] == 2
       assert item_dict['price'] == 499.99

if __name__ == "__main__":
   pytest.main(["-v", __file__])