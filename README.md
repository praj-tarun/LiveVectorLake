# LiveVectorLake

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A LIVE, self-updating knowledge base that avoids expensive full re-indexing**

## Overview

LiveVectorLake solves a critical problem in RAG systems: **How do you keep a knowledge base current without rebuilding it from scratch every time a document changes?**

### The Problem

Traditional RAG systems face three critical limitations:

1. **Expensive Re-indexing**: Change one paragraph → re-embed entire document (100% re-processing)
2. **No Temporal Queries**: Can't answer "What did the policy say 6 months ago?"
3. **No Audit Trail**: Can't prove what information was available when

### Our Solution: LIVE Knowledge Base

A **real-time, self-updating knowledge base** that:
- **LIVE Updates**: New information queryable in <2 seconds (287x faster than full re-index)
- **CDC Efficiency**: Only re-process changed chunks (10% vs 100%)
- **Temporal Queries**: Answer "What was X on date Y?" with 100% accuracy
- **Dual-Tier Storage**: Hot (current, <100ms) + Cold (history, <2s)
- **Complete Audit Trail**: ACID-consistent versioning (who, what, when)

**Assumption**: System assumes an existing ingestion pipeline. Focus is on CDC-based versioning and temporal query capability, not data source integration.

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            LIVEVECTORLAKE SYSTEM                                │
│                    LIVE Knowledge Base with CDC & Temporal Queries             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: DATA INGESTION & CDC                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                    ┌─────────────────────────────────┐                         │
│                    │   Document Sources              │                         │
│                    │   (Files, APIs, Databases)      │                         │
│                    └──────────┬──────────────────────┘                         │
│                               ▼                                                 │
│                    ┌─────────────────────┐                                     │
│                    │  Ingestion Pipeline │                                     │
│                    │  (Assumed existing) │                                     │
│                    └──────────┬──────────┘                                     │
│                               ▼                                                 │
│                    ┌─────────────────────┐                                     │
│                    │   CDC Chunker       │                                     │
│                    │  (chunker.py)       │                                     │
│                    │  - Split into chunks│                                     │
│                    │  - SHA-256 hashing  │                                     │
│                    │  - Change detection │                                     │
│                    └──────────┬──────────┘                                     │
│                               ▼                                                 │
│                    ┌─────────────────────┐                                     │
│                    │   Hash Store        │                                     │
│                    │  (hash_store.py)    │                                     │
│                    │  - In-memory cache  │                                     │
│                    │  - JSON persistence │                                     │
│                    │  - Fast comparison  │                                     │
│                    └──────────┬──────────┘                                     │
│                               │                                                 │
│         ┌─────────────────────┼─────────────────────┐                          │
│         ▼                     ▼                     ▼                          │
│    [NEW CHUNK]           [MODIFIED]            [UNCHANGED]                     │
│         │                     │                     │                          │
└─────────┼─────────────────────┼─────────────────────┼──────────────────────────┘
          │                     │                     │
          │                     │                     └──────> Skip Processing
          │                     │
          └─────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: EMBEDDING & VECTORIZATION                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                    ┌─────────────────────────────────┐                         │
