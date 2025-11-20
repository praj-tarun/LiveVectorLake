"""
Pipeline Service - Handles CDC ingestion from stream
Processes documents through LiveVectorLake pipeline
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.cdc_pipeline import CDCPipeline

class PipelineService:
    def __init__(self):
        self.pipeline = CDCPipeline()
        self.temp_dir = Path("data/temp_stream")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            "total_docs": 0,
            "total_added": 0,
            "total_unchanged": 0,
            "total_deleted": 0
        }
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure Milvus collection is created and ready"""
        if not self._initialized:
            try:
                from vectordb.milvus_db import MilvusDB
                from pymilvus import utility
                
                milvus = MilvusDB()
                milvus.connect()
                
                # Create collection if it doesn't exist
                if not utility.has_collection("doc_chunks"):
                    print("Creating Milvus collection...")
                    milvus.create_collection()
                    print("✓ Collection created and loaded")
                else:
                    # Load existing collection
                    from pymilvus import Collection
                    collection = Collection("doc_chunks")
                    collection.load()
                    print("✓ Collection loaded")
                
                self._initialized = True
            except Exception as e:
                print(f"Error initializing Milvus: {e}")
                raise
    
    async def process_document(self, doc: dict) -> dict:
        """Process a single document through CDC pipeline"""
        # Ensure Milvus is initialized before first document
        if not self._initialized:
            await asyncio.to_thread(self._ensure_initialized)
        
        doc_id = doc["doc_id"]
        content = doc["content"]
        
        # Save to temp file
        temp_file = self.temp_dir / f"{doc_id}.txt"
        temp_file.write_text(content)
        
        try:
            # Run CDC ingestion
            result = await asyncio.to_thread(
                self.pipeline.ingest_directory,
                str(self.temp_dir),
                reset=False
            )
            
            # Update stats
            self.stats["total_docs"] += result["documents_processed"]
            self.stats["total_added"] += result["chunks_added"]
            self.stats["total_unchanged"] += result["chunks_unchanged"]
            self.stats["total_deleted"] += result["chunks_deleted"]
            
            # Cleanup
            temp_file.unlink()
            
            return {
                "doc_id": doc_id,
                "chunks_added": result["chunks_added"],
                "chunks_unchanged": result["chunks_unchanged"],
                "chunks_deleted": result["chunks_deleted"],
                "success": True
            }
        
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"Pipeline error for {doc_id}: {error_msg}")
            traceback.print_exc()
            return {
                "doc_id": doc_id,
                "error": error_msg,
                "success": False
            }
    
    def get_stats(self) -> dict:
        """Get pipeline statistics"""
        total = self.stats["total_added"] + self.stats["total_unchanged"]
        efficiency = (self.stats["total_unchanged"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "efficiency": round(efficiency, 1)
        }

# Global instance
pipeline_service = PipelineService()
