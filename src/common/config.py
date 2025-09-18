class Config:
    """
    Central configuration settings for the livevectorlake project.

    This class holds configuration parameters for database connections,
    model parameters, and other settings that may be used throughout the project.
    """

    def __init__(self):
        # Database configuration
        self.vector_db_url = "http://localhost:6333"  # URL for the vector database
        self.vector_db_name = "livevectorlake"         # Name of the vector database

        # Model parameters
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"  # Default embedding model
        self.llm_model = "ollama/llama3"  # Default LLM model

        # Metadata settings
        self.metadata_fields = ["content", "ingest_date", "source", "chunk_id"]  # Fields to include in metadata

    def get_vector_db_config(self):
        """
        Returns the vector database configuration as a dictionary.
        """
        return {
            "url": self.vector_db_url,
            "name": self.vector_db_name
        }

    def get_model_config(self):
        """
        Returns the model configuration as a dictionary.
        """
        return {
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model
        }

    def get_metadata_fields(self):
        """
        Returns the list of metadata fields.
        """
        return self.metadata_fields

    # TODO: Add additional configuration options as needed for future features.