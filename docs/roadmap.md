# LiveVectorLake Research Prototype: Implementation Roadmap

## 1. Core Milestones (What to Build and Why)

### A. Data Stream Ingestion & Change Detection (COMPLETE)
Goal: Ingest high-velocity, evolving text streams with fine-grained, hash-based change detection (CDC).

Features:
- Data connectors for streaming sources (text files, simulated streaming)
- Chunker that splits documents into paragraphs
- Hash each chunk's content (SHA-256)
- In-memory hash store with JSON persistence for fast comparison
- Label chunks as "insert" (new), "inactivate" (superseded), "active"

Status: Complete - 100% CDC detection accuracy

### B. Embedding and Vector Indexing (COMPLETE)
Goal: Support semantic search for current knowledge and retroactive (temporal) retrieval.

Features:
- SentenceTransformers (all-MiniLM-L6-v2) for chunk embedding
- Milvus Vector DB (dockerized, local): store only "active" chunk vectors
- Collection schema: chunk_id, vector, status, doc_id, valid_from, valid_to
- HNSW index for fast similarity search
- Adding/removing vectors in sync with CDC labeling

Status: Complete - <100ms query latency achieved

### C. Historical Storage and Versioned Metadata (COMPLETE)
Goal: Enable point-in-time (temporal) queries and audit trail.

Features:
- Delta Lake table (local disk): store all chunk records
- Update Delta with new/modified/inactivated chunks on each ingest
- Time-travel with Delta for "as of" queries
- ACID guarantees for all operations

Status: Complete - <2s historical queries

### D. Query Engine (COMPLETE)
Goal: Dual-mode retrieval for current and historical questions.

Features:
- Current query: User input → embed → vector search in Milvus (status=active)
- Historical/"as-of" query: Delta Lake filtering + vector similarity
- Query router for hot/cold path selection
- CLI interface with ingest and query commands

Status: Complete - 4/4 tests passing

### E. Web Interface (IN PROGRESS)
Goal: Visual interface for document upload, queries, and CDC visualization.

Features:
- Streamlit-based web UI
- Document upload and ingestion interface
- Query interface (current + historical)
- CDC visualization (what changed, when)
- Version timeline view
- Results display with source attribution

Status: In progress - 2 days remaining

## 2. Sprint-by-Sprint Progress

### Week 1: CDC Foundation + Embedding (COMPLETE)
Implemented:
- Text loader, chunker, SHA-256 hashing
- CDC: compare incoming hashes with stored list (active/inactive labeling)
- Delta Lake schema for chunk storage (chunk_id, text, doc_id, valid_from, valid_to, status)
- SentenceTransformers embedding (all-MiniLM-L6-v2, 384-dim)
- Dockerized Milvus, Python connection + vector insert/delete
- In-memory hash store with JSON persistence

Tested:
- Ingested 10 chunks; verified hash-based CDC triggers correct updates/inactivations
- CLI ingest command with CDC summary
- 100% CDC detection accuracy

### Week 2: Dual-Tier Storage & Query (COMPLETE)
Implemented:
- Query engine for current vector search (Milvus; status=active)
- Historical/time-travel queries: Delta Lake filtering + vector similarity
- Query router (hot/cold path selection)
- CLI query command with --as-of and --top-k flags
- Result formatting with metadata and provenance

Tested:
- Current queries return latest (active) chunk matches (<100ms)
- As-of queries return version-specific matches (<2s)
- Comprehensive test suite (4/4 tests passing)
- Query routing logic validated

### Week 3: Web UI + Multi-Source Streaming (IN PROGRESS)

Web UI (2 days, in progress):
- Streamlit-based interface
- Document upload and ingestion
- Query interface (current + historical)
- CDC visualization
- Version timeline view

Multi-Source Streaming (remaining):
- Second data source (Wikipedia edit stream, Stack Overflow, or additional news feed)
- Multi-source conflict logic: detect contradictory information
- Simulate data arrival from multiple sources in parallel

Test:
- Ingest/track conflict scenarios, generate metrics
- CLI command for conflict audit

### Week 4: Benchmarking, Audit & Documentation (PLANNED)

Benchmark:
- Ingest-to-query latency (target: <100ms for current, <2s for historical)
- Accuracy: time-travel "as of" queries return correct version
- Throughput: 10K+ ingests/updates/day (simulate via batch)

Audit:
- CLI/notebook: for a random chunk/doc, show all historical versions
- Conflict dashboard: time series of conflict events, resolutions

Deliverables:
- Final CLI tool with commands for ingest, query, audit
- Notebook walkthrough with sample data: CDC, query, audit
- Diagrams: architecture, dataflow, chunk lifecycle
- README with install instructions and research contributions

## 3. Prototype Evaluation Grid

| Module | Technology | Measured By | Target | Status |
|--------|-----------|-------------|--------|--------|
| CDC & chunker | Python | #new, #changed, #inactivated | 99% correct | 100% |
| Embedding | sent-transformers | Coverage, speed | <1s/1000 chunks | Pass |
| Vector index | Milvus/HNSW | Query latency | <100ms | <100ms |
| Cold store | Delta Lake | Time-travel retrieval | <5s/10K rows | <2s |
| Query engine | CLI | Accuracy/latency | <1s current | <100ms |
| Audit trail | Logs/Delta | Completeness | 100% ops tracked | Pass |
| Conflict detect | Python | Conflicts found/logged | 100% of injected | Pending |

## 4. Reference Data for Experiments

Download:
- 1-2 months of RSS/NewsAPI feeds (to .txt or .json)
- Wikipedia edit history dumps (filtered Top 100 articles)
- Stack Overflow question dumps (optional)
- Optionally, use a script to generate artificial high-velocity streams

## 5. Remaining Tasks

### Immediate (Week 3):
- Streamlit web UI (2 days)
- Wikipedia connector (1.5 days)
- Stack Overflow connector (1 day)
- Conflict detection (1.5 days)

### Week 4:
- Performance benchmarks (2 days)
- Baseline comparisons (2 days)
- Accuracy validation (1 day)
- Documentation polish (1 day)

This roadmap demonstrates the scientific, technical, and experimental aims of LiveVectorLake as a streaming, temporally-versioned, real-time RAG system.
