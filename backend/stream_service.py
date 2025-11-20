"""
Stream Simulator Service - Generates continuous document stream
Independent component that simulates Kafka-like streaming
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, List
import json

class StreamSimulator:
    def __init__(self):
        self.is_running = False
        self.rate = 2  # docs per second
        self.subscribers = []
        
        self.topics = [
            "Security incident: Unauthorized access detected in production database",
            "Performance alert: API response time exceeded 2.5s threshold",
            "Network anomaly: Unusual traffic from external IP range",
            "System health: Memory usage spike on application server",
            "Compliance: Failed login attempts exceeded security policy",
            "Infrastructure: Load balancer health check failure",
            "Data integrity: Checksum mismatch during backup",
            "Monitoring: SSL certificate expiration warning",
            "Audit: Privileged user modified database schema",
            "Incident: DDoS attack mitigated - 10K req/sec blocked"
        ]
    
    def generate_document(self) -> Dict:
        """Generate a random document"""
        doc_id = f"doc_{random.randint(1000, 9999)}"
        content = f"{random.choice(self.topics)}. " + \
                  f"Timestamp: {datetime.now().isoformat()}. " + \
                  f"Severity: {random.choice(['Critical', 'High', 'Medium', 'Low'])}. " + \
                  f"Status: {random.choice(['Active', 'Investigating', 'Resolved'])}."
        
        return {
            "doc_id": doc_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    
    async def start(self):
        """Start streaming documents"""
        self.is_running = True
        while self.is_running:
            doc = self.generate_document()
            # Notify all subscribers
            for subscriber in self.subscribers:
                await subscriber(doc)
            await asyncio.sleep(1.0 / self.rate)
    
    def stop(self):
        """Stop streaming"""
        self.is_running = False
    
    def subscribe(self, callback):
        """Subscribe to document stream"""
        self.subscribers.append(callback)
    
    def set_rate(self, rate: int):
        """Set documents per second"""
        self.rate = max(1, min(rate, 10))  # 1-10 docs/sec

# Global instance
stream_simulator = StreamSimulator()
