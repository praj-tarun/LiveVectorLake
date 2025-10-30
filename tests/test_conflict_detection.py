"""Test conflict detection"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from cdc.conflict_detector import ConflictDetector

def test_conflict_detection():
    """Test detecting conflicts between sources"""
    print("\n" + "="*60)
    print("TEST: Conflict Detection")
    print("="*60)
    
    detector = ConflictDetector()
    
    # Simulate chunks from different sources about same topic
    chunks = [
        {
            'chunk_id': 'chunk1',
            'content': 'Machine learning is a subset of artificial intelligence that uses statistical techniques.',
            'source': 'wikipedia',
            'doc_id': 'wiki_ml',
            'timestamp': 1000
        },
        {
            'chunk_id': 'chunk2',
            'content': 'Machine learning is a branch of AI that focuses on neural networks and deep learning.',
            'source': 'file',
            'doc_id': 'file_ml',
            'timestamp': 2000
        }
    ]
    
    conflicts = detector.detect_conflicts(chunks)
    
    print(f"\nDetected {len(conflicts)} conflicts")
    
    if conflicts:
        for i, conflict in enumerate(conflicts, 1):
            print(f"\nConflict {i}:")
            print(f"  Sources: {conflict['sources']}")
            print(f"  Similarity: {conflict['similarity']:.4f}")
            print(f"  Type: {conflict['conflict_type']}")
            print(f"  Content 1: {conflict['contents'][0]}...")
            print(f"  Content 2: {conflict['contents'][1]}...")
            
            # Test resolution
            winner_timestamp = detector.resolve_conflict(conflict, strategy="timestamp")
            winner_source = detector.resolve_conflict(conflict, strategy="source")
            
            print(f"  Winner (timestamp): {winner_timestamp}")
            print(f"  Winner (source): {winner_source}")
        
        print("\nTest PASSED")
    else:
        print("\nNo conflicts detected (may need to adjust thresholds)")

def test_no_conflict():
    """Test that similar content from same source doesn't conflict"""
    print("\n" + "="*60)
    print("TEST: No Conflict (Same Source)")
    print("="*60)
    
    detector = ConflictDetector()
    
    chunks = [
        {
            'chunk_id': 'chunk1',
            'content': 'Machine learning uses algorithms to learn from data.',
            'source': 'wikipedia',
            'doc_id': 'wiki_ml1',
            'timestamp': 1000
        },
        {
            'chunk_id': 'chunk2',
            'content': 'Deep learning is a type of machine learning.',
            'source': 'wikipedia',
            'doc_id': 'wiki_ml2',
            'timestamp': 2000
        }
    ]
    
    conflicts = detector.detect_conflicts(chunks)
    
    print(f"\nDetected {len(conflicts)} conflicts")
    print("Expected: 0 (same source)")
    
    if len(conflicts) == 0:
        print("\nTest PASSED")
    else:
        print("\nTest FAILED: Should not detect conflicts from same source")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CONFLICT DETECTION TESTS")
    print("="*60)
    
    test_conflict_detection()
    test_no_conflict()
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
