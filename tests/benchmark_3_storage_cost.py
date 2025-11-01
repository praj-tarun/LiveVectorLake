"""
Benchmark 3: Storage Cost Analysis

Measures storage overhead of maintaining full version history.
Analyzes hot tier (Milvus), cold tier (Delta Lake), and compression efficiency.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lakehouse.delta_store import DeltaLakeStore
from vectordb.milvus_db import MilvusDB


def get_directory_size(path: Path) -> int:
    """Calculate total size of directory in bytes."""
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total


def run_benchmark():
    """Analyze storage costs for dual-tier architecture."""
    
    lakehouse_dir = Path(__file__).parent.parent / "lakehouse" / "chunks"
    
    if not lakehouse_dir.exists():
        print("ERROR: Delta Lake not found. Run ingestion first.")
        return
    
    print("  Measuring storage...", end='', flush=True)
    
    # Measure Delta Lake (cold tier)
    delta_size_bytes = get_directory_size(lakehouse_dir)
    delta_size_mb = delta_size_bytes / (1024 * 1024)
    
    # Read Delta Lake to get chunk count and estimate hot tier
    try:
        delta_store = DeltaLakeStore()
        df = delta_store.read_chunks()
        print(" Done")
        
        total_chunks = len(df)
        active_chunks = len(df.filter(df['status'] == 'active'))
        
        # Estimate hot tier size (Milvus stores only active chunks)
        # Rough estimate: 384-dim vector (4 bytes/float) + metadata (~100 bytes)
        bytes_per_chunk = (384 * 4) + 100
        hot_size_bytes = active_chunks * bytes_per_chunk
        hot_size_mb = hot_size_bytes / (1024 * 1024)
        
        # Calculate metrics
        total_size_mb = hot_size_mb + delta_size_mb
        hot_cold_ratio = hot_size_mb / delta_size_mb if delta_size_mb > 0 else 0
        
        # Estimate compression (compare with uncompressed size)
        # Uncompressed: vector (1536 bytes) + text (~500 bytes avg) + metadata (100 bytes)
        uncompressed_bytes_per_chunk = 1536 + 500 + 100
        uncompressed_size_mb = (total_chunks * uncompressed_bytes_per_chunk) / (1024 * 1024)
        compression_ratio = uncompressed_size_mb / delta_size_mb if delta_size_mb > 0 else 0
        
        # Storage overhead vs no-history baseline
        baseline_size_mb = hot_size_mb  # Only current versions
        storage_overhead = total_size_mb / baseline_size_mb if baseline_size_mb > 0 else 0
        
        print(f"\nHot: {hot_size_mb:.1f}MB | Cold: {delta_size_mb:.1f}MB | Total: {total_size_mb:.1f}MB | Overhead: {storage_overhead:.1f}x | Compression: {compression_ratio:.1f}x")
        
        # Save results
        results = {
            "benchmark": "storage_cost",
            "corpus": {
                "documents": 100,
                "versions_per_doc": 5,
                "total_versions": 500
            },
            "storage": {
                "hot_tier_mb": hot_size_mb,
                "cold_tier_mb": delta_size_mb,
                "total_mb": total_size_mb,
                "baseline_mb": baseline_size_mb,
                "storage_overhead": storage_overhead
            },
            "efficiency": {
                "hot_cold_ratio": hot_cold_ratio,
                "compression_ratio": compression_ratio,
                "compression_savings_percent": ((compression_ratio - 1) / compression_ratio * 100)
            },
            "chunks": {
                "total": total_chunks,
                "active": active_chunks,
                "historical": total_chunks - active_chunks
            }
        }
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"storage_cost_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
    except Exception as e:
        print(f"ERROR: Cannot analyze Delta Lake: {e}")


if __name__ == "__main__":
    run_benchmark()
