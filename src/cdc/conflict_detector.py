"""Conflict detection for multi-source ingestion"""
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

class ConflictDetector:
    """Detect contradictory information from multiple sources"""
    
    def __init__(self, similarity_threshold: float = 0.7, contradiction_threshold: float = 0.3):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.similarity_threshold = similarity_threshold
        self.contradiction_threshold = contradiction_threshold
    
    def detect_conflicts(self, chunks: List[Dict]) -> List[Dict]:
        """Detect conflicts between chunks from different sources
        
        Args:
            chunks: List of chunk dictionaries with keys:
                - chunk_id: str
                - content: str
                - source: str
                - doc_id: str
                - timestamp: int
        
        Returns:
            List of conflict dictionaries with:
                - chunk_ids: List[str] (conflicting chunks)
                - sources: List[str]
                - similarity: float
                - conflict_type: str
        """
        if len(chunks) < 2:
            return []
        
        # Group by source
        by_source = {}
        for chunk in chunks:
            source = chunk.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(chunk)
        
        # Need at least 2 sources for conflicts
        if len(by_source) < 2:
            return []
        
        conflicts = []
        sources = list(by_source.keys())
        
        # Compare chunks across sources
        for i, source1 in enumerate(sources):
            for source2 in sources[i+1:]:
                source1_chunks = by_source[source1]
                source2_chunks = by_source[source2]
                
                # Find semantically similar but textually different chunks
                for chunk1 in source1_chunks:
                    for chunk2 in source2_chunks:
                        conflict = self._check_conflict(chunk1, chunk2)
                        if conflict:
                            conflicts.append(conflict)
        
        return conflicts
    
    def _check_conflict(self, chunk1: Dict, chunk2: Dict) -> Dict:
        """Check if two chunks conflict
        
        Returns conflict dict if conflict detected, None otherwise
        """
        # Try multiple possible content keys
        content1 = chunk1.get('content') or chunk1.get('chunk_text') or chunk1.get('content_text', '')
        content2 = chunk2.get('content') or chunk2.get('chunk_text') or chunk2.get('content_text', '')
        
        if not content1 or not content2:
            return None
        
        # Embed both chunks
        embeddings = self.model.encode([content1, content2])
        
        # Compute cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        # High semantic similarity but different text = potential conflict
        if similarity > self.similarity_threshold:
            # Check if text is actually different
            if content1.strip() != content2.strip():
                return {
                    'chunk_ids': [chunk1['chunk_id'], chunk2['chunk_id']],
                    'sources': [chunk1.get('source', 'unknown'), chunk2.get('source', 'unknown')],
                    'doc_ids': [chunk1['doc_id'], chunk2['doc_id']],
                    'similarity': float(similarity),
                    'conflict_type': 'semantic_similar_text_different',
                    'timestamps': [chunk1.get('timestamp', 0), chunk2.get('timestamp', 0)],
                    'contents': [content1[:200], content2[:200]]  # Preview
                }
        
        return None
    
    def resolve_conflict(self, conflict: Dict, strategy: str = "timestamp") -> str:
        """Resolve conflict using specified strategy
        
        Args:
            conflict: Conflict dictionary
            strategy: "timestamp" (newer wins) or "source" (authority-based)
        
        Returns:
            Winning chunk_id
        """
        if strategy == "timestamp":
            # Newer timestamp wins
            timestamps = conflict['timestamps']
            winner_idx = 0 if timestamps[0] > timestamps[1] else 1
            return conflict['chunk_ids'][winner_idx]
        
        elif strategy == "source":
            # Source authority hierarchy: wikipedia > file
            sources = conflict['sources']
            source_priority = {'wikipedia': 2, 'file': 1, 'unknown': 0}
            
            priority1 = source_priority.get(sources[0], 0)
            priority2 = source_priority.get(sources[1], 0)
            
            winner_idx = 0 if priority1 >= priority2 else 1
            return conflict['chunk_ids'][winner_idx]
        
        else:
            # Default: first chunk wins
            return conflict['chunk_ids'][0]
    
    def get_conflict_summary(self, conflicts: List[Dict]) -> Dict:
        """Generate summary statistics for conflicts
        
        Returns:
            Dictionary with conflict statistics
        """
        if not conflicts:
            return {
                'total_conflicts': 0,
                'by_source_pair': {},
                'avg_similarity': 0.0
            }
        
        by_source_pair = {}
        similarities = []
        
        for conflict in conflicts:
            sources = tuple(sorted(conflict['sources']))
            by_source_pair[sources] = by_source_pair.get(sources, 0) + 1
            similarities.append(conflict['similarity'])
        
        return {
            'total_conflicts': len(conflicts),
            'by_source_pair': by_source_pair,
            'avg_similarity': sum(similarities) / len(similarities) if similarities else 0.0
        }
