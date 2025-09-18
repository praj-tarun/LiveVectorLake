import unittest
from src.chunking.chunker import Chunker

class TestChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = Chunker()

    def test_chunk_text(self):
        text = "This is a sample document. It contains multiple sentences."
        expected_chunks = [
            "This is a sample document.",
            "It contains multiple sentences."
        ]
        chunks = self.chunker.chunk_text(text)
        self.assertEqual(chunks, expected_chunks)

    def test_get_chunks(self):
        text = "Another example document for testing."
        self.chunker.chunk_text(text)
        chunks = self.chunker.get_chunks()
        self.assertEqual(len(chunks), 1)  # Assuming chunking results in one chunk

    # TODO: Add more tests for edge cases, such as empty strings, very long texts, etc.

if __name__ == '__main__':
    unittest.main()