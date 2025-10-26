# LiveVectorLake Architecture

## Overview

LiveVectorLake implements a **dual-tier temporal RAG system** with automatic change detection (CDC) and complete version history.

---

## System Architecture

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
└──────────┘      └──────────┘      └──────────┘
```

---

## Component Architecture

### 1. Ingestion Layer

```
┌─────────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE                    │
└─────────────────────────────────────────────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│  LOADER  │      │   CDC    │      │ EMBEDDING│
│          │      │ CHUNKER  │      │          │
└──────────┘      └──────────┘      └──────────┘
```

**Components**:
- **Text Loader** (`src/sources/text_loader.py`)
  - Loads documents from files
  - Simulates streaming data
  - Returns: `{doc_id, content, timestamp}`

- **CDC Chunker** (`src/cdc/chunker.py`)
  - Splits text into semantic chunks (paragraphs)
  - Generates SHA-256 hash for each chunk
  - Compares with stored hashes
  - Returns: `{added, deleted, unchanged}`

- **Hash Store** (`src/cdc/hash_store.py`)
  - In-memory cache of chunk hashes
  - Persisted to `cdc_hash_store.json`
  - O(1) lookup for CDC comparison

- **Embedding Service**
  - Model: SentenceTransformers (all-MiniLM-L6-v2)
  - Dimension: 384
  - Speed: ~12 chunks/sec (CPU)
  - Embeds only changed chunks (efficient)

---

### 2. Storage Layer (Dual-Tier)

```
┌─────────────────────────────────────────────────────────┐
│                   STORAGE ARCHITECTURE                  │
└─────────────────────────────────────────────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│   HOT    │      │   COLD   │      │   HASH   │
│  MILVUS  │      │  DELTA   │      │  STORE   │
└──────────┘      └──────────┘      └──────────┘
```

#### Hot Tier: Milvus (`src/vectordb/milvus_db.py`)

**Purpose**: Fast vector search on active chunks

**Schema**:
```python
{
    'chunk_id': str,      # SHA-256 hash
    'vector': List[float], # 384-dim embedding
    'status': str,        # 'active' only
    'doc_id': str,        # Source document
    'valid_from': int,    # Unix timestamp
    'valid_to': int       # 0 (active)
}
```

**Features**:
- HNSW index for <100ms queries
- Stores only active chunks
- Automatic filtering by status
- Temporal fields for future queries

**Performance**:
- Insert: <100ms
- Search: <100ms (p95)
- Index: HNSW (M=16, efConstruction=200)

#### Cold Tier: Delta Lake (`src/lakehouse/delta_store.py`)

**Purpose**: Complete version history with ACID

**Technology**:
- Format: Delta Lake (Rust-based)
- Library: Polars (2-10x faster than Pandas)
- Storage: Parquet (columnar, compressed)
- Transactions: ACID with transaction log

**Schema**:
```python
{
    'chunk_id': str,           # SHA-256 hash
    'content_text': str,       # Raw text
    'content_vector': List[float], # 384-dim embedding
    'doc_id': str,             # Source document
    'valid_from': int,         # Unix timestamp
    'valid_to': int,           # 0 = active, else superseded
    'status': str,             # active/superseded/deleted
    'version_number': int      # Version sequence
}
```

**Features**:
- Stores ALL chunks (active + superseded + deleted)
- Time-travel queries
- Similarity search on historical data
- ACID guarantees
- 3-5x compression (Parquet)

**Performance**:
- Write: <200ms
- Read all: <500ms
- Time-travel query: <1s
- Similarity search: <2s

**Storage Structure**:
```
lakehouse/
└── chunks/
    ├── _delta_log/
    │   ├── 00000000000000000000.json  # Transaction log
    │   └── 00000000000000000001.json
    ├── part-00000-xxx.snappy.parquet  # Data files
    └── part-00001-xxx.snappy.parquet
```

#### Hash Store (`src/cdc/hash_store.py`)

**Purpose**: Fast CDC comparison

**Storage**: `cdc_hash_store.json`

**Structure**:
```json
{
  "article_001": ["hash1", "hash2", ...],
  "article_002": ["hash3", "hash4", ...]
}
```

**Operations**:
- Load: O(1)
- Lookup: O(1)
- Update: O(1)
- Persist: <10ms

---

### 3. Query Layer (Phase 2 - Planned)

```
┌─────────────────────────────────────────────────────────┐
│                    QUERY ARCHITECTURE                   │
└─────────────────────────────────────────────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│  PARSER  │      │  ROUTER  │      │ RETRIEVER│
│          │      │          │      │          │
└──────────┘      └──────────┘      └──────────┘
```

**Components** (Planned):
- **Query Parser**: Extract temporal intent
- **Query Router**: Route to hot/cold tier
- **Current Retriever**: Milvus vector search
- **Historical Retriever**: Delta Lake time-travel
- **Comparative Retriever**: Timeline of changes

---

## Data Flow

### Ingestion Flow

```
1. Load Document
   ↓
2. Chunk Text (paragraphs)
   ↓
3. Hash Chunks (SHA-256)
   ↓
4. Compare with Hash Store (CDC)
   ↓
5. Embed Changed Chunks
   ↓
6. Write to Milvus (hot tier - active only)
   ↓
7. Write to Delta Lake (cold tier - all chunks)
   ↓
8. Update Hash Store
   ↓
