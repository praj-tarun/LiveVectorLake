# File: /livevectorlake/livevectorlake/tests/test_db.py

import unittest
from src.vectordb.db import VectorDB

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        """Set up a VectorDB instance for testing."""
        self.db = VectorDB()
        self.test_vector = [0.1, 0.2, 0.3]
        self.test_metadata = {
            'content': 'Test content',
            'ingest_date': '2023-10-01',
            'source': 'test_source',
            'chunk_id': 'chunk_1'
        }

    def test_add_vector(self):
        """Test adding a vector to the database."""
        self.db.add_vector(self.test_vector, self.test_metadata)
        stored_vector = self.db.get_vector('chunk_1')
        self.assertEqual(stored_vector['vector'], self.test_vector)
        self.assertEqual(stored_vector['metadata'], self.test_metadata)

    def test_get_vector(self):
        """Test retrieving a vector from the database."""
        self.db.add_vector(self.test_vector, self.test_metadata)
        retrieved_vector = self.db.get_vector('chunk_1')
        self.assertIsNotNone(retrieved_vector)
        self.assertEqual(retrieved_vector['vector'], self.test_vector)

    def test_delete_vector(self):
        """Test deleting a vector from the database."""
        self.db.add_vector(self.test_vector, self.test_metadata)
        self.db.delete_vector('chunk_1')
        retrieved_vector = self.db.get_vector('chunk_1')
        self.assertIsNone(retrieved_vector)

    def tearDown(self):
        """Clean up after each test."""
        self.db.delete_vector('chunk_1')

if __name__ == '__main__':
    unittest.main()