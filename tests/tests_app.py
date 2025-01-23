import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest.mock import patch, MagicMock
from app import app, send_message_to_telegram
from models import UserInfo, UserSpending
from extensions import db

class TestApp(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for testing
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()

        # Initialize the test database
        with app.app_context():
            db.init_app(app)
            db.create_all()

            # Add sample data
            user1 = UserInfo(user_id=1, name="Test User", email="test1@example.com", age=25)
            user2 = UserInfo(user_id=2, name="Another User", email="test2@example.com", age=35)
            db.session.add_all([user1, user2])

            spending1 = UserSpending(user_id=1, money_spent=500, year=2023)
            spending2 = UserSpending(user_id=1, money_spent=700, year=2022)
            spending3 = UserSpending(user_id=2, money_spent=800, year=2023)
            db.session.add_all([spending1, spending2, spending3])

            db.session.commit()

    def tearDown(self):
        # Clean up the database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_total_spent(self):
        # Test the total_spent endpoint
        response = self.app.get('/total_spent/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"user_id": 1, "total_spending": 1200})

        response = self.app.get('/total_spent/3')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_average_spending_by_age(self):
        # Test the average_spending_by_age endpoint
        response = self.app.get('/average_spending_by_age')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "18-24": 0,
            "25-30": 600,
            "31-36": 800,
            "37-47": 0,
            "48-+": 0
        })

    @patch('app.collection')
    def test_write_to_mongodb(self, mock_collection):
        # Mock the MongoDB collection
        mock_insert = MagicMock()
        mock_collection.insert_one = mock_insert

        # Test valid data
        response = self.app.post('/write_to_mongodb', json={"user_id": 1, "total_spending": 1500})
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json)
        mock_insert.assert_called_once_with({"user_id": 1, "total_spending": 1500})

        # Test invalid data
        response = self.app.post('/write_to_mongodb', json={"user_id": 1, "total_spending": 500})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    # @patch('app.requests.post')
    # def test_send_average_to_telegram(self, mock_post):
    #     # Mock the Telegram API
    #     mock_post.return_value.status_code = 200
    #     response = self.app.get('/send_average_spending_to_telegram')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("message", response.json)
    #
    #     # Simulate a failure in sending the message
    #     mock_post.return_value.status_code = 400
    #     response = self.app.get('/send_average_spending_to_telegram')
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn("error", response.json)

if __name__ == "__main__":
    unittest.main()
