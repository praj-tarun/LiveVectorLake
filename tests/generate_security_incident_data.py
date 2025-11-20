"""Generate realistic security incident demo data using Ollama LLM"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import requests
from datetime import datetime, timedelta

def generate_with_ollama(prompt, model="llama3:latest"):
    """Generate text using Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            print(f"Error: Ollama returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def create_incident_documents():
    """Generate security incident documents for 6 time points"""
    
    base_path = Path("data/demo_streams/security_incident")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Base timestamp for incident
    base_time = datetime(2024, 1, 15, 10, 0, 0)
    
    print("="*70)
    print("GENERATING SECURITY INCIDENT DEMO DATA")
    print("="*70)
    print("\nUsing Ollama (llama3:latest) to generate realistic content...")
    print("This will take 2-3 minutes...\n")
    
    # ========================================================================
    # T+0: INITIAL DETECTION (10:00 UTC)
    # ========================================================================
    print("[1/6] Generating T+0: Initial Detection...")
    t0_path = base_path / "t0_initial"
    t0_path.mkdir(exist_ok=True)
    
    # Document 1: Initial Alert
    prompt1 = """Write a professional security incident alert report (3-4 paragraphs) about:
- Suspicious login attempts detected at 10:00 UTC
- Multiple failed authentication attempts from IP 185.220.101.45
- Targeting production VPN gateway
- Security team notified, investigation initiated
Keep it factual, technical, and concise."""
    
    content1 = generate_with_ollama(prompt1)
    if content1:
        with open(t0_path / "incident_alert_001.txt", "w") as f:
            f.write("SECURITY INCIDENT ALERT - INITIAL DETECTION\n")
            f.write(f"Timestamp: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Severity: MEDIUM\n")
            f.write(f"Status: INVESTIGATING\n\n")
            f.write(content1)
    
    # Document 2: System Status
    with open(t0_path / "system_status_001.txt", "w") as f:
        f.write("SYSTEM STATUS REPORT\n")
        f.write(f"Timestamp: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("All systems operational. VPN gateway showing elevated failed login attempts.\n\n")
        f.write("Affected Systems:\n")
        f.write("- VPN Gateway (vpn-prod-01): Operational, monitoring enabled\n")
        f.write("- Authentication Service: Operational\n")
        f.write("- Production Environment: No impact\n\n")
        f.write("Security team has been notified and is investigating the source of login attempts.")
    
    # Document 3: Initial Response
    with open(t0_path / "response_log_001.txt", "w") as f:
        f.write("INCIDENT RESPONSE LOG\n")
        f.write(f"Incident ID: INC-2024-0115-001\n")
        f.write(f"Started: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("Actions Taken:\n")
        f.write("1. Security monitoring systems detected anomalous login patterns\n")
        f.write("2. Automated alert triggered and sent to security team\n")
        f.write("3. On-call security engineer acknowledged alert\n")
        f.write("4. Initial triage: Suspicious activity from external IP\n")
        f.write("5. Investigation initiated - gathering logs and network traffic data\n")
    
    print("   ✓ Created 3 documents")
    
    # ========================================================================
    # T+15: ESCALATION (10:15 UTC)
    # ========================================================================
    print("[2/6] Generating T+15: Escalation...")
    t15_path = base_path / "t15_escalation"
    t15_path.mkdir(exist_ok=True)
    
    # Update Alert (modified)
    prompt2 = """Write a security incident escalation report (3-4 paragraphs) about:
- Confirmed unauthorized access to staging environment
- Attacker used compromised credentials
- Lateral movement detected
- Incident escalated to CRITICAL severity
- Incident response team activated
Keep it urgent but professional."""
    
    content2 = generate_with_ollama(prompt2)
    if content2:
        with open(t15_path / "incident_alert_001.txt", "w") as f:
            f.write("SECURITY INCIDENT ALERT - ESCALATION\n")
            f.write(f"Timestamp: {(base_time + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Severity: CRITICAL\n")
            f.write(f"Status: ACTIVE BREACH\n\n")
            f.write(content2)
    
    # Copy unchanged documents
    with open(t15_path / "system_status_001.txt", "w") as f:
        f.write("SYSTEM STATUS REPORT\n")
        f.write(f"Timestamp: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("All systems operational. VPN gateway showing elevated failed login attempts.\n\n")
        f.write("Affected Systems:\n")
        f.write("- VPN Gateway (vpn-prod-01): Operational, monitoring enabled\n")
        f.write("- Authentication Service: Operational\n")
        f.write("- Production Environment: No impact\n\n")
        f.write("Security team has been notified and is investigating the source of login attempts.")
    
    with open(t15_path / "response_log_001.txt", "w") as f:
        f.write("INCIDENT RESPONSE LOG\n")
        f.write(f"Incident ID: INC-2024-0115-001\n")
        f.write(f"Started: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("Actions Taken:\n")
        f.write("1. Security monitoring systems detected anomalous login patterns\n")
        f.write("2. Automated alert triggered and sent to security team\n")
        f.write("3. On-call security engineer acknowledged alert\n")
        f.write("4. Initial triage: Suspicious activity from external IP\n")
        f.write("5. Investigation initiated - gathering logs and network traffic data\n")
    
    # New document: Threat Analysis
    prompt3 = """Write a technical threat analysis report (3-4 paragraphs) about:
- Compromised credentials identified (user: jenkins-deploy)
- Attack vector: Phishing email with malicious link
- Attacker gained access to staging environment
- Evidence of reconnaissance and data exfiltration attempts
Keep it technical and detailed."""
    
    content3 = generate_with_ollama(prompt3)
    if content3:
        with open(t15_path / "threat_analysis_001.txt", "w") as f:
            f.write("THREAT ANALYSIS REPORT\n")
            f.write(f"Timestamp: {(base_time + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Analyst: Security Operations Center\n\n")
            f.write(content3)
    
    print("   ✓ Created 4 documents (1 modified, 2 unchanged, 1 new)")
    
    # ========================================================================
    # T+45: CONTAINMENT (10:45 UTC)
    # ========================================================================
    print("[3/6] Generating T+45: Containment...")
    t45_path = base_path / "t45_containment"
    t45_path.mkdir(exist_ok=True)
    
    # Update Alert (modified)
    with open(t45_path / "incident_alert_001.txt", "w") as f:
        f.write("SECURITY INCIDENT ALERT - CONTAINMENT\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Severity: HIGH\n")
        f.write(f"Status: CONTAINED\n\n")
        f.write("The security incident has been successfully contained. Affected systems have been isolated from the network.\n\n")
        f.write("All compromised credentials have been rotated and multi-factor authentication has been enforced across all services.\n\n")
        f.write("The attacker's access has been terminated. No evidence of production environment compromise has been found.\n\n")
        f.write("Investigation continues to determine the full scope of the breach and identify any additional indicators of compromise.")
    
    # Update System Status (modified)
    with open(t45_path / "system_status_001.txt", "w") as f:
        f.write("SYSTEM STATUS REPORT\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("CONTAINMENT ACTIONS COMPLETED\n\n")
        f.write("Affected Systems:\n")
        f.write("- VPN Gateway (vpn-prod-01): ISOLATED - Access restricted\n")
        f.write("- Staging Environment: ISOLATED - Network segmentation applied\n")
        f.write("- Authentication Service: SECURED - All credentials rotated\n")
        f.write("- Production Environment: OPERATIONAL - No compromise detected\n\n")
        f.write("All systems are being monitored for any signs of persistent access or backdoors.")
    
    # Copy unchanged
    with open(t45_path / "response_log_001.txt", "w") as f:
        f.write("INCIDENT RESPONSE LOG\n")
        f.write(f"Incident ID: INC-2024-0115-001\n")
        f.write(f"Started: {base_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("Actions Taken:\n")
        f.write("1. Security monitoring systems detected anomalous login patterns\n")
        f.write("2. Automated alert triggered and sent to security team\n")
        f.write("3. On-call security engineer acknowledged alert\n")
        f.write("4. Initial triage: Suspicious activity from external IP\n")
        f.write("5. Investigation initiated - gathering logs and network traffic data\n")
    
    with open(t45_path / "threat_analysis_001.txt", "w") as f:
        f.write("THREAT ANALYSIS REPORT\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Analyst: Security Operations Center\n\n")
        if content3:
            f.write(content3)
    
    # New document: Containment Actions
    prompt4 = """Write a detailed containment actions report (3-4 paragraphs) about:
- Systems isolated from network at 10:45 UTC
- All compromised credentials rotated immediately
- Multi-factor authentication enforced
- Network segmentation applied to staging environment
- Attacker access terminated
Keep it action-oriented and technical."""
    
    content4 = generate_with_ollama(prompt4)
    if content4:
        with open(t45_path / "containment_actions_001.txt", "w") as f:
            f.write("CONTAINMENT ACTIONS REPORT\n")
            f.write(f"Timestamp: {(base_time + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Response Team: Incident Response Team Alpha\n\n")
            f.write(content4)
    
    print("   ✓ Created 5 documents (2 modified, 2 unchanged, 1 new)")
    
    # ========================================================================
    # T+90: INVESTIGATION (11:30 UTC)
    # ========================================================================
    print("[4/6] Generating T+90: Investigation...")
    t90_path = base_path / "t90_investigation"
    t90_path.mkdir(exist_ok=True)
    
    # Update Alert
    with open(t90_path / "incident_alert_001.txt", "w") as f:
        f.write("SECURITY INCIDENT ALERT - INVESTIGATION\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=90)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Severity: MEDIUM\n")
        f.write(f"Status: INVESTIGATING\n\n")
        f.write("Incident contained. Root cause analysis in progress.\n\n")
        f.write("Forensic investigation has identified the initial attack vector as a spear-phishing email sent to the jenkins-deploy service account owner.\n\n")
        f.write("Malware analysis reveals a custom credential harvester was deployed. No evidence of data exfiltration from production systems.\n\n")
        f.write("Investigation continues to identify all affected systems and ensure no persistence mechanisms remain.")
    
    # Copy unchanged documents
    for doc in ["system_status_001.txt", "response_log_001.txt", "threat_analysis_001.txt", "containment_actions_001.txt"]:
        src = t45_path / doc
        dst = t90_path / doc
        if src.exists():
            with open(src, "r") as f:
                content = f.read()
            with open(dst, "w") as f:
                f.write(content)
    
    # New document: Forensic Analysis
    prompt5 = """Write a forensic analysis report (3-4 paragraphs) about:
- Malware identified: Custom credential harvester
- Attack timeline reconstructed from logs
- Initial access via phishing email on January 14
- Lateral movement to staging environment
- No evidence of production compromise
Keep it technical and forensic-focused."""
    
    content5 = generate_with_ollama(prompt5)
    if content5:
        with open(t90_path / "forensic_analysis_001.txt", "w") as f:
            f.write("FORENSIC ANALYSIS REPORT\n")
            f.write(f"Timestamp: {(base_time + timedelta(minutes=90)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Forensic Analyst: Digital Forensics Team\n\n")
            f.write(content5)
    
    print("   ✓ Created 6 documents (1 modified, 4 unchanged, 1 new)")
    
    # ========================================================================
    # T+150: RESOLUTION (12:30 UTC)
    # ========================================================================
    print("[5/6] Generating T+150: Resolution...")
    t150_path = base_path / "t150_resolution"
    t150_path.mkdir(exist_ok=True)
    
    # Update Alert
    with open(t150_path / "incident_alert_001.txt", "w") as f:
        f.write("SECURITY INCIDENT ALERT - RESOLVED\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=150)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Severity: LOW\n")
        f.write(f"Status: RESOLVED\n\n")
        f.write("Security incident has been fully resolved. All affected systems have been cleaned and restored to normal operation.\n\n")
        f.write("Enhanced monitoring and additional security controls have been implemented to prevent similar incidents.\n\n")
        f.write("Post-incident review scheduled for January 16, 2024. All stakeholders will be notified of findings and remediation actions.")
    
    # Update System Status
    with open(t150_path / "system_status_001.txt", "w") as f:
        f.write("SYSTEM STATUS REPORT\n")
        f.write(f"Timestamp: {(base_time + timedelta(minutes=150)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write("ALL SYSTEMS OPERATIONAL\n\n")
        f.write("System Status:\n")
        f.write("- VPN Gateway (vpn-prod-01): OPERATIONAL - Enhanced monitoring active\n")
        f.write("- Staging Environment: OPERATIONAL - Rebuilt and secured\n")
        f.write("- Authentication Service: OPERATIONAL - MFA enforced\n")
        f.write("- Production Environment: OPERATIONAL - No impact\n\n")
        f.write("All systems have been restored to normal operation with enhanced security controls.")
    
    # Copy unchanged
    for doc in ["response_log_001.txt", "threat_analysis_001.txt", "containment_actions_001.txt", "forensic_analysis_001.txt"]:
        src = t90_path / doc
        dst = t150_path / doc
        if src.exists():
            with open(src, "r") as f:
                content = f.read()
            with open(dst, "w") as f:
                f.write(content)
    
    # New document: Resolution Summary
    prompt6 = """Write a resolution summary report (3-4 paragraphs) about:
- All affected systems cleaned and restored
- Security patches applied
- Enhanced monitoring implemented
- User security awareness training scheduled
- Incident successfully resolved
Keep it conclusive and forward-looking."""
    
    content6 = generate_with_ollama(prompt6)
    if content6:
        with open(t150_path / "resolution_summary_001.txt", "w") as f:
            f.write("INCIDENT RESOLUTION SUMMARY\n")
            f.write(f"Timestamp: {(base_time + timedelta(minutes=150)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Incident Commander: Security Operations Manager\n\n")
            f.write(content6)
    
    print("   ✓ Created 7 documents (2 modified, 4 unchanged, 1 new)")
    
    # ========================================================================
    # T+240: POST-MORTEM (14:00 UTC)
    # ========================================================================
    print("[6/6] Generating T+240: Post-Mortem...")
    t240_path = base_path / "t240_postmortem"
    t240_path.mkdir(exist_ok=True)
    
    # Copy all previous documents
    for doc in ["incident_alert_001.txt", "system_status_001.txt", "response_log_001.txt", 
                "threat_analysis_001.txt", "containment_actions_001.txt", "forensic_analysis_001.txt",
                "resolution_summary_001.txt"]:
        src = t150_path / doc
        dst = t240_path / doc
        if src.exists():
            with open(src, "r") as f:
                content = f.read()
            with open(dst, "w") as f:
                f.write(content)
    
    # New document: Post-Mortem Report
    prompt7 = """Write a comprehensive post-mortem report (4-5 paragraphs) covering:
- Root cause: Phishing attack targeting service account
- Timeline of events from detection to resolution
- Lessons learned and gaps identified
- Remediation actions: MFA enforcement, security training, monitoring enhancements
- Recommendations for preventing future incidents
Keep it professional and comprehensive."""
    
    content7 = generate_with_ollama(prompt7)
    if content7:
        with open(t240_path / "postmortem_report_001.txt", "w") as f:
            f.write("POST-INCIDENT REVIEW - FINAL REPORT\n")
            f.write(f"Incident ID: INC-2024-0115-001\n")
            f.write(f"Report Date: {(base_time + timedelta(minutes=240)).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Prepared by: Security Operations Center\n\n")
            f.write(content7)
    
    print("   ✓ Created 8 documents (7 unchanged, 1 new)")
    
    print("\n" + "="*70)
    print("✅ DEMO DATA GENERATION COMPLETE")
    print("="*70)
    print(f"\nGenerated 6 time-stamped folders in: {base_path}")
    print("\nFolder structure:")
    print("  t0_initial/      - 3 documents (initial detection)")
    print("  t15_escalation/  - 4 documents (1 modified, 1 new)")
    print("  t45_containment/ - 5 documents (2 modified, 1 new)")
    print("  t90_investigation/ - 6 documents (1 modified, 1 new)")
    print("  t150_resolution/ - 7 documents (2 modified, 1 new)")
    print("  t240_postmortem/ - 8 documents (1 new)")
    print("\nTotal: 33 document files showing realistic incident evolution")
    print("\nNext steps:")
    print("1. Test CDC detection: python src/cli.py ingest data/demo_streams/security_incident/t0_initial --reset")
    print("2. Ingest updates: python src/cli.py ingest data/demo_streams/security_incident/t15_escalation")
    print("3. Query: python src/cli.py query \"incident status\"")

if __name__ == "__main__":
    create_incident_documents()
