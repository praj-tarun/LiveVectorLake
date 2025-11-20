"""
CDC Pipeline wrapper for UI integration
"""
from pathlib import Path
from typing import Dict
from .cdc_ingest_simple import CDCIngestionPipeline

class CDCPipeline:
    """Simplified CDC pipeline for UI"""
    
    def __init__(self):
        self.pipeline = None
    
    def ingest_directory(self, directory_path: str, reset: bool = False) -> Dict:
        """Ingest all documents from a directory"""
        # Initialize pipeline
        self.pipeline = CDCIngestionPipeline(reset_milvus=reset)
        
        # Find all text files
        dir_path = Path(directory_path)
        txt_files = list(dir_path.glob("*.txt"))
        
        if not txt_files:
            return {
                'documents_processed': 0,
                'chunks_added': 0,
                'chunks_deleted': 0,
                'chunks_unchanged': 0
            }
        
        # Process each document
        total_added = 0
        total_deleted = 0
        total_unchanged = 0
        
        for txt_file in txt_files:
            doc_id = txt_file.stem
            content = txt_file.read_text(encoding='utf-8')
            
            result = self.pipeline.ingest_document(doc_id, content)
            
            total_added += result['added']
            total_deleted += result['deleted']
            total_unchanged += result['unchanged']
        
        return {
            'documents_processed': len(txt_files),
            'chunks_added': total_added,
            'chunks_deleted': total_deleted,
            'chunks_unchanged': total_unchanged,
            'details': {
                'directory': directory_path,
                'files_processed': [f.name for f in txt_files]
            }
        }
