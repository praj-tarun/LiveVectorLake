import logging
from typing import List, Optional
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType, Collection,
    utility
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("milvus_utils")

def connect(host: str = "localhost", port: str = "19530"):
    """
    Connect to Milvus server. Returns True on success, or raises/returns None on failure.
    """
    try:
        connections.connect(alias="default", host=host, port=port)
        logger.info("Connected to Milvus at %s:%s", host, port)
        return True
    except Exception as e:
        logger.exception("Failed to connect to Milvus: %s", e)
        return None

def ensure_collection(client_alias_or_flag, name: str, dim: int):
    """
    Ensure collection with float vector field exists. Uses auto_id primary key.
    """
    try:
        # check collection existence via utility
        if utility.has_collection(name):
            logger.debug("Collection %s already exists", name)
            return Collection(name)
        # build schema: auto-id primary key + vector field
        id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        vector_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
        schema = CollectionSchema(fields=[id_field, vector_field], description="LiveVectorLake chunks")
        coll = Collection(name=name, schema=schema)
        # create an index for vector searches
        index_params = {"index_type": "HNSW", "metric_type": "COSINE", "params": {"M": 16, "efConstruction": 128}}
        coll.create_index(field_name="embedding", index_params=index_params)
        coll.load()
        logger.info("Created and loaded collection %s (dim=%d)", name, dim)
        return coll
    except Exception as e:
        logger.exception("Failed to ensure/create collection %s: %s", name, e)
        raise

def insert_embeddings(client_alias_or_flag, collection_name: str, embeddings: List[List[float]], meta_chunks: Optional[List[dict]] = None) -> List[int]:
    """
    Insert embeddings into collection. Returns generated ids.
    meta_chunks is optional; we do not store metadata in Milvus for now.
    """
    try:
        coll = Collection(collection_name)
        # For auto_id primary key, insert only embedding field values as a list-of-lists
        mr = coll.insert([embeddings])
        # flush to persist
        coll.flush()
        # mr.primary_keys contains assigned ids
        ids = mr.primary_keys if hasattr(mr, "primary_keys") else []
        logger.info("Inserted %d vectors into %s", len(embeddings), collection_name)
        return ids
    except Exception as e:
        logger.exception("Failed to insert embeddings into %s: %s", collection_name, e)
        raise

def search(collection_name: str, query_vector: List[float], top_k: int = 5):
    """
    Search collection and return list of (id, distance) tuples.
    """
    try:
        coll = Collection(collection_name)
        results = coll.search([query_vector], "embedding", param={"metric_type": "COSINE", "params": {"ef": 64}}, limit=top_k)
        out = []
        for hit in results[0]:
            out.append((hit.id, hit.distance))
        return out
    except Exception as e:
        logger.exception("Search failed on %s: %s", collection_name, e)
        raise
