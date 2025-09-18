import unittest
from src.embedding.embedder import Embedder

class TestEmbedder(unittest.TestCase):
    def setUp(self):
        """Set up the Embedder instance for testing."""
        self.embedder = Embedder()

    def test_embed(self):
        """Test the embedding of a single text chunk."""
        text_chunk = "This is a test chunk."
        embedding = self.embedder.embed(text_chunk)
        self.assertIsNotNone(embedding, "Embedding should not be None.")
        self.assertEqual(len(embedding), self.embedder.embedding_dimension, 
                         "Embedding dimension should match the expected size.")

    def test_get_embeddings(self):
        """Test the retrieval of embeddings for multiple text chunks."""
        text_chunks = ["First chunk.", "Second chunk.", "Third chunk."]
        embeddings = self.embedder.get_embeddings(text_chunks)
        self.assertEqual(len(embeddings), len(text_chunks), 
                         "Number of embeddings should match number of text chunks.")
        for embedding in embeddings:
            self.assertIsNotNone(embedding, "Each embedding should not be None.")
            self.assertEqual(len(embedding), self.embedder.embedding_dimension, 
                             "Embedding dimension should match the expected size.")

if __name__ == '__main__':
    unittest.main()