import unittest
from app import app

class TestNotesAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_categories(self):
        response = self.app.get('/api/categories')
        self.assertEqual(response.status_code, 200)

    def test_get_notes(self):
        response = self.app.get('/api/notes')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
