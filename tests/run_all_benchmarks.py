"""
Run all benchmarks for LiveVectorLake evaluation.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_benchmark(script_name: str, feature_name: str) -> bool:
    """Run a single benchmark script. Returns True if successful."""
    script_path = Path(__file__).parent / script_name
    
    print(f"\n[{feature_name}]")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            error_lines = result.stderr.strip().split('\n')
            if error_lines:
                print(f"FAILED: {error_lines[-1]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FAILED: Timeout (>10 min)")
        return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def main():
    """Run all benchmarks."""
    
    print("=" * 60)
    print("LIVEVECTORLAKE BENCHMARK SUITE")
    print("=" * 60)
    print("\nPrerequisites:")
    print("  1. Milvus running (docker-compose up -d)")
    print("  2. Benchmark corpus generated")
    print("  3. Initial ingestion completed")
    
    benchmarks = [
        ("benchmark_1_knowledge_freshness.py", "Feature 1: Knowledge Freshness"),
        ("benchmark_2_processing_efficiency.py", "Feature 2: Processing Efficiency"),
        ("benchmark_3_storage_cost.py", "Feature 3: Storage Cost"),
        ("benchmark_4_temporal_accuracy.py", "Feature 4: Temporal Accuracy")
    ]
    
    start_time = datetime.now()
    results = []
    
    for script, feature in benchmarks:
        success = run_benchmark(script, feature)
        results.append((feature, success))
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n{'=' * 60}")
    passed = sum(1 for _, success in results if success)
    print(f"Results: {passed}/{len(results)} passed")
    for feature, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {feature}")
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Results saved to: tests/results/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark suite interrupted by user.")
        sys.exit(1)