│                    │  SentenceTransformers           │                         │
│                    │  Model: all-MiniLM-L6-v2        │                         │
│                    │  - Dimension: 384               │                         │
│                    │  - Speed: ~12 chunks/sec (CPU)  │                         │
│                    │  - Size: ~80MB                  │                         │
│                    └────────────┬────────────────────┘                         │
│                                 │                                               │
│                                 ▼                                               │
│                    ┌─────────────────────────────────┐                         │
│                    │  Vector Embeddings (384-dim)    │                         │
│                    │  + Metadata (doc_id, chunk_id,  │                         │
│                    │    timestamp, status, version)  │                         │
│                    └────────────┬────────────────────┘                         │
│                                 │                                               │
└─────────────────────────────────┼───────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: DUAL-TIER STORAGE (HOT + COLD)                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌────────────────────────────────┐    ┌────────────────────────────────┐     │
│  │     HOT TIER (Milvus)          │    │    COLD TIER (Delta Lake)      │     │
│  │     (milvus_db.py)             │    │    (delta_store.py)            │     │
│  ├────────────────────────────────┤    ├────────────────────────────────┤     │
│  │                                │    │                                │     │
│  │  Purpose:                      │    │  Purpose:                      │     │
│  │  - Current/Active chunks only  │    │  - Complete version history    │     │
│  │  - Fast vector similarity      │    │  - All states (active,         │     │
│  │                                │    │    superseded, deleted)        │     │
│  │  Performance:                  │    │                                │     │
│  │  - Query: <100ms               │    │  Performance:                  │     │
│  │  - In-memory index             │    │  - Query: <2s                  │     │
│  │                                │    │  - Compressed Parquet          │     │
│  │  Storage:                      │    │                                │     │
│  │  - Vectors (384-dim)           │    │  Storage:                      │     │
│  │  - Minimal metadata:           │    │  - Vectors (384-dim)           │     │
│  │    * doc_id                    │    │  - Full metadata:              │     │
│  │    * chunk_id                  │    │    * doc_id                    │     │
│  │    * chunk_hash                │    │    * chunk_id                  │     │
│  │    * timestamp                 │    │    * chunk_hash                │     │
│  │    * status (active)           │    │    * chunk_text                │     │
│  │                                │    │    * timestamp                 │     │
│  │  Operations:                   │    │    * valid_from                │     │
│  │  - INSERT (new chunks)         │    │    * valid_to                  │     │
│  │  - DELETE (superseded chunks)  │    │    * status (active/           │     │
│  │  - SEARCH (vector similarity)  │    │      superseded/deleted)       │     │
│  │                                │    │    * version                   │     │
│  │  Collection Schema:            │    │                                │     │
│  │  ┌──────────────────────────┐ │    │  Operations:                   │     │
│  │  │ Field      │ Type         │ │    │  - APPEND (all changes)        │     │
│  │  ├──────────────────────────┤ │    │  - UPDATE (mark superseded)    │     │
│  │  │ id         │ INT64 (PK)   │ │    │  - TIME-TRAVEL queries         │     │
│  │  │ doc_id     │ VARCHAR      │ │    │  - ACID transactions           │     │
│  │  │ chunk_id   │ VARCHAR      │ │    │                                │     │
│  │  │ chunk_hash │ VARCHAR      │ │    │  Delta Lake Features:          │     │
│  │  │ embedding  │ FLOAT_VECTOR │ │    │  - Schema evolution            │     │
│  │  │ timestamp  │ INT64        │ │    │  - Time travel (AS OF)         │     │
│  │  │ status     │ VARCHAR      │ │    │  - ACID guarantees             │     │
│  │  └──────────────────────────┘ │    │  - Parquet compression         │     │
│  │                                │    │  - Polars integration          │     │
│  └────────────────────────────────┘    └────────────────────────────────┘     │
│                                                                                 │
│  WRITE FLOW:                                                                    │
│  1. New chunk      → INSERT to Milvus (hot)  + APPEND to Delta Lake (cold)    │
│  2. Modified chunk → DELETE old from Milvus  + UPDATE old in Delta Lake        │
│                      INSERT new to Milvus    + APPEND new to Delta Lake        │
│  3. Deleted chunk  → DELETE from Milvus      + UPDATE status in Delta Lake     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: QUERY ENGINE                                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                    ┌─────────────────────────────────┐                         │
│                    │   Query Parser                  │                         │
│                    │   - Detect temporal intent      │                         │
│                    │   - Extract time constraints    │                         │
│                    └────────────┬────────────────────┘                         │
│                                 │                                               │
│                                 ▼                                               │
│                    ┌─────────────────────────────────┐                         │
│                    │   Query Router                  │                         │
│                    │   - Route to hot/cold/hybrid    │                         │
│                    └────────────┬────────────────────┘                         │
│                                 │                                               │
│         ┌───────────────────────┼───────────────────────┐                     │
│         ▼                       ▼                       ▼                     │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐              │
│  │ CURRENT     │        │ HISTORICAL  │        │ COMPARATIVE │              │
│  │ Query       │        │ Query       │        │ Query       │              │
│  │             │        │             │        │             │              │
│  │ → Milvus    │        │ → Delta Lake│        │ → Both tiers│              │
│  │ → <100ms    │        │ → <2s       │        │ → Timeline  │              │
│  │ → Active    │        │ → AS OF     │        │ → Diff view │              │
│  │   chunks    │        │   timestamp │        │             │              │
│  └─────────────┘        └─────────────┘        └─────────────┘              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: INTERFACE                                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌────────────────────────────────┐    ┌────────────────────────────────┐     │
│  │     CLI (cli.py)               │    │    Web UI                      │     │
│  ├────────────────────────────────┤    ├────────────────────────────────┤     │
│  │                                │    │                                │     │
│  │  Commands:                     │    │  Features:                     │     │
│  │  - ingest <path> [--reset]     │    │  - Document upload             │     │
│  │  - query <text> [--as-of]      │    │  - Query interface             │     │
│  │  - audit <doc_id>              │    │  - CDC visualization           │     │
│  │                                │    │  - Version timeline            │     │
│  │  Output:                       │    │  - Diff highlighting           │     │
│  │  - CDC summary                 │    │  - Source attribution          │     │
│  │  - Hash store stats            │    │                                │     │
│  │  - Performance metrics         │    │  Technology: Streamlit         │     │
│  │                                │    │                                │     │
│  └────────────────────────────────┘    └────────────────────────────────┘     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE (cdc_ingest_simple.py)                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

  Document File
       │
       ▼
  ┌─────────┐
  │  Load   │  text_loader.py (load text files)
  └────┬────┘
       │
       ▼
  ┌─────────┐
  │  Chunk  │  chunker.py (split, hash with SHA-256)
  └────┬────┘
       │
       ▼
  ┌──────────────────┐
  │  CDC Detection   │  Compare with hash_store.py
  └────┬─────────────┘
       │
       ├─────────────┬─────────────┬─────────────┐
       ▼             ▼             ▼             ▼
   [NEW]       [MODIFIED]    [DELETED]    [UNCHANGED]
       │             │             │             │
       │             │             │             └──> Skip
       │             │             │
       ▼             ▼             ▼
  ┌─────────────────────────────────────┐
  │  Embed (SentenceTransformers)       │
  │  384-dim vectors                    │
  └────┬────────────────────────────────┘
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
  ┌─────────┐      ┌──────────┐      ┌──────────┐
  │ Milvus  │      │  Delta   │      │   Hash   │
  │ INSERT  │      │  Lake    │      │  Store   │
  │ (hot)   │      │  APPEND  │      │  UPDATE  │
  │         │      │  (cold)  │      │          │
  └─────────┘      └──────────┘      └──────────┘
