from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class UpsertVectorDB:
    """Qdrant vector database with upsert support for CDC operations"""
    
    def __init__(self, path: str = ":memory:", collection_name: str = "livevectorlake"):
        self.client = QdrantClient(path)  # Use persistent path in production
        self.collection_name = collection_name
    
    def create_collection(self, vector_size: int):
        """Create collection with specified vector size"""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    
    def upsert_vectors(self, ids: List[str], vectors: List[List[float]], 
                      metadatas: List[Dict], documents: List[str]):
        """Upsert vectors - insert new or update existing"""
        points = [
            PointStruct(id=hash(id_), vector=vector, payload={**meta, "document": doc})
            for id_, vector, meta, doc in zip(ids, vectors, metadatas, documents)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search similar vectors"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return [{
            "document": hit.payload["document"],
            "metadata": hit.payload,
            "score": hit.score
        } for hit in results]