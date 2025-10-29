"""Query engine for current and historical retrieval"""
from typing import List, Dict, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from vectordb.milvus_db import MilvusDB
from lakehouse.delta_store import DeltaStore
import numpy as np
import polars as pl

class QueryEngine:
    """Handles current and historical queries with dual-tier retrieval"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)
        self.milvus = MilvusDB()
        self.delta_store = DeltaStore()
        
    def query_current(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Query current/active chunks from Milvus (hot tier)"""
        query_vector = self.model.encode(query_text).tolist()
        
        self.milvus.connect()
        
        # Debug: Check collection stats
        if not self.milvus.collection:
            from pymilvus import Collection
            self.milvus.collection = Collection(self.milvus.collection_name)
        
        self.milvus.collection.load()
        num_entities = self.milvus.collection.num_entities
        print(f"DEBUG: Collection has {num_entities} entities")
        
        results = self.milvus.search(query_vector, limit=top_k)
        print(f"DEBUG: Search returned {len(results)} results")
        
        formatted = self._format_results(results, query_type="current")
        
        # Enrich with content from Delta Lake for display
        chunk_ids = [r['chunk_id'] for r in formatted if r['chunk_id']]
        if chunk_ids:
            delta_chunks = self.delta_store.read_chunks()
            if not delta_chunks.is_empty():
                for result in formatted:
                    chunk_data = delta_chunks.filter(
                        (pl.col('chunk_id') == result['chunk_id']) & 
                        (pl.col('status') == 'active')
                    )
                    if len(chunk_data) > 0:
                        result['content'] = chunk_data['content_text'][0]
                        result['timestamp'] = chunk_data['valid_from'][0]
        
        return formatted
    
    def query_historical(self, query_text: str, as_of_timestamp: int, top_k: int = 5) -> List[Dict]:
        """Query historical chunks from Delta Lake (cold tier)"""
        query_vector = self.model.encode(query_text)
        
        historical_chunks = self.delta_store.query_as_of(as_of_timestamp)
        
        if not historical_chunks:
            return []
        
        chunk_vectors = np.array([chunk['content_vector'] for chunk in historical_chunks])
        similarities = np.dot(chunk_vectors, query_vector) / (
            np.linalg.norm(chunk_vectors, axis=1) * np.linalg.norm(query_vector)
        )
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            chunk = historical_chunks[idx]
            results.append({
                'chunk_id': chunk['chunk_id'],
                'doc_id': chunk['doc_id'],
                'content': chunk['content_text'],
                'similarity': float(similarities[idx]),
                'timestamp': chunk['valid_from'],
                'status': chunk['status']
            })
        
        return results
    
    def _format_results(self, raw_results: List, query_type: str) -> List[Dict]:
        """Format search results consistently"""
        formatted = []
        for result in raw_results:
            formatted.append({
                'chunk_id': result.get('chunk_id'),
                'doc_id': result.get('doc_id'),
                'similarity': result.get('score', 0.0),
                'query_type': query_type
            })
        return formatted
    
    def print_results(self, results: List[Dict], query_text: str, query_type: str = "current"):
        """Print query results"""
        print("\n" + "="*60)
        print(f"QUERY RESULTS ({query_type.upper()})")
        print("="*60)
        print(f"Query: {query_text}")
        print(f"Results found: {len(results)}\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Document: {result['doc_id']}")
            print(f"   Chunk ID: {result['chunk_id']}")
            print(f"   Similarity: {result['similarity']:.4f}")
            if 'content' in result:
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"   Content: {content_preview}")
            if 'timestamp' in result:
                dt = datetime.fromtimestamp(result['timestamp'])
                print(f"   Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        print("="*60 + "\n")