```

### Data Flow: Query Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  QUERY PIPELINE                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

  User Query: "What is AI?" [--as-of 2024-01-15]
       │
       ▼
  ┌──────────────┐
  │ Parse Query  │  Extract: text, temporal intent, time constraint
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Embed Query  │  SentenceTransformers → 384-dim vector
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Route Query  │  Decide: hot / cold / hybrid path
  └──────┬───────┘
         │
         ├─────────────────┬─────────────────┬─────────────────┐
         ▼                 ▼                 ▼                 ▼
    [CURRENT]        [HISTORICAL]      [COMPARATIVE]     [HYBRID]
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
  │  Milvus  │      │  Delta   │      │  Delta   │      │  Both    │
  │  Search  │      │  Lake    │      │  Lake    │      │  Tiers   │
  │          │      │  AS OF   │      │  Timeline│      │          │
  │  <100ms  │      │  <2s     │      │  Query   │      │  Merge   │
  └────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Rank & Merge │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Results    │
                         │ + Metadata   │
                         │ + Provenance │
                         └──────────────┘
```

### Core Components

1. **CDC Chunker** ([chunker.py](src/cdc/chunker.py))
   - Hash-based change detection at chunk level
   - SHA-256 hashing for content fingerprinting
   - Configurable chunk size and overlap

2. **Hash Store** ([hash_store.py](src/cdc/hash_store.py))
   - In-memory cache for fast hash comparison
   - JSON persistence (cdc_hash_store.json)
   - Tracks document → chunk → hash mappings

3. **Milvus (Hot Tier)** ([milvus_db.py](src/vectordb/milvus_db.py))
   - Active chunks only for fast retrieval
   - Vector similarity search (<100ms)
   - In-memory index for performance

4. **Delta Lake (Cold Tier)** ([delta_store.py](src/lakehouse/delta_store.py))
   - Complete version history with ACID guarantees
   - Time-travel queries (AS OF timestamp)
   - Parquet compression for storage efficiency
   - Polars integration for fast analytics

5. **Embedding Engine**
   - Model: SentenceTransformers (all-MiniLM-L6-v2)
   - Dimension: 384
   - Speed: ~12 chunks/sec (CPU)
   - Quality: Optimized for semantic similarity

