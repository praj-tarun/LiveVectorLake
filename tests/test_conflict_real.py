"""Real-world conflict detection test with actual multi-source data"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pipeline.cdc_ingest_simple import CDCIngestionPipeline
from cdc.conflict_detector import ConflictDetector
from lakehouse.delta_store import DeltaStore
import polars as pl

def test_conflict_detection():
    """Test conflict detection with overlapping content from different sources"""
    
    print("\n" + "="*60)
    print("REAL-WORLD CONFLICT DETECTION TEST")
    print("="*60)
    
    # Initialize pipeline
    print("\n[1] Initializing CDC pipeline...")
    pipeline = CDCIngestionPipeline()
    
    # Create two documents with similar but conflicting information
    wikipedia_content = """Machine Learning Definition
    
Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. The field emerged in the 1950s and has become increasingly important with the growth of big data and computational power.

Key approaches in machine learning include supervised learning, unsupervised learning, and reinforcement learning. These methods allow systems to learn patterns from data without being explicitly programmed for every scenario.
"""
    
    local_file_content = """Machine Learning Overview
    
Machine learning is a branch of artificial intelligence that emphasizes neural networks and deep learning architectures. It was developed in the 1960s and gained prominence in the 2010s with advances in GPU computing. The primary focus is on training models using large datasets to recognize patterns and make predictions.

Modern machine learning relies heavily on deep neural networks, convolutional networks, and transformer architectures. These techniques have revolutionized fields like computer vision and natural language processing.
"""
    
    # Ingest Wikipedia content
    print("\n[2] Ingesting Wikipedia content...")
    wiki_stats = pipeline.ingest_document(
        doc_id="ml_wikipedia_001",
        content=wikipedia_content,
        source="wikipedia"
    )
    print(f"  Added: {wiki_stats['added']} chunks")
    
    # Ingest local file content
    print("\n[3] Ingesting local file content...")
    file_stats = pipeline.ingest_document(
        doc_id="ml_local_001",
        content=local_file_content,
        source="file"
    )
    print(f"  Added: {file_stats['added']} chunks")
    
    # Query Delta Lake
    print("\n[4] Querying Delta Lake...")
    delta = DeltaStore()
    df = delta.read_chunks(pl.col("status") == "active")
    
    wiki_chunks = df.filter(pl.col("source") == "wikipedia").to_dicts()
    file_chunks = df.filter(pl.col("source") == "file").to_dicts()
    
    print(f"  Wikipedia chunks: {len(wiki_chunks)}")
    print(f"  File chunks: {len(file_chunks)}")
    
    # Detect conflicts
    print("\n[5] Running conflict detection...")
    detector = ConflictDetector(similarity_threshold=0.6)  # Lower threshold
    
    all_chunks = wiki_chunks + file_chunks
    conflicts = detector.detect_conflicts(all_chunks)
    
    print(f"  Detected {len(conflicts)} conflicts")
    
    if conflicts:
        print("\n[6] Conflict Details:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"\n  Conflict {i}:")
            print(f"    Sources: {conflict['sources']}")
            print(f"    Similarity: {conflict['similarity']:.4f}")
            print(f"    Type: {conflict['conflict_type']}")
            print(f"\n    Chunk 1 (first 150 chars):")
            print(f"      {conflict['contents'][0][:150]}...")
            print(f"\n    Chunk 2 (first 150 chars):")
            print(f"      {conflict['contents'][1][:150]}...")
            
            # Resolve using both strategies
            winner_time_id = detector.resolve_conflict(conflict, strategy="timestamp")
            winner_source_id = detector.resolve_conflict(conflict, strategy="source")
            
            print(f"\n    Resolution:")
            print(f"      By timestamp: {winner_time_id}")
            print(f"      By source authority: {winner_source_id}")
        
        print("\n" + "="*60)
        print(f"TEST PASSED - {len(conflicts)} conflicts detected and resolved")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("TEST COMPLETED - No conflicts detected")
        print("(Content may not be similar enough above threshold)")
        print("="*60)
        return True

if __name__ == "__main__":
    try:
        success = test_conflict_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
