import unittest
import json
from flask import Flask
from app import create_app
from app.models import db, User

class TestUserIntegration(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_flow(self):
        # Test registration
        response = self.client.post('/api/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'testuser')

        # Test duplicate registration
        response = self.client.post('/api/register',
            json={
                'username': 'testuser2',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_login_flow(self):
        # Register user
        self.client.post('/api/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )

        # Test successful login
        response = self.client.post('/api/login',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

        # Test wrong password
        response = self.client.post('/api/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_routes(self):
        # Register and get token
        response = self.client.post('/api/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        token = json.loads(response.data)['token']
        
        # Test accessing protected route with token
        response = self.client.get('/api/users/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)

        # Test accessing protected route without token
        response = self.client.get('/api/users/1')
        self.assertEqual(response.status_code, 401)

    def test_update_user_flow(self):
        # Register and get token
        response = self.client.post('/api/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        token = json.loads(response.data)['token']
        user_id = json.loads(response.data)['user']['id']

        # Update user
        response = self.client.put(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'updateduser',
                'email': 'updated@example.com'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'updateduser')
        self.assertEqual(data['email'], 'updated@example.com')

    def test_delete_user_flow(self):
        # Register and get token
        response = self.client.post('/api/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        token = json.loads(response.data)['token']
        user_id = json.loads(response.data)['user']['id']

        # Delete user
        response = self.client.delete(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)

        # Verify deletion
        response = self.client.get(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()