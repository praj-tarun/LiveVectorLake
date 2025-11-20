"""Query engine for current and historical retrieval"""
from typing import List, Dict, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from vectordb.milvus_db import MilvusDB
from lakehouse.delta_store import DeltaStore
from llm_engine import LLMEngine
import numpy as np
import polars as pl

class QueryEngine:
    """Handles current and historical queries with dual-tier retrieval"""
    
    def __init__(self, milvus_db=None, delta_store=None, embedding_model: str = "all-MiniLM-L6-v2", 
                 use_llm: bool = True, llm_provider: str = "ollama", llm_model: str = "llama3:latest", api_key: Optional[str] = None):
        self.model = SentenceTransformer(embedding_model)
        self.milvus = milvus_db if milvus_db else MilvusDB()
        self.delta_store = delta_store if delta_store else DeltaStore()
        self.use_llm = use_llm
        self.llm = LLMEngine(provider=llm_provider, model=llm_model, api_key=api_key) if use_llm else None
    
    def get_system_status(self) -> Dict:
        """Get system status and metrics for monitoring dashboard"""
        try:
            self.milvus.connect()
            
            # Get Milvus stats
            try:
                from pymilvus import Collection, utility
                if utility.has_collection(self.milvus.collection_name):
                    collection = Collection(self.milvus.collection_name)
                    collection.load()
                    hot_tier_count = collection.num_entities
                else:
                    hot_tier_count = 0
            except:
                hot_tier_count = 0
            
            # Get Delta Lake stats
            try:
                cold_tier_count = self.delta_store.get_total_chunks()
            except:
                cold_tier_count = 0
            
            # Get unique documents
            try:
                unique_docs = self.delta_store.get_unique_documents()
                doc_count = len(unique_docs)
            except:
                doc_count = 0
            
            return {
                'status': 'connected',
                'hot_tier_chunks': hot_tier_count,
                'cold_tier_chunks': cold_tier_count,
                'total_documents': doc_count,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                'status': 'error',
                'hot_tier_chunks': 0,
                'cold_tier_chunks': 0,
                'total_documents': 0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
    def query_current(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Query current/active chunks from Milvus (hot tier - optimized)"""
        query_vector = self.model.encode(query_text).tolist()
        
        self.milvus.connect()
        results = self.milvus.search(query_vector, limit=top_k)
        
        formatted = []
        for result in results:
            formatted.append({
                'chunk_id': result.get('chunk_id'),
                'doc_id': result.get('doc_id'),
                'position': result.get('position'),
                'similarity': result.get('score', 0.0),
                'content': result.get('content', ''),
                'timestamp': result.get('valid_from'),
                'query_type': 'current'
            })
        
        return formatted
    
    def query_historical(self, query_text: str, as_of_timestamp: int, top_k: int = 5) -> List[Dict]:
        """Query historical chunks from Delta Lake (cold tier)"""
        query_vector = self.model.encode(query_text)
        
        historical_chunks = self.delta_store.query_as_of(as_of_timestamp)
        
        if not historical_chunks:
            return []
        
        chunk_vectors = np.array([chunk['content_vector'] for chunk in historical_chunks])
        norms = np.linalg.norm(chunk_vectors, axis=1) * np.linalg.norm(query_vector)
        norms = np.where(norms == 0, 1e-10, norms)  # Avoid division by zero
        similarities = np.dot(chunk_vectors, query_vector) / norms
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            chunk = historical_chunks[idx]
            results.append({
                'chunk_id': chunk['chunk_id'],
                'doc_id': chunk['doc_id'],
                'position': chunk.get('position'),
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
    
    def format_results_for_ui(self, results: List[Dict], query_text: str = "", query_type: str = "current") -> Dict:
        """Format results for UI display with full citations"""
        if not results:
            return {
                'answer': 'No relevant information found.',
                'sources': [],
                'total_results': 0
            }
        
        # Generate natural language answer using LLM
        if self.use_llm and self.llm and self.llm.is_available():
            answer_text = self.llm.generate_answer(query_text, results, query_type)
        else:
            # Fallback: concatenate top 3 chunks
            answer_chunks = results[:3]
            answer_text = ' '.join([r['content'] for r in answer_chunks if 'content' in r])
        
        # Format sources with full citation data
        sources = []
        for i, result in enumerate(results, 1):
            source = {
                'index': i,
                'doc_id': result.get('doc_id', 'Unknown'),
                'chunk_id': result.get('chunk_id', ''),
                'position': result.get('position'),
                'paragraph': result.get('position', 0) + 1 if result.get('position') is not None else None,
                'similarity': round(result.get('similarity', 0.0), 4),
                'content': result.get('content', ''),
                'snippet': result.get('content', '')[:150] + '...' if len(result.get('content', '')) > 150 else result.get('content', ''),
                'timestamp': result.get('timestamp'),
                'timestamp_formatted': datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if result.get('timestamp') else None
            }
            sources.append(source)
        
        return {
            'answer': answer_text,
            'sources': sources,
            'total_results': len(results)
        }
    
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
            if result.get('position') is not None:
                print(f"   Position: {result['position']} (paragraph {result['position'] + 1})")
            print(f"   Similarity: {result['similarity']:.4f}")
            if 'content' in result:
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"   Content: {content_preview}")
            if 'timestamp' in result:
                dt = datetime.fromtimestamp(result['timestamp'])
                print(f"   Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        print("="*60 + "\n")
