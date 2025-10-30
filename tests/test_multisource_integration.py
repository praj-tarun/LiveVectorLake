"""Integration test for multi-source ingestion with conflict detection"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sources.wikipedia_connector import WikipediaConnector
from pipeline.cdc_ingest_simple import CDCIngestionPipeline
from cdc.conflict_detector import ConflictDetector
from lakehouse.delta_store import DeltaStore
import polars as pl
from datetime import datetime

def test_multisource_workflow():
    """Test complete multi-source workflow with conflict detection"""
    
    print("\n" + "="*60)
    print("MULTI-SOURCE INTEGRATION TEST")
    print("="*60)
    
    # Step 1: Fetch Wikipedia article
    print("\n[1] Fetching Wikipedia article on 'Artificial Intelligence'...")
    wiki = WikipediaConnector()
    wiki_article = wiki.get_article_content("Artificial intelligence")
    
    if not wiki_article:
        print("Failed to fetch Wikipedia article")
        return False
    
    print(f"  Title: {wiki_article['title']}")
    print(f"  Content length: {len(wiki_article['content'])} chars")
    print(f"  Source: {wiki_article['source']}")
    
    # Step 2: Create local file with conflicting content
    print("\n[2] Creating local file with conflicting content...")
    local_content = """Artificial Intelligence Overview
    
Artificial intelligence (AI) is intelligence demonstrated by machines. AI research focuses on creating intelligent agents that can perceive their environment and take actions to achieve goals. The field was established in 1956 and has grown significantly due to advances in computing power and data availability.

Machine learning is the primary approach in modern AI, using statistical techniques to enable computers to learn from data without explicit programming. Deep learning, a subset of machine learning, uses neural networks with multiple layers to process complex patterns.
"""
    
    test_file = "data/test_ai_local.txt"
    os.makedirs("data", exist_ok=True)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(local_content)
    
    print(f"  Created: {test_file}")
    print(f"  Content length: {len(local_content)} chars")
    
    # Step 3: Initialize pipeline
    print("\n[3] Initializing CDC pipeline...")
    pipeline = CDCIngestionPipeline()
    
    # Step 4: Ingest Wikipedia article
    print("\n[4] Ingesting Wikipedia article...")
    wiki_stats = pipeline.ingest_document(
        doc_id=wiki_article['doc_id'],
        content=wiki_article['content'],
        source="wikipedia"
    )
    print(f"  Added: {wiki_stats['added']} chunks")
    print(f"  Source: wikipedia")
    
    # Step 5: Ingest local file
    print("\n[5] Ingesting local file...")
    local_stats = pipeline.ingest_document(
        doc_id="ai_local_001",
        content=local_content,
        source="file"
    )
    print(f"  Added: {local_stats['added']} chunks")
    print(f"  Source: file")
    
    # Step 6: Query Delta Lake for both sources
    print("\n[6] Querying Delta Lake for active chunks from both sources...")
    delta = DeltaStore()
    df = delta.read_chunks(pl.col("status") == "active")
    
    if df is None or df.height == 0:
        print("  No chunks found in Delta Lake")
        return False
    
    wiki_chunks = df.filter(pl.col("source") == "wikipedia")
    file_chunks = df.filter(pl.col("source") == "file")
    
    print(f"  Wikipedia chunks: {wiki_chunks.height}")
    print(f"  File chunks: {file_chunks.height}")
    
    # Step 7: Detect conflicts
    print("\n[7] Running conflict detection...")
    detector = ConflictDetector()
    
    # Convert to list of dicts for conflict detector
    wiki_chunk_list = wiki_chunks.to_dicts()
    file_chunk_list = file_chunks.to_dicts()
    
    all_chunks = wiki_chunk_list + file_chunk_list
    conflicts = detector.detect_conflicts(all_chunks)
    
    print(f"  Detected {len(conflicts)} conflicts")
    
    if conflicts:
        print("\n  Conflict Details:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"\n  Conflict {i}:")
            print(f"    Sources: {conflict['sources']}")
            print(f"    Similarity: {conflict['similarity']:.4f}")
            print(f"    Chunk 1 (first 100 chars): {conflict['chunk1']['chunk_text'][:100]}...")
            print(f"    Chunk 2 (first 100 chars): {conflict['chunk2']['chunk_text'][:100]}...")
            
            # Resolve conflict
            winner = detector.resolve_conflict(conflict, strategy="source_authority")
            print(f"    Winner (source authority): {winner['source']}")
    
    # Cleanup
    print("\n[8] Cleanup...")
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"  Removed: {test_file}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_multisource_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
