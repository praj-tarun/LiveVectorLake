# Contributing to LiveVectorLake

Thank you for your interest in contributing to LiveVectorLake! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Setup Development Environment

```bash
# Fork and clone
git clone https://github.com/yourusername/LiveVectorLake.git
cd LiveVectorLake

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up -d
```

## 📋 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow existing code style
- Add docstrings to functions
- Keep functions small and focused

### 3. Test Your Changes

```bash
# Generate test data
python tests/generate_test_data.py

# Test ingestion
python src/cli.py ingest data/test_news --reset
python src/cli.py ingest data/test_news_v2

# Test Delta Lake
python tests/test_delta_lake.py
```

### 4. Commit

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Format**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 🎯 Areas for Contribution

### Phase 2 (Query Engine)
- [ ] Current query implementation
- [ ] Historical query with time-travel
- [ ] Query CLI commands

### Phase 3 (Multi-Source)
- [ ] Wikipedia stream connector
- [ ] Conflict detection logic
- [ ] Multi-source reconciliation

### Phase 4 (Benchmarking)
- [ ] Performance tests
- [ ] Accuracy validation
- [ ] Documentation improvements

### General
- [ ] Bug fixes
- [ ] Documentation improvements
- [ ] Test coverage
- [ ] Performance optimizations

## 📝 Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep lines under 100 characters

**Example**:
```python
def process_chunk(chunk: str, doc_id: str) -> Dict[str, Any]:
    """Process a text chunk with CDC detection.
    
    Args:
        chunk: Text content to process
        doc_id: Document identifier
    
    Returns:
        Dictionary with chunk metadata
    """
    # Implementation
    pass
```

## 🧪 Testing Guidelines

### Test Structure

```python
def test_cdc_detection():
    """Test CDC detects changes correctly"""
    # Arrange
    initial_chunks = ["chunk1", "chunk2"]
    modified_chunks = ["chunk1", "chunk3"]
    
    # Act
    result = compare_chunks(modified_chunks, set(initial_chunks))
    
    # Assert
    assert len(result['added']) == 1
    assert len(result['deleted']) == 1
```

### Running Tests

```bash
# Run all tests (future)
pytest

# Run specific test
pytest tests/test_cdc.py
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Provide usage examples

### README Updates

- Update README.md for new features
- Add examples for new CLI commands
- Update architecture diagrams if needed

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try latest version
3. Reproduce with minimal example

### Report Format

```markdown
**Description**: Brief description

**Steps to Reproduce**:
1. Step 1
2. Step 2

**Expected**: What should happen

**Actual**: What actually happens

**Environment**:
- OS: Windows/Linux/Mac
- Python: 3.12
- Docker: 20.10
```

## 💡 Feature Requests

### Request Format

```markdown
**Feature**: Brief description

**Use Case**: Why is this needed?

**Proposed Solution**: How should it work?

**Alternatives**: Other approaches considered
```

## 🔍 Code Review Process

### What We Look For

- ✅ Code follows style guidelines
- ✅ Tests pass
- ✅ Documentation updated
- ✅ No breaking changes (or documented)
- ✅ Commit messages clear

### Review Timeline

- Initial review: 2-3 days
- Follow-up: 1-2 days
- Merge: After approval

## 📞 Getting Help

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: your.email@example.com

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in research papers (if applicable)

---

Thank you for contributing to LiveVectorLake! 🚀
