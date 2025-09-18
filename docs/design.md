# Architectural Design of the livevectorlake RAG System

## Overview
The livevectorlake project aims to create a robust Retrieval-Augmented Generation (RAG) system that can evolve from a simple prototype to a fully operational knowledge base. This document outlines the architectural design of the system, detailing its core components and their interactions.

## Core Components

### 1. Data Ingestion
- **Functionality**: The system will ingest raw text documents from the `data/` directory.
- **Chunking**: The `chunking/chunker.py` module will handle the segmentation of documents into manageable chunks for processing.

### 2. Embedding
- **Functionality**: Each chunk will be transformed into a vector representation using embedding techniques.
- **Module**: The `embedding/embedder.py` module will be responsible for this transformation, utilizing libraries such as SentenceTransformers or Ollama’s embedding APIs.

### 3. Vector Database
- **Functionality**: The system will store vectors and associated metadata in a vector database.
- **Module**: The `vectordb/db.py` module will implement CRUD operations for managing the vector data, ensuring efficient storage and retrieval.

### 4. Retrieval
- **Functionality**: The system will retrieve relevant chunks based on user queries using similarity search.
- **Module**: The `retrieval/retriever.py` module will implement top-k retrieval logic, allowing for both hot and cold data retrieval strategies.

### 5. Generation
- **Functionality**: The system will generate answers to user queries by leveraging the retrieved chunks and an LLM.
- **Module**: The `generation/rag_llm.py` module will wrap the Ollama LLM, providing methods for generating answers and assembling the RAG response.

### 6. Change Data Capture (CDC)
- **Functionality**: Future enhancements will include CDC capabilities to track changes in the data.
- **Module**: The `cdc/cdc_sim.py` module is stubbed for future development, allowing for the simulation of CDC events.

### 7. Temporal Logic
- **Functionality**: The system will support dual-date reasoning for time-sensitive queries.
- **Module**: The `temporal/date_utils.py` module is planned for future implementation of date handling logic.

### 8. API Layer
- **Functionality**: An optional API layer will be provided for external interactions with the RAG system.
- **Module**: The `api/app.py` module will set up a FastAPI application for demo purposes.

## Metadata Management
All chunks and vectors will carry metadata, including:
- Content
- Ingest date
- Source
- Chunk ID

This metadata will facilitate future enhancements related to versioning and temporal queries.

## Future Enhancements
- Implement true change data capture to enable versioned fact storage and auditability.
- Support hybrid retrieval strategies, optimizing for both performance and cost.
- Develop dual-date logic for handling time-sensitive information in queries.

## Conclusion
The architectural design of the livevectorlake project is structured to support modular development and future scalability. Each component is designed with clear responsibilities, ensuring that the system can evolve from a basic RAG prototype to a comprehensive, enterprise-ready knowledge base.