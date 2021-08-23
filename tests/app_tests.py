from app import app
import unittest


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_root_status(self):
        result = self.app.get("/")
        self.assertEqual(result.status_code, 200)

    def test_root_get(self):
        result = self.app.get("/")
        html = result.data.decode()
        self.assertIn("GET", html)
        self.assertIn("POST", html)
        self.assertIn("Welcome to Message in a Bottle", html)
