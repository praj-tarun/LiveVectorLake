"""
Initial Data Loader - Loads base knowledge before streaming starts
Demonstrates initial ingestion and sets up for CDC updates
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.cdc_pipeline import CDCPipeline

# Initial knowledge base documents
INITIAL_DOCS = {
    "policy_001": """
    Security Policy v1.0
    Last Updated: 2024-01-01
    
    Access Control: All production systems require multi-factor authentication.
    Password Requirements: Minimum 12 characters with complexity requirements.
    Data Classification: Confidential data must be encrypted at rest and in transit.
    Incident Response: Security incidents must be reported within 1 hour of detection.
    """,
    
    "policy_002": """
    Backup Policy v1.0
    Last Updated: 2024-01-01
    
    Backup Schedule: Daily incremental backups at 2 AM, weekly full backups on Sunday.
    Retention Period: Daily backups retained for 30 days, weekly backups for 1 year.
    Backup Verification: Monthly restore tests required for all critical systems.
    """,
    
    "system_001": """
    Production Database Server
    Hostname: prod-db-01.company.com
    IP: 10.0.1.50
    
    Configuration: PostgreSQL 14.5, 64GB RAM, 2TB SSD storage
    Purpose: Primary customer database for web application
    Backup: Daily snapshots to S3, point-in-time recovery enabled
    Monitoring: CloudWatch metrics, PagerDuty alerts configured
    """,
    
    "system_002": """
    API Gateway Server
    Hostname: api-gateway-01.company.com
    IP: 10.0.1.100
    
    Configuration: NGINX 1.21, Load balanced across 3 instances
    Purpose: Public API endpoint for mobile and web clients
    Rate Limiting: 1000 requests per minute per API key
    SSL: TLS 1.3, certificate expires 2024-12-31
    """,
    
    "runbook_001": """
    Incident Response Runbook
    
    Step 1: Detect and Triage
    - Monitor alerts from CloudWatch, PagerDuty, or user reports
    - Assess severity: Critical, High, Medium, Low
    - Create incident ticket in Jira
    
    Step 2: Contain
    - Isolate affected systems if necessary
    - Block malicious IPs at firewall level
    - Disable compromised user accounts
    
    Step 3: Investigate
    - Collect logs from affected systems
    - Analyze attack vectors and entry points
    - Document timeline of events
    
    Step 4: Remediate
    - Apply security patches
    - Update firewall rules
    - Reset compromised credentials
    
    Step 5: Post-Mortem
    - Document lessons learned
    - Update security policies
    - Implement preventive measures
    """
}

def load_initial_data():
    """Load initial knowledge base"""
    print("Loading initial knowledge base...")
    
    # Create data directory
    data_dir = Path("data/initial_load")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Write documents
    for doc_id, content in INITIAL_DOCS.items():
        file_path = data_dir / f"{doc_id}.txt"
        file_path.write_text(content.strip())
    
    # Ingest through pipeline
    pipeline = CDCPipeline()
    result = pipeline.ingest_directory(str(data_dir), reset=False)
    
    print(f"\n✓ Initial data loaded:")
    print(f"  Documents: {result['documents_processed']}")
    print(f"  Chunks added: {result['chunks_added']}")
    print(f"  Total chunks: {result['chunks_added']}")
    
    return result

if __name__ == "__main__":
    load_initial_data()
