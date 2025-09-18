# Quickstart Example for RAG Pipeline

import os
from src.chunking.chunker import Chunker
from src.embedding.embedder import Embedder
from src.vectordb.db import VectorDB
from src.retrieval.retriever import Retriever
from src.generation.rag_llm import RagLLM

def main():
    # Step 1: Load documents
    document_path = os.path.join('data', 'example.txt')
    with open(document_path, 'r') as file:
        raw_text = file.read()

    # Step 2: Chunk the document
    chunker = Chunker()
    chunks = chunker.chunk_text(raw_text)

    # Step 3: Embed the chunks
    embedder = Embedder()
    embeddings = embedder.embed(chunks)

    # Step 4: Store the vectors in the vector database
    vector_db = VectorDB()
    for chunk, embedding in zip(chunks, embeddings):
        vector_db.add_vector(embedding, metadata={'content': chunk, 'ingest_date': '2023-10-01'})

    # Step 5: Retrieve top-k similar vectors
    retriever = Retriever(vector_db)
    query_embedding = embedder.embed(['What is the main topic of the document?'])[0]
    top_k_results = retriever.retrieve_top_k(query_embedding, k=5)

    # Step 6: Generate RAG answer
    rag_llm = RagLLM()
    answer = rag_llm.generate_answer(top_k_results)

    # Output the answer
    print("RAG Answer:", answer)

if __name__ == "__main__":
    main()