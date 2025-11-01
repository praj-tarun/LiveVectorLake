"""
Benchmark 1: Knowledge Freshness Latency

Measures how fast new information becomes queryable in the knowledge base.
Tests LiveVectorLake's incremental CDC updates vs Standard RAG's full re-indexing.
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "baselines"))

from pipeline.cdc_ingest_simple import CDCIngestionPipeline
from standard_rag import StandardRAG


def measure_livevectorlake(test_file: Path, doc_id: str) -> float:
    """Measure update-to-query time for LiveVectorLake (incremental CDC)."""
    print("  Testing LiveVectorLake...", end='', flush=True)
    
    try:
        pipeline = CDCIngestionPipeline(reset_milvus=False)
        
        start_time = time.time()
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        pipeline.ingest_document(doc_id, content)
        
        # Verify queryable
        pipeline.milvus.connect()
        test_vector = pipeline.model.encode("test query").tolist()
        pipeline.milvus.search(test_vector, limit=1)
        
        elapsed = time.time() - start_time
        print(f" {elapsed:.2f}s")
        return elapsed
    except Exception as e:
        print(f" FAILED")
        raise Exception(f"LiveVectorLake test failed: {e}")


def measure_standard_rag(test_files: list) -> float:
    """Measure update-to-query time for Standard RAG (full re-index)."""
    print("  Testing Standard RAG...", end='', flush=True)
    
    try:
        rag = StandardRAG(reset=True)
        
        start_time = time.time()
        for i, file_path in enumerate(test_files, 1):
            if i % 20 == 0:
                print(f" {i}/{len(test_files)}", end='', flush=True)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_id = Path(file_path).stem.replace('_v1', '')
            rag.ingest_document(doc_id, content)
        
        # Verify queryable
        rag.query("test query", top_k=1)
        
        elapsed = time.time() - start_time
        print(f" {elapsed:.2f}s")
        return elapsed
    except Exception as e:
        print(f" FAILED")
        raise Exception(f"Standard RAG test failed: {e}")


def run_benchmark():
    """Run knowledge freshness benchmark."""
    
    corpus_dir = Path(__file__).parent.parent / "data" / "benchmark_corpus"
    test_file = corpus_dir / "doc_001_v1.txt"
    
    if not corpus_dir.exists():
        print("ERROR: Benchmark corpus not found.")
        return
    
    all_files = sorted(corpus_dir.glob("*_v1.txt"))
    print(f"Corpus: {len(all_files)} documents")
    
    try:
        lvl_time = measure_livevectorlake(test_file, "doc_001")
        rag_time = measure_standard_rag([str(f) for f in all_files])
        
        print(f"\nStandard RAG: {rag_time:.2f}s | LiveVectorLake: {lvl_time:.2f}s | {rag_time / lvl_time:.1f}x faster")
    except Exception as e:
        print(f"\nERROR: {e}")
        return
    
    # Save results
    results = {
        "benchmark": "knowledge_freshness",
        "corpus_size": len(all_files),
        "livevectorlake_seconds": lvl_time,
        "standard_rag_seconds": rag_time,
        "speedup": rag_time / lvl_time
    }
    
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"knowledge_freshness_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    run_benchmark()
