from fastapi import FastAPI
from src.chunking.chunker import Chunker
from src.embedding.embedder import Embedder
from src.vectordb.db import VectorDB
from src.retrieval.retriever import Retriever
from src.generation.rag_llm import RagLLM

def create_app() -> FastAPI:
    app = FastAPI()

    # Initialize components
    chunker = Chunker()
    embedder = Embedder()
    vector_db = VectorDB()
    retriever = Retriever(vector_db)
    rag_llm = RagLLM()

    @app.post("/ingest/")
    async def ingest_document(document: str):
        chunks = chunker.chunk_text(document)
        embeddings = embedder.embed(chunks)
        for chunk, embedding in zip(chunks, embeddings):
            vector_db.add_vector(embedding, {"content": chunk, "ingest_date": "TODO: Add date", "source": "local", "chunk_id": "TODO: Generate unique ID"})
        return {"message": "Document ingested successfully."}

    @app.get("/query/")
    async def query_rag(question: str):
        top_k = retriever.retrieve_top_k(question)
        answer = rag_llm.generate_answer(top_k)
        return {"answer": answer}

    return app