6. **CDC Pipeline** ([cdc_ingest_simple.py](src/pipeline/cdc_ingest_simple.py))
   - Orchestrates ingestion flow
   - Handles new, modified, deleted, unchanged chunks
   - Dual-tier writes (hot + cold)
   - Transaction coordination

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- 4GB RAM minimum

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/LiveVectorLake.git
cd LiveVectorLake

# Install dependencies
pip install -r requirements.txt

# Start Milvus
docker-compose up -d
```

### Generate Test Data

```bash
python tests/generate_test_data.py
```

This creates:
- `data/test_news/` - 5 initial articles
- `data/test_news_v2/` - Same articles with 2 modifications

### Run CDC Ingestion

```bash
# Initial ingestion
python src/cli.py ingest data/test_news --reset

# Ingest modified data (test CDC)
python src/cli.py ingest data/test_news_v2
```

**Expected Output**:
```
============================================================
CDC INGESTION SUMMARY
============================================================
Documents processed: 5
Total chunks added: 2      ← CDC detected changes!
Total chunks deleted: 2
Total chunks unchanged: 8

Hash Store Stats:
  Total documents: 5
  Total active chunks: 10
  Avg chunks/doc: 2.0
============================================================
```

---

## Implementation Status

### Completed Features

**CDC Foundation + Storage**:
- Hash-based CDC with SHA-256 (100% accuracy)
- Dual-tier storage (Milvus hot + Delta Lake cold)
- ACID transactions with Delta Lake
- Time-travel queries on historical data

**Query Engine**:
- Query router (hot/cold path selection)
- Current queries (Milvus, 17.7ms p50)
- Historical queries (Delta Lake, 437ms p50)
- CLI with --as-of and --top-k flags
- Test suite (4/4 passing)

**Web Interface**:
- Streamlit-based UI
- Document upload and ingestion
- Query interface (current + historical)
- CDC visualization

**Benchmarking** (In-Progress):

*Completed:*
- **Benchmark 1: Knowledge Freshness** - Measures update-to-query latency (0.13s vs 303s baseline, 2338× faster)
- **Benchmark 2: Processing Efficiency** - Measures CDC savings (2.4% vs 100% re-processing, 97.6% savings)
- **Benchmark 3: Storage Cost** - Analyzes hot/cold tier overhead (4.5× total, 1.8× compression)
- **Benchmark 4: Temporal Accuracy** - Validates historical query precision (96% accuracy, 0% leakage)
- Versioned corpus (100 docs × 5 versions)
- Standard RAG baseline comparison
- Automated benchmark suite with progress tracking
- Prerequisite checker for setup validation

*Planned:*
- **Scalability Testing** - Test with 1K, 10K, 100K documents to measure system limits
- **Performance Profiling** - CPU, memory, I/O bottleneck analysis and optimization
- **Storage Growth Analysis** - Long-term storage costs with version accumulation
- **End-to-End Latency** - Complete pipeline breakdown from ingestion to query

---

## Project Structure

```
LiveVectorLake/
├── data/
│   ├── test_news/          # Test data v1
│   └── test_news_v2/       # Test data v2 (modified)
├── docs/
│   ├── ARCHITECTURE.md     # System architecture
│   ├── BENCHMARKING_STRATEGY.md # Evaluation approach
│   ├── Problem_statement.md # Research problems
│   ├── Project.md          # Main project document
│   └── roadmap.md          # Implementation roadmap
├── src/
│   ├── cdc/
│   │   ├── chunker.py      # Hash-based CDC
│   │   ├── hash_store.py   # In-memory cache
│   │   └── pdf_parser.py   # Content extraction
│   ├── lakehouse/
│   │   └── delta_store.py  # Delta Lake storage
│   ├── pipeline/
│   │   └── cdc_ingest_simple.py # CDC pipeline
│   ├── sources/
│   │   └── text_loader.py  # File loader
│   ├── vectordb/
│   │   └── milvus_db.py    # Milvus integration
│   ├── app.py              # Streamlit web UI
│   ├── cli.py              # CLI tool
│   └── query_engine.py     # Query router
├── tests/
│   ├── baselines/
│   │   └── standard_rag.py # Baseline comparison
│   ├── benchmark_1_knowledge_freshness.py
│   ├── benchmark_2_processing_efficiency.py
│   ├── benchmark_3_storage_cost.py
│   ├── benchmark_4_temporal_accuracy.py
│   ├── check_prerequisites.py
│   ├── run_all_benchmarks.py
│   ├── generate_test_data.py
│   └── test_*.py           # Unit tests
├── .gitignore
├── docker-compose.yml
├── README.md
├── QUICKSTART.md
└── requirements.txt
```

---

## Testing

### Run Benchmarks

```bash
# Check prerequisites
python tests/check_prerequisites.py

