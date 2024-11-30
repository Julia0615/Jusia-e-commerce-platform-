# intergration_test.py
import unittest
import requests
from flask import Flask
from app import create_app
from app.models import db
import json

class TestCartIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_integration.db'
        
        with cls.app.app_context():
            db.create_all()

    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
        }

    def test_cart_lifecycle(self):
        # Add item
        response = self.client.post('/api/cart/items', 
            headers=self.headers,
            json={
                'product_id': 1,
                'price': 99.99,
                'quantity': 2
            })
        self.assertEqual(response.status_code, 201)
        item_id = response.json['id']

        # Update quantity
        response = self.client.put(f'/api/cart/items/{item_id}',
            headers=self.headers,
            json={'quantity': 3})
        self.assertEqual(response.status_code, 200)

        # Get cart
        response = self.client.get('/api/cart/1', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        cart = response.json
        self.assertEqual(len(cart['items']), 1)
        self.assertEqual(cart['items'][0]['quantity'], 3)

        # Clear cart
        response = self.client.delete('/api/cart/1', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        # Invalid product
        response = self.client.post('/api/cart/items',
            headers=self.headers,
            json={'product_id': -1})
        self.assertEqual(response.status_code, 400)

        # Invalid quantity
        response = self.client.put('/api/cart/items/1',
            headers=self.headers,
            json={'quantity': 0})
        self.assertEqual(response.status_code, 400)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()