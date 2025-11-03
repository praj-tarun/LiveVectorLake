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

---

## Key Features

### Completed

**CDC Foundation + Storage**:
- Hash-based CDC with SHA-256 (100% accuracy)
- Position metadata for chunk tracking and audit trails
- Dual-tier storage (Milvus hot + Delta Lake cold)
- ACID transactions with Delta Lake
- Time-travel queries on historical data

**Query Engine**:
- Query router (hot/cold path selection)
- Current queries (Milvus, 17.7ms p50)
- Historical queries (Delta Lake, 437ms p50)
- CLI with --as-of and --top-k flags
- Test suite (4/4 passing)

**Evaluation**:
- Comprehensive benchmark suite (5 core benchmarks)
- Versioned corpus generator (100 docs × 5 versions)
- Standard RAG baseline comparison
- Web UI (Streamlit-based)

### In Progress

- Performance optimization (storage compression, CDC speed)
- Multi-source data integration
- Advanced conflict detection

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

### Basic Usage

```bash
# Generate test data
python tests/generate_test_data.py

# Initial ingestion
python src/cli.py ingest data/test_news --reset

# Ingest modified data (test CDC)
python src/cli.py ingest data/test_news_v2

# Query current knowledge
python src/cli.py query "What is AI?"

# Historical query
python src/cli.py query "What is AI?" --as-of 2024-01-15
```

**Expected CDC Output**:
```
============================================================
CDC INGESTION SUMMARY
============================================================
Documents processed: 5
Total chunks added: 2      ← CDC detected changes!
Total chunks deleted: 2
Total chunks unchanged: 8
============================================================
```

---

## Architecture

LiveVectorLake implements a **dual-tier temporal RAG system** with automatic change detection:

```
┌─────────────────────────────────────────────────────────┐
│                    LIVEVECTORLAKE                       │
│          Streaming Temporal RAG System                  │
└─────────────────────────────────────────────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ INGEST   │      │ STORAGE  │      │  QUERY   │
│  LAYER   │      │  LAYER   │      │  LAYER   │
│          │      │ (Hot+Cold)│      │          │
│ CDC-based│      │ Dual-Tier│      │ Temporal │
└──────────┘      └──────────┘      └──────────┘
```

**Core Components**:
1. **CDC Chunker** ([chunker.py](src/cdc/chunker.py)) - Hash-based change detection with SHA-256
2. **Hash Store** ([hash_store.py](src/cdc/hash_store.py)) - In-memory cache with JSON persistence
3. **Hot Tier** ([milvus_db.py](src/vectordb/milvus_db.py)) - Milvus for active chunks, <100ms queries
4. **Cold Tier** ([delta_store.py](src/lakehouse/delta_store.py)) - Delta Lake for complete history, <2s queries
5. **Embedding Engine** - SentenceTransformers (all-MiniLM-L6-v2, 384-dim, ~12 chunks/sec)
6. **Query Router** ([query_engine.py](src/query_engine.py)) - Intelligent hot/cold path selection

**[View Detailed Architecture & Diagrams →](docs/ARCHITECTURE.md)**

---

## Performance

### Core Innovation Metrics

| Metric | Standard RAG | LiveVectorLake | Improvement |
|--------|--------------|----------------|-------------|
| Update Latency | 344s (full re-index) | <2s (CDC) | **287x faster** |
| Re-processing | 100% of chunks | ~10% of chunks | **90% savings** |
| Temporal Queries | Not supported | 100% accuracy | **New capability** |
| Audit Trail | No | Complete (ACID) | **New capability** |

### System Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| CDC Detection | 99% | 100% | Pass |
| Hot Tier Query | <100ms | 17.7ms (p50) | Pass |
| Cold Tier Query | <2s | 437ms (p50) | Pass |
| Temporal Accuracy | 100% | 100% | Pass |
| Storage Compression | >3x | 1.8x | Below target |

---

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - Detailed system design, diagrams, and data flows
- **[Benchmarking Guide](tests/BENCHMARKS_README.md)** - How to run and interpret benchmarks
- **[Problem Statement](docs/Problem_statement.md)** - Research problems addressed
- **[Project Document](docs/Project.md)** - Complete research proposal
- **[Roadmap](docs/roadmap.md)** - Implementation phases and status

---

## Project Structure

```
LiveVectorLake/
├── src/
│   ├── cdc/                # Change detection components
│   ├── vectordb/           # Milvus integration
│   ├── lakehouse/          # Delta Lake storage
│   ├── pipeline/           # CDC ingestion pipeline
│   └── query_engine.py     # Query router
├── tests/
│   ├── benchmark_suite.py  # Comprehensive benchmarks
│   └── baselines/          # Baseline comparisons
├── docs/                   # Detailed documentation
└── data/                   # Test datasets
```

---

## Testing & Benchmarks

### Run Benchmarks

```bash
# Generate benchmark corpus
python tests/generate_versioned_corpus.py

# Run complete benchmark suite
python tests/benchmark_suite.py
```

### Validation Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Initial ingestion | 10 added | 10 added | Pass |
| Re-ingest same | 0 added, 10 unchanged | 0 added, 10 unchanged | Pass |
| Modified data | 2 added, 2 deleted, 8 unchanged | 2 added, 2 deleted, 8 unchanged | Pass |
| Current query | <100ms | <100ms, 3 results | Pass |
| Historical query | <2s | <2s, 5 results | Pass |

**CDC Detection Accuracy**: 100%  
**Query Engine Tests**: 4/4 passing

---

## CLI Commands

```bash
# Ingest documents
python src/cli.py ingest <path> [--reset]

# Query current knowledge
python src/cli.py query "<text>" [--top-k N]

# Historical query
python src/cli.py query "<text>" --as-of YYYY-MM-DD

# Audit document history (planned)
python src/cli.py audit <doc_id>
```

---

## Troubleshooting

**Milvus Connection Error**:
```bash
docker ps | grep milvus
docker-compose restart
```

**Hash Store Not Persisting**:
- Check file permissions for `cdc_hash_store.json`

**Embedding Slow**:
- First run downloads model (~80MB)
- Subsequent runs use cached model

---

## Future Work

- **Temporal Embeddings**: 385-dim vectors (384 semantic + 1 temporal)
- **Scalability**: Distributed deployment for petabyte-scale corpora
- **Multi-Source Integration**: Wikipedia, Stack Overflow, news feeds
- **Performance Optimization**: Storage compression, batch operations

---

## License

This project is licensed under the MIT License.

---

## Citation

If you use LiveVectorLake in your research, please cite:

```bibtex
@software{livevectorlake2025,
  title={LiveVectorLake: A LIVE Knowledge Base with CDC and Temporal Queries},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/LiveVectorLake}
}
```
