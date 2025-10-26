"""CDC-aware ingestion pipeline (simplified without Delta Lake for Python 3.13)"""
from typing import List, Dict
from datetime import datetime
from sentence_transformers import SentenceTransformer
import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from cdc.chunker import chunk_text, hash_chunk, create_chunk_record, compare_chunks
from cdc.hash_store import HashStore
from vectordb.milvus_db import MilvusDB

class CDCIngestionPipeline:
    """Ingestion pipeline with CDC support (simplified)"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", reset_milvus: bool = False):
        self.model = SentenceTransformer(embedding_model)
        self.hash_store = HashStore()
        self.milvus = MilvusDB()
        self.metadata_file = Path("cdc_metadata.json")
        
        # Initialize Milvus collection if needed
        if reset_milvus:
            self.milvus.connect()
            self.milvus.create_collection()
    
    def save_metadata(self, records: List[Dict]):
        """Save chunk metadata to JSON (replaces Delta Lake for now)"""
        existing = []
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        existing = data
            except:
                existing = []
        
        existing.extend(records)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
    def ingest_document(self, doc_id: str, content: str) -> Dict:
        """Ingest document with CDC detection"""
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
            record = {
                'chunk_id': chunk_hash,
                'text': chunk_content,
                'doc_id': doc_id,
                'chunk_index': idx,
                'valid_from': timestamp,
                'valid_to': None,
                'status': 'active'
            }
            added_records.append(record)
            added_texts.append(chunk_content)
            added_hashes.append(chunk_hash)
        
        # Step 4: Embed new chunks
        if added_texts:
            vectors = self.model.encode(added_texts).tolist()
            
            # Step 5: Insert into Milvus (hot tier)
            self.milvus.connect()
            doc_ids = [doc_id] * len(added_hashes)
            statuses = ['active'] * len(added_hashes)
            valid_from_list = [timestamp] * len(added_hashes)
            valid_to_list = [0] * len(added_hashes)  # 0 means NULL/active
            
            self.milvus.insert(added_hashes, vectors, statuses, doc_ids, valid_from_list, valid_to_list)
        
        # Step 6: Handle deleted chunks (mark inactive)
        deleted_records = []
        for chunk_hash in cdc_result['deleted']:
            record = {
                'chunk_id': chunk_hash,
                'text': '',
                'doc_id': doc_id,
                'chunk_index': -1,
                'valid_from': 0,
                'valid_to': timestamp,
                'status': 'inactive'
            }
            deleted_records.append(record)
        
        # Step 7: Save metadata to JSON
        all_records = added_records + deleted_records
        if all_records:
            self.save_metadata(all_records)
        
        # Step 8: Update hash store
        new_hash_set = {h for h, _ in chunk_tuples}
        self.hash_store.update_hashes(doc_id, new_hash_set)
        
        # Step 9: Return CDC summary
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
