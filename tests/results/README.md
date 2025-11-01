# Benchmark Results

This directory contains benchmark and baseline comparison results.

## Files

- `benchmark_results_*.json` - LiveVectorLake performance benchmarks
- `baseline_comparison_*.json` - Comparison with Standard RAG and Doc Versioning

## Latest Results

### Benchmark Suite (100 docs)
- **File**: `benchmark_results_20251031_180511.json`
- Ingestion: 1.58 chunks/s
- CDC: 100% accuracy
- Query: Hot 17.7ms p50, Cold 437ms p50
- Storage: 1.8x compression

### Baseline Comparison (20 docs)
- **File**: `baseline_comparison_20251031_193707.json`
- Standard RAG: 61.48s initial, 62.73s update, 13.35ms query
- Doc Versioning: 59.01s initial, 61.06s update, 16.72ms query
- LiveVectorLake: 62.17s initial, 61.16s update, 15.52ms query

## Running Benchmarks

```bash
# Full benchmark suite
python benchmark_suite.py

# Baseline comparison
python baseline_comparison.py
```
