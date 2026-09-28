"""
Populates detailed Investigation Steps, Root Cause Analysis, Actions Taken,
Successful Resolutions, and Lessons Learned across incidents in the SQLite Database.
"""

import json
from datetime import datetime, timezone
from backend.database import get_db_connection, db_get_all, db_save_incident
from backend.services.incident_service import incident_service

INVESTIGATION_TEMPLATES = {
    "Brute-Force Attack": {
        "investigation_process": (
            "1. Analyzed auth.log telemetry and identified 1,420 failed SSH attempts within a 4-minute window.\n"
            "2. Traced source IP 192.168.1.105 via GeoIP intelligence to an unauthorized external proxy.\n"
            "3. Verified bastion host session logs to confirm whether any login attempt succeeded.\n"
            "4. Checked endpoint memory artifacts and PAM authentication daemon configuration."
        ),
        "root_cause": "Perimeter bastion host exposed SSH on standard port 22 with password-based authentication enabled instead of enforcing hardware security keys and VPN IP whitelisting.",
        "actions_taken": "Enforced perimeter firewall block on source subnet; rotated compromised credentials; disabled password authentication in sshd_config and enforced ed25519 key-only access.",
        "successful_resolution": "SSH port restricted to internal management subnet (10.0.0.0/16); zero unauthorized ingress confirmed across 48-hour monitoring window.",
        "lessons_learned": "Enforce automated CI/CD security linting for SSH configurations and require mandatory MFA on all bastion jump hosts.",
        "analyst_feedback": "AI triage correctly flagged the high-volume failure pattern and recommended immediate network isolation."
    },
    "Physical Threat & Hostile Statement": {
        "investigation_process": (
            "1. Ingested internal communication telemetry containing violent hostile threat indicators.\n"
            "2. Cross-referenced badge reader logs at facility turnstiles to locate individual's physical presence.\n"
            "3. Coordinated immediate priority triage with Corporate Physical Security and HR Legal.\n"
            "4. Preserved digital audit trail and workstation activity logs for chain-of-custody documentation."
        ),
        "root_cause": "Insider threat incident involving hostile verbal statements and safety escalation violating corporate safety policies.",
        "actions_taken": "Revoked physical access badges immediately; suspended Active Directory, SSO, and VPN sessions; dispatched physical security personnel for on-site assessment.",
        "successful_resolution": "Perimeter and facility access secured; employee escorted off premises by security with formal HR and legal protocol initiated.",
        "lessons_learned": "Integrate automated workplace violence threat detection with real-time physical badge revocation workflows.",
        "analyst_feedback": "Rapid severity auto-escalation to HIGH prevented potential physical safety escalation."
    },
    "Malware Detection": {
        "investigation_process": (
            "1. Ingested EDR process creation alerts indicating anomalous PowerShell execution with base64 payloads.\n"
            "2. Extracted SHA-256 hash and submitted to VirusTotal / Sandbox analysis.\n"
            "3. Queried network flow logs for command-and-control (C2) beaconing activity.\n"
            "4. Scanned adjacent endpoints on the same VLAN for lateral propagation."
        ),
        "root_cause": "Malicious macro-enabled attachment executed from a spear-phishing email on an unpatched engineering workstation.",
        "actions_taken": "Isolated infected host from the network; terminated malicious parent and child processes; removed persistent registry run keys; updated EDR behavioral signatures.",
        "successful_resolution": "Host sanitized, re-imaged from golden baseline image, and restored to production with enhanced EDR monitoring.",
        "lessons_learned": "Enforce strict PowerShell script block logging and block macro execution across all incoming email gateways.",
        "analyst_feedback": "EDR telemetry integration allowed automated host containment within 90 seconds of alert trigger."
    },
    "Phishing Attempt": {
        "investigation_process": (
            "1. Inspected inbound email headers, SPF/DKIM/DMARC records, and embedded hyperlinked domains.\n"
            "2. Identified spoofed Microsoft 365 credential harvesting landing page.\n"
            "3. Queried email gateway logs to discover all internal recipients who received the same message.\n"
            "4. Analyzed Azure AD sign-in logs for anomalous token generation or MFA fatigue prompts."
        ),
        "root_cause": "Sophisticated typosquatted domain bypassing legacy email spam filters to harvest corporate SSO credentials.",
        "actions_taken": "Purged phishing email from all user mailboxes; blocked malicious sender domain and hosting IP at firewall; initiated forced password resets for targeted users.",
        "successful_resolution": "Phishing campaign neutralized across all 250 inboxes with zero credential compromise or unauthorized logins.",
        "lessons_learned": "Deploy FIDO2 WebAuthn hardware tokens to make credential harvesting attacks completely ineffective.",
        "analyst_feedback": "Fast domain blocking prevented secondary clicks across internal staff."
    },
    "Data-Access Anomaly": {
        "investigation_process": (
            "1. CloudTrail anomaly alert flagged bulk S3 bucket downloads exceeding 50GB outside business hours.\n"
            "2. Inspected IAM role assume-role events and associated IP addresses.\n"
            "3. Cross-checked with data owner to verify if download was authorized.\n"
            "4. Reviewed DLP logs to inspect sensitive data classifications (PII/PCI)."
        ),
        "root_cause": "Stale developer IAM access key exposed in a private git repository and utilized without IP restriction.",
        "actions_taken": "Revoked exposed IAM access key immediately; applied restrictive S3 bucket policy; rotated all shared database connection strings.",
        "successful_resolution": "Unauthorized S3 access terminated; data exfiltration scope contained and verified against audit ledger.",
        "lessons_learned": "Implement automated secret scanning in Git pre-commit hooks and enforce short-lived IAM STS session tokens.",
        "analyst_feedback": "Hindsight memory match to previous S3 exfiltration playbook saved 40 minutes of triage time."
    },
    "DDoS Attack": {
        "investigation_process": (
            "1. Detected ingress spike exceeding 150,000 HTTP requests/sec on edge load balancer.\n"
            "2. Inspected HTTP request headers to identify signature characteristics of Layer 7 botnet flood.\n"
            "3. Evaluated origin server CPU utilization and error rate telemetry.\n"
            "4. Coordinated Cloudflare/AWS Shield rate limiting rules."
        ),
        "root_cause": "Distributed botnet targeting public API endpoint with un-cached search queries to exhaust database connection pool.",
        "actions_taken": "Enabled WAF managed challenge rules; enforced rate limiting of 50 req/min per IP; scaled backend replica pods.",
        "successful_resolution": "Traffic normalized within 3 minutes; origin server latency returned to <85ms baseline.",
        "lessons_learned": "Implement edge Redis caching for expensive dynamic queries and tune proactive WAF rate limits.",
        "analyst_feedback": "Automated WAF challenge mitigation prevented complete service disruption."
    },
    "Lateral Movement": {
        "investigation_process": (
            "1. SIEM correlated abnormal Pass-the-Hash / SMB authentication attempts originating from staging server.\n"
            "2. Inspected Windows Security Event 4624 (Type 3) network logins across domain controllers.\n"
            "3. Dumped memory artifacts to detect Mimikatz or PsExec artifacts.\n"
            "4. Checked active Kerberos ticket granting requests (TGS) for service accounts."
        ),
        "root_cause": "Compromised local administrator password shared across multiple internal servers enabled credential dumping and lateral hopping.",
        "actions_taken": "Deployed LAPS (Local Administrator Password Solution); isolated staging subnet; forced Kerberos KRBTGT password rotation.",
        "successful_resolution": "Lateral movement path severed; zero domain escalation achieved by threat actor.",
        "lessons_learned": "Eliminate shared local administrator credentials across all server tiers.",
        "analyst_feedback": "Hindsight memory recall quickly surfaced the exact LAPS remediation playbook."
    },
    "Account Takeover": {
        "investigation_process": (
            "1. Azure AD Identity Protection flagged impossible travel login between London and Tokyo in 15 minutes.\n"
            "2. Detected unauthorized OAuth application consent granting offline mail access.\n"
            "3. Revoked active session refresh tokens across all tenant devices.\n"
            "4. Analyzed mailbox forwarding rules and deleted items."
        ),
        "root_cause": "Attacker bypassed SMS-based MFA via SIM swap / session hijacking and granted malicious OAuth permissions.",
        "actions_taken": "Revoked all active OAuth grants; reset account passwords; enforced Number Matching Authenticator MFA.",
        "successful_resolution": "Account reclaimed and verified; malicious forwarding rules removed.",
        "lessons_learned": "Deprecate SMS authentication in favor of FIDO2 or app-based number matching MFA.",
        "analyst_feedback": "OAuth permission review workflow was executed accurately."
    },
    "Unauthorized Privilege Change": {
        "investigation_process": (
            "1. Audit trail alert detected user account added to Domain Admins outside change management window.\n"
            "2. Correlated administrative action to service account API token.\n"
            "3. Interviewed requesting engineer to verify authorized ticket ID.\n"
            "4. Reverted group membership and reviewed active domain controller sessions."
        ),
        "root_cause": "Misconfigured automation script mistakenly assigned Domain Admin scope instead of scoped Helpdesk role.",
        "actions_taken": "Removed user from privileged group; audited all actions taken during elevated window; updated automation RBAC definitions.",
        "successful_resolution": "Privileges restored to least-privilege baseline with zero unauthorized system modifications.",
        "lessons_learned": "Enforce Just-In-Time (JIT) privileged access management with dual-approval requirements.",
        "analyst_feedback": "Immediate alert triggering minimized elevated window to under 5 minutes."
    }
}

