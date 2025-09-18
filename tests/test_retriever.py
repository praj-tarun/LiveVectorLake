# tests/test_retriever.py

import unittest
from src.retrieval.retriever import Retriever
from src.vectordb.db import VectorDB

class TestRetriever(unittest.TestCase):
    def setUp(self):
        # Initialize a VectorDB instance for testing
        self.vector_db = VectorDB()
        self.retriever = Retriever(self.vector_db)

        # Sample data for testing
        self.sample_vectors = [
            {"id": 1, "vector": [0.1, 0.2, 0.3], "metadata": {"source": "doc1"}},
            {"id": 2, "vector": [0.4, 0.5, 0.6], "metadata": {"source": "doc2"}},
            {"id": 3, "vector": [0.7, 0.8, 0.9], "metadata": {"source": "doc3"}},
        ]

        # Add sample vectors to the vector database
        for vec in self.sample_vectors:
            self.vector_db.add_vector(vec["id"], vec["vector"], vec["metadata"])

    def test_retrieve_top_k(self):
        # Test retrieval of top-k similar vectors
        query_vector = [0.1, 0.2, 0.3]
        top_k = self.retriever.retrieve_top_k(query_vector, k=2)

        # Check if the retrieved vectors are as expected
        self.assertEqual(len(top_k), 2)
        self.assertIn(top_k[0]["id"], [1, 2, 3])
        self.assertIn(top_k[1]["id"], [1, 2, 3])

    def test_hybrid_retrieve(self):
        # Test hybrid retrieval logic (stubbed for now)
        query_vector = [0.4, 0.5, 0.6]
        hybrid_results = self.retriever.hybrid_retrieve(query_vector)

        # Check if hybrid retrieval returns results (placeholder check)
        self.assertIsNotNone(hybrid_results)

    def tearDown(self):
        # Clean up the vector database after tests
        self.vector_db = None
        self.retriever = None

if __name__ == '__main__':
    unittest.main()