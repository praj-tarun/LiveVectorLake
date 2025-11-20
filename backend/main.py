"""
FastAPI Backend - Real-time WebSocket server
Connects stream simulator, pipeline, and query engine
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
from pathlib import Path
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import stream_service
import pipeline_service
from query_engine import QueryEngine

stream_simulator = stream_service.stream_simulator
pipeline_service = pipeline_service.pipeline_service

app = FastAPI(title="LiveVectorLake Demo")

# Global session state (persists across page reloads)
session_state = {
    "stream_running": False,
    "total_docs_processed": 0,
    "session_stats": {
        "total_docs": 0,
        "total_added": 0,
        "total_unchanged": 0,
        "total_deleted": 0
    }
}

# Initialize query engine
try:
    query_engine = QueryEngine()
    print("✓ Query engine initialized")
except Exception as e:
    print(f"✗ Query engine failed: {e}")
    query_engine = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Stream callback - processes docs and broadcasts updates
async def on_document_received(doc: dict):
    """Called when stream generates a new document"""
    # Broadcast stream event
    await manager.broadcast({
        "type": "stream",
        "data": doc
    })
    
    # Process through pipeline
    result = await pipeline_service.process_document(doc)
    
    # Update session state
    session_state["session_stats"]["total_docs"] += 1
    session_state["session_stats"]["total_added"] += result.get("chunks_added", 0)
    session_state["session_stats"]["total_unchanged"] += result.get("chunks_unchanged", 0)
    session_state["session_stats"]["total_deleted"] += result.get("chunks_deleted", 0)
    
    # Broadcast pipeline result
    await manager.broadcast({
        "type": "pipeline",
        "data": result
    })
    
    # Broadcast updated stats
    stats = session_state["session_stats"]
    system_status = query_engine.get_system_status()
    
    # Calculate efficiency from session stats
    total = stats["total_added"] + stats["total_unchanged"]
    efficiency = (stats["total_unchanged"] / total * 100) if total > 0 else 0
    
    # Use actual document count from storage
    actual_docs = system_status["total_documents"]
    
    await manager.broadcast({
        "type": "stats",
        "data": {
            "total_docs": actual_docs,  # Actual count from storage
            "efficiency": round(efficiency, 1),
            "hot_tier": system_status["hot_tier_chunks"],
            "cold_tier": system_status["cold_tier_chunks"]
        }
    })

# Subscribe pipeline to stream
stream_simulator.subscribe(on_document_received)

@app.get("/")
async def get_ui():
    """Serve the UI"""
    html_file = Path(__file__).parent / "ui.html"
    return HTMLResponse(html_file.read_text(encoding='utf-8'))

@app.get("/storage")
async def get_storage_ui():
    """Serve the storage details UI"""
    html_file = Path(__file__).parent / "storage.html"
    return HTMLResponse(html_file.read_text(encoding='utf-8'))

@app.get("/api/storage")
async def get_storage_data():
    """Get storage details for both tiers"""
    try:
        # Get hot tier data (Milvus)
        hot_status = query_engine.get_system_status()
        hot_chunks = []
        
        # Get sample chunks from Milvus
        try:
            from pymilvus import connections, Collection, utility
            connections.connect(host="localhost", port="19530")
            
            # Check if collection exists
            if not utility.has_collection("doc_chunks"):
                print("Collection 'doc_chunks' does not exist")
                hot_chunks = []
            else:
                collection = Collection("doc_chunks")
                collection.load()
                
                # Query all chunks (no filter since all in hot tier are active)
                results = collection.query(
                    expr="chunk_id != ''",
                    output_fields=["chunk_id", "doc_id", "content", "position", "valid_from"],
                    limit=50
                )
                
                # Format results
                for r in results:
                    r['status'] = 'active'  # All hot tier chunks are active
                
                hot_chunks = results
                print(f"Loaded {len(hot_chunks)} chunks from hot tier")
        except Exception as e:
            print(f"Error loading hot tier chunks: {e}")
            import traceback
            traceback.print_exc()
        
        # Get cold tier data (Delta Lake)
        from lakehouse.delta_store import DeltaStore
        delta_store = DeltaStore()
        cold_chunks = delta_store.get_all_chunks(limit=50)
        cold_stats = delta_store.get_stats()
        
        return {
            "hot_tier": {
                "total_chunks": hot_status["hot_tier_chunks"],
                "unique_docs": hot_status["total_documents"],
                "chunks": hot_chunks
            },
            "cold_tier": {
                "total_chunks": cold_stats.get("total_chunks", 0),
                "unique_docs": cold_stats.get("unique_docs", 0),
                "total_versions": cold_stats.get("total_versions", 0),
                "chunks": cold_chunks
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "hot_tier": {"total_chunks": 0, "unique_docs": 0, "chunks": []},
            "cold_tier": {"total_chunks": 0, "unique_docs": 0, "total_versions": 0, "chunks": []}
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    try:
        await manager.connect(websocket)
        print("WebSocket connected")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "get_stats":
                # Send current stats to sync UI
                stats = session_state["session_stats"]
                system_status = query_engine.get_system_status()
                
                # Calculate efficiency from session stats
                total = stats["total_added"] + stats["total_unchanged"]
                efficiency = (stats["total_unchanged"] / total * 100) if total > 0 else 0
                
                # Get actual document count from storage (not session counter)
                actual_docs = system_status["total_documents"]
                
                await websocket.send_json({
                    "type": "stats",
                    "data": {
                        "total_docs": actual_docs,  # Use actual count from storage
                        "efficiency": round(efficiency, 1),
                        "hot_tier": system_status["hot_tier_chunks"],
                        "cold_tier": system_status["cold_tier_chunks"]
                    }
                })
                
                # Send stream status
                await websocket.send_json({
                    "type": "stream_status",
                    "data": {"running": session_state["stream_running"]}
                })
            
            elif data["type"] == "reset_all":
                # Stop stream first
                stream_simulator.stop()
                
                # Reset Milvus
                try:
                    from pymilvus import utility, connections
                    connections.connect(host="localhost", port="19530")
                    if utility.has_collection("doc_chunks"):
                        utility.drop_collection("doc_chunks")
                    print("Milvus collection dropped")
                except Exception as e:
                    print(f"Error resetting Milvus: {e}")
                
                # Reset Delta Lake
                try:
                    import shutil
                    delta_path = Path("./lakehouse/chunks")
                    if delta_path.exists():
                        shutil.rmtree(delta_path)
                    print("Delta Lake cleared")
                except Exception as e:
                    print(f"Error resetting Delta Lake: {e}")
                
                # Reset hash store
                try:
                    hash_store_path = Path("cdc_hash_store.json")
                    if hash_store_path.exists():
                        hash_store_path.unlink()
                    print("Hash store cleared")
                except Exception as e:
                    print(f"Error resetting hash store: {e}")
                
                # Reset session state
                session_state["stream_running"] = False
                session_state["session_stats"] = {
                    "total_docs": 0,
                    "total_added": 0,
                    "total_unchanged": 0,
                    "total_deleted": 0
                }
                
                # Reset pipeline stats
                pipeline_service.stats = {
                    "total_docs": 0,
                    "total_added": 0,
                    "total_unchanged": 0,
                    "total_deleted": 0
                }
                
                await websocket.send_json({"type": "status", "data": "System reset complete"})
                print("System reset complete")
            
            elif data["type"] == "start_stream":
                if not stream_simulator.is_running:
                    asyncio.create_task(stream_simulator.start())
                    session_state["stream_running"] = True
                    await websocket.send_json({"type": "status", "data": "Stream started"})
            
            elif data["type"] == "stop_stream":
                stream_simulator.stop()
                session_state["stream_running"] = False
                await websocket.send_json({"type": "status", "data": "Stream stopped"})
            
            elif data["type"] == "query":
                query_text = data["query"]
                mode = data.get("mode", "current")
                temporal_date = data.get("temporal_date")
                
                try:
                    if mode == "temporal" and temporal_date:
                        # Convert datetime string to timestamp
                        from datetime import datetime
                        dt = datetime.fromisoformat(temporal_date)
                        timestamp = int(dt.timestamp())
                        raw_results = query_engine.query_historical(query_text, timestamp, top_k=3)
                        results = query_engine.format_results_for_ui(raw_results, query_text, "historical")
                    else:
                        raw_results = query_engine.query_current(query_text, top_k=3)
                        results = query_engine.format_results_for_ui(raw_results, query_text, "current")
                    
                    await websocket.send_json({
                        "type": "query_response",
                        "data": results
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": str(e)
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
