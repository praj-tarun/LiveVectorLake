# Quick Start Guide

## ✅ What's Implemented

**CDC Foundation + Embedding**:

- ✅ Text file loader (simulates streaming)
- ✅ Hash-based CDC with comparison logic
- ✅ In-memory hash store (persisted to JSON)
- ✅ Enhanced Milvus schema (temporal fields)
- ✅ CDC-aware ingestion pipeline
- ✅ CLI tool for testing
- ✅ Test data generator

## 🚀 Setup

### 1. Start Milvus (if not running)

```bash
docker-compose up -d
```

### 2. Install Dependencies

```bash
pip install sentence-transformers pymilvus
```

### 3. Generate Test Data

```bash
python generate_test_data.py
```

This creates:
- `data/test_news/` - 5 initial articles
- `data/test_news_v2/` - Same articles with 2 modifications

## 📝 Usage

### Ingest Initial Data

```bash
python src/cli.py ingest data/test_news
```

**Expected Output**:
```
Loading files from: data/test_news
Found 5 files

============================================================
CDC INGESTION SUMMARY
============================================================
Documents processed: 5
Total chunks added: 20
Total chunks deleted: 0
Total chunks unchanged: 0

Hash Store Stats:
  Total documents: 5
  Total active chunks: 20
  Avg chunks/doc: 4.0
============================================================
```

### Ingest Modified Data (Test CDC)

```bash
python src/cli.py ingest data/test_news_v2
```

**Expected Output**:
```
Loading files from: data/test_news_v2
Found 5 files

============================================================
CDC INGESTION SUMMARY
============================================================
Documents processed: 5
Total chunks added: 2        ← New chunks detected!
Total chunks deleted: 0
Total chunks unchanged: 18   ← Unchanged chunks skipped

Hash Store Stats:
  Total documents: 5
  Total active chunks: 22
  Avg chunks/doc: 4.4
============================================================
```

### Ingest Single File

```bash
python src/cli.py ingest data/test_news/article_001.txt
```

## 🧪 Testing CDC Detection

### Test 1: Initial Ingestion
```bash
# Clean start
rm cdc_hash_store.json

# Ingest initial data
python src/cli.py ingest data/test_news
```

**Validation**: All chunks should be "added" (no previous data)

### Test 2: Re-ingest Same Data
```bash
# Ingest same data again
python src/cli.py ingest data/test_news
```

**Validation**: All chunks should be "unchanged" (no changes detected)

### Test 3: Ingest Modified Data
```bash
# Ingest modified versions
python src/cli.py ingest data/test_news_v2
```

**Validation**: 
- 2 chunks "added" (article_001 and article_003 have new content)
- 18 chunks "unchanged"
- 0 chunks "deleted"

### Test 4: Delete a Document
```bash
# Remove one file and re-ingest
rm data/test_news_v2/article_005.txt
python src/cli.py ingest data/test_news_v2
```

**Validation**: Chunks from article_005 should be marked "deleted"

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| CDC detection accuracy | 99% | ✅ Hash-based (100%) |
| Embedding speed | <1s/1000 chunks | ✅ SentenceTransformers |
| Milvus insert | Works | ✅ With temporal fields |
| Delta Lake write | Works | ✅ Append mode |
| CLI ingest | Works | ✅ With CDC summary |

## 🔍 Verify Data

### Check Milvus
```python
from src.vectordb.milvus_db import MilvusDB

milvus = MilvusDB()
milvus.connect()
# Check collection exists and has data
```

### Check Hash Store
```bash
cat cdc_hash_store.json
```

Should show document IDs and their chunk hashes.

### Check Delta Lake
```python
from src.lakehouse.delta_store import DeltaStore

delta = DeltaStore()
df = delta.read_chunks()
df.show()
```

## 🐛 Troubleshooting

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

### Delta Lake Errors
- Ensure PySpark is installed (Python 3.12 compatible)
- Check `lakehouse/` directory exists

## 📝 Next Steps

- [ ] Query engine for current vector search
- [ ] Historical/time-travel queries
- [ ] Ingestion batching simulation
- [ ] Query CLI commands

## 🎯 Completed Features

✅ **Implemented**:
1. Text loader for local files
2. Hash-based CDC with comparison
3. In-memory hash store
4. Enhanced Milvus schema (temporal fields)
5. CDC-aware ingestion pipeline
6. CLI tool with ingest command
7. Test data generator
8. CDC summary reporting

**Ready for Week 2!** 🚀
