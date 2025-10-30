"""CDC-aware ingestion pipeline with Delta Lake cold storage"""
from typing import List, Dict
from datetime import datetime
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from cdc.chunker import chunk_text, hash_chunk, create_chunk_record, compare_chunks
from cdc.hash_store import HashStore
from vectordb.milvus_db import MilvusDB
from lakehouse.delta_store import DeltaStore

class CDCIngestionPipeline:
    """Ingestion pipeline with CDC support and Delta Lake cold storage"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", reset_milvus: bool = False):
        self.model = SentenceTransformer(embedding_model)
        self.hash_store = HashStore()
        self.milvus = MilvusDB()
        self.delta_store = DeltaStore()
        
        # Initialize Milvus collection if needed
        if reset_milvus:
            self.milvus.connect()
            self.milvus.create_collection()
        
    def ingest_document(self, doc_id: str, content: str, source: str = "file") -> Dict:
        """Ingest document with CDC detection
        
        Args:
            doc_id: Document identifier
            content: Document text content
            source: Source type (file, wikipedia, stackoverflow, etc.)
        """
        # Step 1: Chunk and hash
        text_chunks = chunk_text(content)
        chunk_tuples = [(hash_chunk(chunk), chunk) for chunk in text_chunks]
        
        # Step 2: Compare with stored hashes
        old_hashes = self.hash_store.get_hashes(doc_id)
        cdc_result = compare_chunks(chunk_tuples, old_hashes)
        
        # Step 3: Process added chunks
        added_records = []
        added_texts = []
        added_hashes = []
        
        timestamp = int(datetime.utcnow().timestamp())
        
        for idx, (chunk_hash, chunk_content) in enumerate(cdc_result['added']):
            added_texts.append(chunk_content)
            added_hashes.append(chunk_hash)
        
        # Step 4: Embed new chunks
        delta_records = []
        if added_texts:
            vectors = self.model.encode(added_texts).tolist()
            
            # Step 5: Insert into Milvus (hot tier - active chunks only)
            self.milvus.connect()
            doc_ids = [doc_id] * len(added_hashes)
            statuses = ['active'] * len(added_hashes)
            valid_from_list = [timestamp] * len(added_hashes)
            valid_to_list = [0] * len(added_hashes)  # 0 means NULL/active
            
            self.milvus.insert(added_hashes, vectors, statuses, doc_ids, valid_from_list, valid_to_list)
            
            # Step 6: Insert into Delta Lake (cold tier - complete history)
            for idx, (chunk_hash, text_content, vector) in enumerate(zip(added_hashes, added_texts, vectors)):
                delta_records.append({
                    'chunk_id': chunk_hash,
                    'content_text': text_content,
                    'content_vector': vector,
                    'doc_id': doc_id,
                    'valid_from': timestamp,
                    'valid_to': 0,  # 0 means NULL/active
                    'status': 'active',
                    'version_number': 1,  # Simplified versioning
                    'source': source  # Track source
                })
        
        # Step 7: Handle deleted chunks (mark superseded in Delta Lake)
        for chunk_hash in cdc_result['deleted']:
            delta_records.append({
                'chunk_id': chunk_hash,
                'content_text': '',
                'content_vector': [0.0] * 384,  # Placeholder vector
                'doc_id': doc_id,
                'valid_from': 0,
                'valid_to': timestamp,
                'status': 'superseded',
                'version_number': 0
            })
        
        # Step 8: Write to Delta Lake
        if delta_records:
            self.delta_store.write_chunks(delta_records)
        
        # Step 9: Update hash store
        new_hash_set = {h for h, _ in chunk_tuples}
        self.hash_store.update_hashes(doc_id, new_hash_set)
        
        # Step 10: Return CDC summary
        summary = cdc_result['summary']
        summary['doc_id'] = doc_id
        summary['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        return summary
    
    def ingest_batch(self, documents: List[Dict]) -> Dict:
        """Ingest multiple documents"""
        batch_summary = {
            'total_docs': len(documents),
            'total_added': 0,
            'total_deleted': 0,
            'total_unchanged': 0,
            'doc_summaries': []
        }
        
        for doc in documents:
            summary = self.ingest_document(doc['doc_id'], doc['content'])
            batch_summary['total_added'] += summary['added']
            batch_summary['total_deleted'] += summary['deleted']
            batch_summary['total_unchanged'] += summary['unchanged']
            batch_summary['doc_summaries'].append(summary)
        
        return batch_summary
    
    def print_summary(self, summary: Dict):
        """Print CDC summary in readable format"""
        print("\n" + "="*60)
        print("CDC INGESTION SUMMARY")
        print("="*60)
        
        if 'total_docs' in summary:
            # Batch summary
            print(f"Documents processed: {summary['total_docs']}")
            print(f"Total chunks added: {summary['total_added']}")
            print(f"Total chunks deleted: {summary['total_deleted']}")
            print(f"Total chunks unchanged: {summary['total_unchanged']}")
        else:
            # Single document summary
            print(f"Document: {summary['doc_id']}")
            print(f"Chunks added: {summary['added']}")
            print(f"Chunks deleted: {summary['deleted']}")
            print(f"Chunks unchanged: {summary['unchanged']}")
            print(f"Total chunks: {summary['total_new']}")
        
        # Hash store stats
        stats = self.hash_store.get_stats()
        print(f"\nHash Store Stats:")
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  Total active chunks: {stats['total_chunks']}")
        print(f"  Avg chunks/doc: {stats['avg_chunks_per_doc']:.1f}")
        print("="*60 + "\n")
