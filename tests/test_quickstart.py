# Contents of tests/test_quickstart.py

import unittest
from src.chunking.chunker import Chunker
from src.embedding.embedder import Embedder
from src.vectordb.db import VectorDB
from src.retrieval.retriever import Retriever
from src.generation.rag_llm import RagLLM

class TestQuickstart(unittest.TestCase):
    def setUp(self):
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.vector_db = VectorDB()
        self.retriever = Retriever()
        self.rag_llm = RagLLM()

        # Sample text for testing
        self.sample_text = "This is a sample document for testing the RAG pipeline."
        self.chunks = self.chunker.chunk_text(self.sample_text)
        self.embeddings = self.embedder.embed(self.chunks)

        # Store embeddings in the vector database
        for chunk, embedding in zip(self.chunks, self.embeddings):
            self.vector_db.add_vector(embedding, {"chunk": chunk})

    def test_chunking(self):
        self.assertGreater(len(self.chunks), 0, "Chunking failed, no chunks created.")

    def test_embedding(self):
        self.assertEqual(len(self.embeddings), len(self.chunks), "Embedding count does not match chunk count.")

    def test_vector_storage(self):
        for chunk in self.chunks:
            vector = self.vector_db.get_vector({"chunk": chunk})
            self.assertIsNotNone(vector, f"Vector for chunk '{chunk}' not found in DB.")

    def test_retrieval(self):
        retrieved = self.retriever.retrieve_top_k(self.embeddings[0], k=1)
        self.assertGreater(len(retrieved), 0, "Retrieval failed, no vectors returned.")

    def test_rag_generation(self):
        answer = self.rag_llm.generate_answer("What is this document about?")
        self.assertIsNotNone(answer, "RAG answer generation failed, no answer returned.")

if __name__ == '__main__':
    unittest.main()