# Run all benchmarks
python tests/run_all_benchmarks.py

# Run individual benchmarks
python tests/benchmark_1_knowledge_freshness.py
python tests/benchmark_2_processing_efficiency.py
python tests/benchmark_3_storage_cost.py
python tests/benchmark_4_temporal_accuracy.py
```

### Test CDC Detection

```bash
# Clean start
del cdc_hash_store.json

# Test 1: Initial ingestion (all chunks new)
python src/cli.py ingest data/test_news --reset

# Test 2: Re-ingest same data (all chunks unchanged)
python src/cli.py ingest data/test_news

# Test 3: Ingest modified data (2 chunks changed)
python src/cli.py ingest data/test_news_v2
```

### Validation Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Initial ingestion | 10 added | 10 added | Pass |
| Re-ingest same | 0 added, 10 unchanged | 0 added, 10 unchanged | Pass |
| Modified data | 2 added, 2 deleted, 8 unchanged | 2 added, 2 deleted, 8 unchanged | Pass |
| Current query | <100ms, results from Milvus | <100ms, 3 results | Pass |
| Historical query | <2s, results from Delta Lake | <2s, 5 results | Pass |
| Query routing | Correct tier selection | Hot/cold routing correct | Pass |

**CDC Detection Accuracy**: 100%
**Query Engine Tests**: 4/4 passing

---

## Performance

### Core Innovation Metrics

| Metric | Standard RAG | LiveVectorLake | Status |
|--------|--------------|----------------|--------|
| Time-to-Live | 344s (full re-index) | <2s (target) | In progress |
| CDC Efficiency | 100% re-process | 10% re-process | Pass |
| Temporal Queries | Not supported | 100% accuracy | Pass |
| Current Query | 16.55ms | 36.36ms | Pass |
| Historical Query | Not supported | 437ms | Pass |
| Audit Trail | No | Yes (100%) | Pass |

### System Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| CDC detection | 99% | 100% | Pass |
| Current query (hot) | <100ms | 17.7ms p50 | Pass |
| Historical query (cold) | <2s | 437ms p50 | Pass |
| Storage compression | >3x | 1.8x | Below target |
| Query engine tests | 4/4 pass | 4/4 pass | Pass |

### Embedding Details

- **Model**: all-MiniLM-L6-v2
- **Dimension**: 384
- **Size**: ~80MB
- **Speed**: ~12 chunks/sec (CPU)
- **Quality**: Good for general text

---

## CLI Commands

### Ingest

```bash
# Ingest directory
python src/cli.py ingest data/test_news

# Ingest with collection reset
python src/cli.py ingest data/test_news --reset

# Ingest single file
python src/cli.py ingest data/test_news/article_001.txt
```

### Query

```bash
# Current query (searches active chunks in Milvus)
python src/cli.py query "What is AI?"

# Historical query (searches Delta Lake at specific date)
python src/cli.py query "What is AI?" --as-of 2024-01-15

# Specify number of results
python src/cli.py query "What is AI?" --top-k 10
```

### Audit

```bash
# Show document history (planned)
python src/cli.py audit article_001
```

---

## Troubleshooting

### Milvus Connection Error

```bash
# Check Milvus is running
docker ps | grep milvus

# Restart if needed
docker-compose restart
```

### Hash Store Not Persisting

- Check file permissions in project root
- File: `cdc_hash_store.json`

### Embedding Slow

- First run downloads model (~80MB)
- Subsequent runs use cached model
- Consider GPU for faster embedding (future)

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Benchmarking Strategy](docs/BENCHMARKING_STRATEGY.md) - Evaluation approach
- [Problem Statement](docs/Problem_statement.md) - Research problems addressed
- [Project Document](docs/Project.md) - Complete research proposal
- [Roadmap](docs/roadmap.md) - Implementation timeline

---

## Future Work

### Multi-Source Ingestion
Extend to handle multiple data sources with conflict detection and resolution. Current implementation assumes a single ingestion pipeline.

### Temporal Embeddings
Embed time as additional vector dimensions (385-dim: 384 semantic + 1 temporal) for unified semantic-temporal similarity scoring.

### Scalability
Distributed deployment for petabyte-scale corpora with sharded vector DB and distributed lakehouse.

---

## License

This project is licensed under the MIT License.
