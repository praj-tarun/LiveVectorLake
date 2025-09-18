# LiveVectorLake 🚀

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
LiveVectorLake is an end-to-end Retrieval-Augmented Generation (RAG) system designed for research and production use. The project aims to create a scalable, versioned, and auditable knowledge base that supports hybrid hot/cold retrieval, change data capture (CDC), dual-date reasoning, and temporal querying.

## 🎯 Features
- ✅ **Working RAG Pipeline**: Complete end-to-end implementation
- 🔍 **Semantic Search**: Vector-based similarity search using SentenceTransformers
- 🗄️ **Vector Database**: Qdrant integration for efficient vector storage
- 🤖 **LLM Integration**: Ollama support for local inference
- 📊 **Jupyter Notebooks**: Interactive experiments and demos
- 🔄 **CDC Ready**: Architecture prepared for change data capture

## Project Structure
The project is organized into several key directories and files:

- **data/**: Contains example raw documents and future CDC event files.
- **docs/**: Project documentation, including roadmap, design documents, and research paper summaries.
- **notebooks/**: Jupyter notebooks for experiments and quick local demos.
- **src/**: The source code for the RAG system, organized into modules for chunking, embedding, vector database operations, retrieval, generation, and more.
- **tests/**: Unit and integration tests to ensure the functionality of the system.
- **examples/**: Example scripts demonstrating the basic RAG flow.
- **requirements.txt**: Lists the dependencies required for the project.

## Core Components
1. **Chunking**: The `chunking` module handles the segmentation of text documents into smaller, manageable chunks.
2. **Embedding**: The `embedding` module converts text chunks into vector representations for storage and retrieval.
3. **Vector Database**: The `vectordb` module implements CRUD operations for managing vectors and their associated metadata.
4. **Retrieval**: The `retrieval` module retrieves the top-k similar vectors from the vector database.
5. **Generation**: The `generation` module wraps the Ollama LLM for generating answers based on retrieved information.
6. **Change Data Capture (CDC)**: The `cdc` module is stubbed for future development of CDC event handling.
7. **Temporal Logic**: The `temporal` module is planned for future dual-date/time handling.
8. **API**: The `api` module sets up a FastAPI application for demo purposes.

## Getting Started
To set up the project locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/livevectorlake.git
   cd livevectorlake
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the example quickstart script to see the basic RAG flow in action:
   ```
   python examples/quickstart.py
   ```

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## Future Scope
The project aims to evolve into a fully operational, CDC-aware, versioned RAG stack for live knowledge bases. Future enhancements will include:
- Implementing true change data capture.
- Supporting hybrid retrieval strategies.
- Adding dual-date logic for time-sensitive queries.
- Benchmarking and exploring compliance/audit use cases.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.