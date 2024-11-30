import unittest
from unittest.mock import Mock, patch
from flask import Flask
from app.models import db, User
from app import create_app

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        # Test user creation
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.username, 'testuser')
        self.assertTrue(saved_user.check_password('password123'))

    def test_password_hashing(self):
        # Test password hashing
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_user_to_dict(self):
        # Test to_dict method
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()
        self.assertEqual(user_dict['username'], 'testuser')
        self.assertEqual(user_dict['email'], 'test@example.com')
        self.assertNotIn('password_hash', user_dict)

    def test_unique_email(self):
        # Test unique email constraint
        user1 = User(
            username='user1',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user1)
        db.session.commit()

        user2 = User(
            username='user2',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_update_user(self):
        # Test user update
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()

        user.username = 'updateduser'
        db.session.commit()

        updated_user = User.query.get(user.id)
        self.assertEqual(updated_user.username, 'updateduser')