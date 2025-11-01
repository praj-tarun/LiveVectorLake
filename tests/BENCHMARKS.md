# Benchmarking Suite

This directory contains benchmarks that validate LiveVectorLake's 4 core features.

## Benchmark Files

### Benchmark 1: Knowledge Freshness
**File**: `benchmark_1_knowledge_freshness.py`  
**Feature**: LIVE Knowledge Base (Speed)  
**Measures**: How fast new information becomes queryable  
**Comparison**: LiveVectorLake (CDC) vs Standard RAG (full re-index)

```bash
python tests/benchmark_1_knowledge_freshness.py
```

**Expected Output**:
- LiveVectorLake: ~0.13s
- Standard RAG: ~300s
- Improvement: ~2300× faster

---

### Benchmark 2: Processing Efficiency
**File**: `benchmark_2_processing_efficiency.py`  
**Feature**: CDC Efficiency (Avoid Unnecessary Work)  
**Measures**: % of chunks re-processed on document updates  
**Comparison**: LiveVectorLake (chunk-level CDC) vs Standard RAG (100% re-processing)

```bash
python tests/benchmark_2_processing_efficiency.py
```

**Expected Output**:
- LiveVectorLake: ~2.4% re-processed
- Standard RAG: 100% re-processed
- Savings: ~97.6% less processing

---

### Benchmark 3: Storage Cost
**File**: `benchmark_3_storage_cost.py`  
**Feature**: Dual-Tier Storage Efficiency  
**Measures**: Storage overhead of maintaining full version history  
**Analysis**: Hot tier (Milvus), Cold tier (Delta Lake), Compression ratio

```bash
python tests/benchmark_3_storage_cost.py
```

**Expected Output**:
- Hot tier: ~8 MB (current versions only)
- Cold tier: ~28 MB (all history, compressed)
- Storage overhead: ~4.5× vs no-history baseline
- Compression savings: ~44%

---

### Benchmark 4: Temporal Accuracy
**File**: `benchmark_4_temporal_accuracy.py`  
**Feature**: Temporal Queries & Audit Trail  
**Measures**: Accuracy and latency of historical queries  
**Comparison**: LiveVectorLake (supported) vs Standard RAG (not supported)

```bash
python tests/benchmark_4_temporal_accuracy.py
```

**Expected Output**:
- Temporal precision: ~96%
- Version leakage: 0%
- Audit completeness: 100%
- Average latency: ~400ms

---

## Running All Benchmarks

```bash
# Run individually
python tests/benchmark_1_knowledge_freshness.py
python tests/benchmark_2_processing_efficiency.py
python tests/benchmark_3_storage_cost.py
python tests/benchmark_4_temporal_accuracy.py
```

## Results

All benchmark results are saved to `tests/results/` as JSON files with timestamps.

## Prerequisites

**Check prerequisites:**
```bash
python tests/check_prerequisites.py
```

**Setup (if needed):**
```bash
# 1. Start Milvus
docker-compose up -d

# 2. Generate benchmark corpus
python tests/generate_versioned_corpus.py

# 3. Run initial ingestion
python src/cli.py ingest data/benchmark_corpus --reset
```

---

## Deprecated Files

The following files have been replaced by the new benchmark suite:
- `benchmark_time_to_live.py` → `benchmark_1_knowledge_freshness.py`
- `benchmark_cdc_efficiency.py` → `benchmark_2_processing_efficiency.py`
- `benchmark_temporal_queries.py` → `benchmark_4_temporal_accuracy.py`
- `benchmark_suite.py` → Run benchmarks individually

These old files are gitignored and can be deleted.
