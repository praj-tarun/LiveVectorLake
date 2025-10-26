from typing import List, Dict, Any
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

class MilvusDB:
    def __init__(self, host: str = "localhost", port: str = "19530", collection_name: str = "doc_chunks"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None
        
    def connect(self):
        """Connect to Milvus"""
        connections.connect("default", host=self.host, port=self.port)
        
    def create_collection(self, dim: int = 384):
        """Create collection with schema including temporal fields"""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            
        fields = [
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=16),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="valid_from", dtype=DataType.INT64),
            FieldSchema(name="valid_to", dtype=DataType.INT64)
        ]
        schema = CollectionSchema(fields, "Document chunk collection with versioning")
        self.collection = Collection(self.collection_name, schema)
        
        # Create index
        index_params = {"metric_type": "IP", "index_type": "HNSW", "params": {"M": 16, "efConstruction": 200}}
        self.collection.create_index(field_name="vector", index_params=index_params)
        
    def insert(self, chunk_ids: List[str], vectors: List[List[float]], statuses: List[str], doc_ids: List[str], valid_from: List[int], valid_to: List[int]):
        """Insert vectors into collection with temporal metadata"""
        if not self.collection:
            self.collection = Collection(self.collection_name)
        
        data = [chunk_ids, vectors, statuses, doc_ids, valid_from, valid_to]
        self.collection.insert(data)
        self.collection.flush()
        
    def search(self, query_vector: List[float], limit: int = 5, filter_expr: str = "status == 'active'") -> List[Dict]:
        """Search for similar vectors"""
        if not self.collection:
            self.collection = Collection(self.collection_name)
        
        self.collection.load()
        search_params = {"metric_type": "IP", "params": {"ef": 128}}
        results = self.collection.search([query_vector], "vector", search_params, limit=limit, expr=filter_expr, output_fields=["chunk_id", "status", "doc_id", "valid_from", "valid_to"])
        
        return [{"chunk_id": hit.id, "score": hit.score, "status": hit.entity.get("status"), "doc_id": hit.entity.get("doc_id"), "valid_from": hit.entity.get("valid_from"), "valid_to": hit.entity.get("valid_to")} for hit in results[0]]
    
    def update_status(self, chunk_ids: List[str], new_status: str = "inactive"):
        """Mark chunks as inactive (for CDC)"""
        # Milvus doesn't support direct updates, so delete and reinsert
        self.collection.delete(f"chunk_id in {chunk_ids}")
