# Tests

This directory contains test scripts and utilities for LiveVectorLake.

## Test Scripts

### generate_test_data.py
Generates sample test data for CDC testing:
- `data/test_news/` - 5 initial articles
- `data/test_news_v2/` - Same articles with 2 modifications

**Usage:**
```bash
python tests/generate_test_data.py
```

### test_delta_lake.py
Tests Delta Lake integration and historical queries:
- Verifies data storage in Delta Lake
- Tests time-travel queries
- Tests similarity search on historical data

**Usage:**
```bash
python tests/test_delta_lake.py
```

## Running Tests

```bash
# Generate test data
python tests/generate_test_data.py

# Test ingestion
python src/cli.py ingest data/test_news --reset

# Test CDC detection
python src/cli.py ingest data/test_news_v2

# Test Delta Lake
python tests/test_delta_lake.py
```

## Test Data

Test data is stored in `data/` directory:
- `data/test_news/` - Initial version of 5 news articles
- `data/test_news_v2/` - Modified version with 2 changed articles
