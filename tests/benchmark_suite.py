"""Comprehensive benchmark suite for LiveVectorLake"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from pipeline.cdc_ingest_simple import CDCIngestionPipeline
from query_engine import QueryEngine
from lakehouse.delta_store import DeltaStore
from vectordb.milvus_db import MilvusDB

class BenchmarkSuite:
    """Benchmark suite for performance validation"""
    
    def __init__(self, corpus_dir: str = "data/benchmark_corpus"):
        self.corpus_dir = Path(corpus_dir)
        self.results = {}
        self.pipeline = None
        self.query_engine = None
        
    def setup(self):
        """Initialize pipeline and clean state"""
        print("\n[Setup] Initializing benchmark environment...")
        
        # Clean state
        if os.path.exists("cdc_hash_store.json"):
            os.remove("cdc_hash_store.json")
        
        # Initialize pipeline and query engine
        self.pipeline = CDCIngestionPipeline(reset_milvus=True)
        self.query_engine = QueryEngine()
        print("[Setup] Complete")
    
    def benchmark_ingestion_throughput(self, num_docs: int = 100) -> Dict:
        """Benchmark ingestion throughput"""
        print(f"\n[Benchmark] Ingestion Throughput ({num_docs} documents)...")
        
        # Get first version of each document
        files = sorted(self.corpus_dir.glob("doc_*_v1.txt"))[:num_docs]
        
        start_time = time.time()
        total_chunks = 0
        
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = file_path.stem
            summary = self.pipeline.ingest_document(doc_id, content, source="file")
            total_chunks += summary['added']
        
        elapsed = time.time() - start_time
        
        results = {
            'total_documents': num_docs,
            'total_chunks': total_chunks,
            'elapsed_seconds': round(elapsed, 2),
            'docs_per_second': round(num_docs / elapsed, 2),
            'chunks_per_second': round(total_chunks / elapsed, 2)
        }
        
        print(f"  Documents: {num_docs}")
        print(f"  Chunks: {total_chunks}")
        print(f"  Time: {results['elapsed_seconds']}s")
        print(f"  Throughput: {results['docs_per_second']} docs/s, {results['chunks_per_second']} chunks/s")
        
        return results
    
    def benchmark_cdc_detection(self, num_docs: int = 50) -> Dict:
        """Benchmark CDC detection accuracy and speed"""
        print(f"\n[Benchmark] CDC Detection ({num_docs} documents)...")
        
        # Ingest v1
        files_v1 = sorted(self.corpus_dir.glob("doc_*_v1.txt"))[:num_docs]
        for file_path in files_v1:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_id = file_path.stem.replace('_v1', '')
            self.pipeline.ingest_document(doc_id, content, source="file")
        
        # Ingest v2 and measure CDC
        files_v2 = sorted(self.corpus_dir.glob("doc_*_v2.txt"))[:num_docs]
        
        start_time = time.time()
        total_added = 0
        total_deleted = 0
        total_unchanged = 0
        
        for file_path in files_v2:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_id = file_path.stem.replace('_v2', '')
            summary = self.pipeline.ingest_document(doc_id, content, source="file")
            
            total_added += summary['added']
            total_deleted += summary['deleted']
            total_unchanged += summary['unchanged']
        
        elapsed = time.time() - start_time
        
        results = {
            'documents_updated': num_docs,
            'chunks_added': total_added,
            'chunks_deleted': total_deleted,
            'chunks_unchanged': total_unchanged,
            'elapsed_seconds': round(elapsed, 2),
            'cdc_speed': round(num_docs / elapsed, 2)
        }
        
        print(f"  Added: {total_added}, Deleted: {total_deleted}, Unchanged: {total_unchanged}")
        print(f"  CDC Speed: {results['cdc_speed']} docs/s")
        
        return results
    
    def benchmark_query_latency(self, num_queries: int = 20) -> Dict:
        """Benchmark query latency (hot and cold paths)"""
        print(f"\n[Benchmark] Query Latency ({num_queries} queries)...")
        
        queries = [
            "What is AI?",
            "Machine learning definition",
            "Cloud computing overview",
            "Cybersecurity policy",
            "Data science requirements"
        ]
        
        # Current queries (hot path)
        hot_latencies = []
        for i in range(num_queries):
            query = queries[i % len(queries)]
            start = time.time()
            results = self.query_engine.query_current(query, top_k=5)
            latency = (time.time() - start) * 1000  # ms
            hot_latencies.append(latency)
        
        # Historical queries (cold path)
        cold_latencies = []
        target_timestamp = int(datetime(2024, 2, 1).timestamp())
        
        for i in range(num_queries):
            query = queries[i % len(queries)]
            start = time.time()
            results = self.query_engine.query_historical(query, target_timestamp, top_k=5)
            latency = (time.time() - start) * 1000  # ms
            cold_latencies.append(latency)
        
        results = {
            'hot_path': {
                'p50': round(sorted(hot_latencies)[len(hot_latencies)//2], 2),
                'p95': round(sorted(hot_latencies)[int(len(hot_latencies)*0.95)], 2),
                'p99': round(sorted(hot_latencies)[int(len(hot_latencies)*0.99)], 2),
                'avg': round(sum(hot_latencies)/len(hot_latencies), 2)
            },
            'cold_path': {
                'p50': round(sorted(cold_latencies)[len(cold_latencies)//2], 2),
                'p95': round(sorted(cold_latencies)[int(len(cold_latencies)*0.95)], 2),
                'p99': round(sorted(cold_latencies)[int(len(cold_latencies)*0.99)], 2),
                'avg': round(sum(cold_latencies)/len(cold_latencies), 2)
            }
        }
        
        print(f"  Hot Path (Milvus): p50={results['hot_path']['p50']}ms, p95={results['hot_path']['p95']}ms")
        print(f"  Cold Path (Delta): p50={results['cold_path']['p50']}ms, p95={results['cold_path']['p95']}ms")
        
        return results
    
    def benchmark_storage_efficiency(self) -> Dict:
        """Benchmark storage efficiency"""
        print(f"\n[Benchmark] Storage Efficiency...")
        
        delta = DeltaStore()
        stats = delta.get_stats()
        
        # Estimate storage sizes (rough approximation)
        hot_size_mb = stats['active_chunks'] * 0.001  # ~1KB per chunk in Milvus
        cold_size_mb = stats['total_chunks'] * 0.0005  # ~0.5KB per chunk in Delta (compressed)
        
        results = {
            'total_chunks': stats['total_chunks'],
            'active_chunks': stats['active_chunks'],
            'superseded_chunks': stats['superseded_chunks'],
            'hot_storage_mb': round(hot_size_mb, 2),
            'cold_storage_mb': round(cold_size_mb, 2),
            'compression_ratio': round(hot_size_mb / cold_size_mb if cold_size_mb > 0 else 0, 2)
        }
        
        print(f"  Total Chunks: {results['total_chunks']}")
        print(f"  Hot Storage: {results['hot_storage_mb']} MB")
        print(f"  Cold Storage: {results['cold_storage_mb']} MB")
        print(f"  Compression Ratio: {results['compression_ratio']}x")
        
        return results
    
    def run_all(self) -> Dict:
        """Run all benchmarks"""
        print("\n" + "="*60)
        print("LIVEVECTORLAKE BENCHMARK SUITE")
        print("="*60)
        
        self.setup()
        
        self.results['ingestion'] = self.benchmark_ingestion_throughput(num_docs=100)
        self.results['cdc'] = self.benchmark_cdc_detection(num_docs=50)
        self.results['query'] = self.benchmark_query_latency(num_queries=20)
        self.results['storage'] = self.benchmark_storage_efficiency()
        
        # Save results
        output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "="*60)
        print(f"BENCHMARK COMPLETE - Results saved to {output_file}")
        print("="*60)
        
        return self.results

if __name__ == "__main__":
    suite = BenchmarkSuite()
    results = suite.run_all()