9. Return CDC Summary
```

### Query Flow (Current - Phase 1)

**Time-Travel Query**:
```
1. Query: "What was X on date Y?"
   ↓
2. Load chunks from Delta Lake
   ↓
3. Filter: valid_from <= Y < valid_to
   ↓
4. Embed query
   ↓
5. Compute similarity (cosine)
   ↓
6. Return top-k results
```

### Query Flow (Planned - Phase 2)

**Current Query (Hot Path)**:
```
1. Query: "What is X?"
   ↓
2. Parse intent: CURRENT
   ↓
3. Route to Milvus
   ↓
4. Embed query
   ↓
5. Vector search (HNSW)
   ↓
6. Return top-k results (<100ms)
```

**Historical Query (Cold Path)**:
```
1. Query: "What was X on date Y?"
   ↓
2. Parse intent: HISTORICAL
   ↓
3. Route to Delta Lake
   ↓
4. Time-travel query
   ↓
5. Similarity search
   ↓
6. Return top-k results (<2s)
```

---

## Technology Stack

| Layer | Component | Technology | Why |
|-------|-----------|-----------|-----|
| **Ingestion** | Loader | Python | Simple, flexible |
| | Chunker | Python | Custom logic |
| | Embedding | SentenceTransformers | Fast, accurate |
| **Storage** | Hot Tier | Milvus 2.4+ | Fast vector search |
| | Cold Tier | Delta Lake (Polars) | ACID, time-travel |
| | Hash Store | JSON | Simple, fast |
| **Query** | Parser | Python (planned) | Flexible |
| | Router | Python (planned) | Custom logic |
| **Infrastructure** | Container | Docker Compose | Easy deployment |
| | Language | Python 3.13 | Modern, compatible |

---

## Design Principles

### 1. Chunk-Level Granularity
- All versioning at chunk level (not document)
- Enables fine-grained change detection
- Supports paragraph-level queries

### 2. Content-Addressable Identity
- SHA-256 hash as chunk ID
- Automatic deduplication
- No external dependency tracking

### 3. Immutable History
- All versions preserved
- Deletions are logical (status change)
- Complete audit trail

### 4. Dual-Tier Storage
- Hot tier: Performance (Milvus)
- Cold tier: History (Delta Lake)
- 10-100x cost savings

### 5. ACID Guarantees
- Transaction log in Delta Lake
- Atomic writes
- No data loss on failures

---

## Performance Characteristics

### Ingestion

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Load document | <10ms | 100 docs/sec |
| Chunk text | <5ms | 200 docs/sec |
| Hash chunk | <1ms | 1000 chunks/sec |
| CDC comparison | <10ms | 100 docs/sec |
| Embed chunk | ~80ms | 12 chunks/sec |
| Milvus insert | <100ms | 10 chunks/batch |
| Delta Lake write | <200ms | 50 chunks/batch |

### Query

| Operation | Latency | Notes |
|-----------|---------|-------|
| Milvus search (hot) | <100ms | p95, HNSW index |
| Delta Lake read | <500ms | Full scan |
| Time-travel query | <1s | Filtered scan |
| Similarity search | <2s | Load + compute |

### Storage

| Metric | Value | Notes |
|--------|-------|-------|
| Milvus size | ~1KB/chunk | Vector + metadata |
| Delta Lake size | ~500B/chunk | Parquet compressed |
| Compression ratio | 3-5x | Parquet vs JSON |
| Hot/cold cost ratio | 10-100x | Milvus vs S3 |

---

## Scalability

### Current Capacity (Single Node)

- **Documents**: 10K-100K
- **Chunks**: 100K-1M
- **Versions**: 10-100 per chunk
- **Storage**: 1-10 GB (cold tier)
- **Memory**: 4-8 GB

### Future Scaling (Distributed)

- **Milvus**: Sharding by collection
- **Delta Lake**: Partitioning by date/source
- **Embedding**: GPU acceleration
- **Ingestion**: Kafka streaming

---

## Security & Compliance

### Data Protection

- **Encryption**: At rest (storage) and in transit (TLS)
- **Access Control**: Role-based (future)
- **Audit Logging**: All operations logged

### Compliance

- **ACID**: Transaction guarantees
- **Audit Trail**: Complete version history
- **Provenance**: Source tracking
- **Immutability**: No data deletion

---

## Monitoring & Observability

### Metrics (Planned)

- Ingestion rate (chunks/sec)
- Query latency (p50, p95, p99)
- CDC detection accuracy
- Storage utilization
- Error rates

### Logging

- Structured JSON logs
- Operation tracking
- Error reporting
- Performance profiling

---

## Future Enhancements

### Phase 2: Query Engine
- Query parser with temporal intent
- Hot/cold path routing
- LLM integration for answers

### Phase 3: Multi-Source
- Wikipedia stream connector
- Conflict detection
- Source reconciliation

### Phase 4: Production
- Performance benchmarking
- Distributed deployment
- REST API
- Dashboard (Streamlit)

---

## References

- [Project Document](Project.md) - Complete research proposal
- [Roadmap](roadmap.md) - Implementation plan
- [Problem Statement](Problem_statement.md) - Research problems
- [Delta Lake Implementation](../DELTA_LAKE_IMPLEMENTATION.md) - Technical details

---

**Last Updated**: October 26, 2025  
**Version**: 1.0 (Phase 1 Complete)
