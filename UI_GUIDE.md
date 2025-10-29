# LiveVectorLake Web UI Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit>=1.28.0
```

### 2. Start Milvus

```bash
docker-compose up -d
```

### 3. Run the Web UI

```bash
streamlit run src/app.py
```

The UI will open in your browser at `http://localhost:8501`

## Features

### Query Page

**Current Query:**
- Search active chunks in Milvus hot tier
- Fast retrieval (<100ms)
- Returns most recent knowledge

**Historical Query:**
- Search Delta Lake cold tier at specific date
- Time-travel to past versions
- See what knowledge existed on that date

### Ingest Page

**Upload Documents:**
- Upload .txt files
- Automatic CDC detection
- See what changed (added/modified/unchanged)

**Reset Option:**
- Clear all existing data
- Fresh start for testing

### CDC History Page

**View Ingestion History:**
- See all uploaded documents
- CDC summary for each ingestion
- Status indicators (new/modified/unchanged)

## Usage Examples

### Example 1: Initial Ingestion

1. Go to "Ingest" page
2. Check "Reset collection"
3. Upload `data/test_news/article_001.txt`
4. Click "Ingest"
5. See CDC summary: All chunks marked as "Added"

### Example 2: Detect Changes

1. Modify article_001.txt (change a paragraph)
2. Upload modified file
3. See CDC summary: Some chunks "Modified", others "Unchanged"

### Example 3: Current Query

1. Go to "Query" page
2. Select "Current"
3. Enter query: "What is machine learning?"
4. Click "Search"
5. See results from Milvus hot tier

### Example 4: Historical Query

1. Go to "Query" page
2. Select "Historical"
3. Pick a past date
4. Enter query: "What is AI?"
5. See results as they existed on that date

## Troubleshooting

### UI won't start

```bash
# Check streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install streamlit>=1.28.0
```

### No results from queries

```bash
# Check Milvus is running
docker ps | grep milvus

# Ingest some data first
# Go to Ingest page and upload documents
```

### Import errors

```bash
# Make sure you're in project root
cd LiveVectorLake

# Run from project root
streamlit run src/app.py
```

## Next Steps

After testing the UI:
1. Try ingesting multiple documents
2. Test CDC detection with modified files
3. Compare current vs historical queries
4. Check CDC history to see all changes