DEFAULT_TEMPLATE = {
    "investigation_process": (
        "1. Captured and analyzed system syslog and EDR telemetry.\n"
        "2. Correlated network ingress connections with threat intelligence feeds.\n"
        "3. Inspected host process execution tree and authenticated sessions.\n"
        "4. Validated system integrity against baseline SOC runbooks."
    ),
    "root_cause": "Unmitigated configuration vulnerability on perimeter system exposed to untrusted network traffic.",
    "actions_taken": "Applied firewall perimeter block; rotated credentials; verified system telemetry and patched software components.",
    "successful_resolution": "Threat contained and verified; all services restored to normal operational baseline.",
    "lessons_learned": "Enforce continuous vulnerability assessment and strict network segmentation.",
    "analyst_feedback": "Incident handled smoothly following SOC standard operating procedures."
}

def enrich_all_incidents():
    incidents = db_get_all()
    print(f"[*] Processing {len(incidents)} incidents in SQLite database...")
    
    updated_count = 0
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for inc in incidents:
        itype = inc.get("type", "Brute-Force Attack")
        template = INVESTIGATION_TEMPLATES.get(itype, DEFAULT_TEMPLATE)
        
        # Populate investigation process if missing
        if not inc.get("investigation_process"):
            inc["investigation_process"] = template["investigation_process"]
            
        # If incident is resolved or needs resolution fields filled
        if not inc.get("root_cause"):
            inc["root_cause"] = template["root_cause"]
        if not inc.get("actions_taken"):
            inc["actions_taken"] = template["actions_taken"]
        if not inc.get("successful_resolution"):
            inc["successful_resolution"] = template["successful_resolution"]
        if not inc.get("lessons_learned"):
            inc["lessons_learned"] = template["lessons_learned"]
        if not inc.get("analyst_feedback"):
            inc["analyst_feedback"] = template["analyst_feedback"]
            
        # Ensure status is properly resolved if resolution fields are populated
        if inc.get("status") == "OPEN" and inc.get("id") in ["INC-2026-1044", "INC-2026-1001", "INC-2026-1002"]:
            inc["status"] = "RESOLVED"
            inc["resolved_at"] = now_str
            
        db_save_incident(inc)
        updated_count += 1
        
    # Sync with JSON
    incident_service._sync_to_json()
    print(f"[+] Successfully enriched {updated_count} incidents with detailed investigation and resolution data in SQLite DB!")

if __name__ == "__main__":
    enrich_all_incidents()
