import os
import json
import httpx
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class AIService:
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def api_key(self) -> str:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        return os.getenv("GROQ_API_KEY", "")

    @property
    def model(self) -> str:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
<<<<<<< HEAD
        return os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
=======
        return os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
>>>>>>> 9e33a6993227b8a707af8d7479c82e38245810a0

    async def analyze_incident(
        self,
        incident_data: Dict[str, Any],
        historical_memories: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes an incoming incident using LLM.
        If historical memories from Hindsight are supplied, performs Memory-Aware Triage.
        If no API key is provided, returns high-precision structured synthetic analysis.
        """
        if not self.api_key:
            return self._generate_fallback_analysis(incident_data, historical_memories)

        try:
            prompt = self._build_prompt(incident_data, historical_memories)
<<<<<<< HEAD
            async with httpx.AsyncClient(timeout=12.0) as client:
=======
            async with httpx.AsyncClient(timeout=30.0) as client:
>>>>>>> 9e33a6993227b8a707af8d7479c82e38245810a0
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are Incident Response Agent, an elite AI Cybersecurity Incident Response Agent. "
                                    "Analyze the security incident thoroughly. If historical Hindsight memories are provided, "
                                    "explicitly cite them in the historical evidence and tailor recommendations to proven past resolutions. "
                                    "Always return ONLY a valid JSON object matching the requested schema."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
                else:
                    print(f"LLM API Error ({response.status_code}): {response.text}")
                    return self._generate_fallback_analysis(incident_data, historical_memories)
        except Exception as e:
            print(f"Exception during LLM analysis: {e}")
            return self._generate_fallback_analysis(incident_data, historical_memories)

    async def synthesize_memory_answer(self, query: str, memories: List[Dict[str, Any]]) -> str:
        """
        Synthesizes a direct natural-language answer to an analyst's organizational memory query,
        citing relevant historical incidents from Hindsight.
        """
        if not memories:
            return f"No direct historical incident memories found in the Hindsight bank matching '{query}'."

        if not self.api_key:
            top = memories[0]
            return f"Based on organizational memory in {top.get('id')} ('{top.get('title')}'), similar attacks were caused by: '{top.get('root_cause')}'. The verified resolution was: '{top.get('successful_resolution')}'."

        try:
            prompt = (
                f"You are Incident Response Agent Security Memory Analyst. An analyst asked the following question about organizational security history:\n"
                f"QUESTION: \"{query}\"\n\n"
                f"RELEVANT HISTORICAL INCIDENT MEMORIES FROM HINDSIGHT:\n{json.dumps(memories, indent=2)}\n\n"
                f"Provide a concise, direct, professional answer (2-4 sentences) answering the analyst's question clearly, citing specific Incident IDs and verified resolutions from the retrieved memories."
            )
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are Incident Response Agent Security Memory AI. Answer questions about historical incident resolutions clearly and concisely citing Incident IDs."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 300
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error in synthesize_memory_answer: {e}")

        top = memories[0]
        return f"Based on organizational memory in {top.get('id')} ('{top.get('title')}'), similar incidents were caused by: '{top.get('root_cause')}'. The verified resolution was: '{top.get('successful_resolution')}'."

    def _build_prompt(self, inc: Dict[str, Any], memories: Optional[List[Dict[str, Any]]]) -> str:
        prompt = f"""
Analyze this incoming cybersecurity or physical security/hostile statement incident and return a JSON object with this exact structure:
{{
  "incident_classification": "string",
  "severity_assessment": "HIGH|MEDIUM|LOW",
  "explanation": "string",
  "possible_root_cause": "string",
  "indicators": ["string", "string"],
  "investigation_steps": ["string", "string"],
  "recommended_response": ["string", "string"],
  "reason_for_recommendation": "string",
  "historical_evidence": "string (explicitly describe how past Hindsight memories supported this recommendation)",
  "prevention_suggestions": ["string", "string"]
}}

CRITICAL SAFETY & SEVERITY RULE:
If the incident description, title, or logs contain ANY violent expressions, physical harm threats, threat-to-life phrases (e.g. 'he was killing me', 'I will harm/destroy', weapon mentions), hostile/abusive language, profanity, vulgarity, harassment, or bad sentences/words, you MUST assess severity_assessment as 'HIGH'. Classify under 'Physical Safety & Hostile Statement / Threat Alert', provide urgent protective containment recommendations (badge revocation, physical security notification, digital session termination, evidence preservation), and cite relevant safety memories.

CURRENT INCIDENT:
- Title: {inc.get('title')}
- Type: {inc.get('type')}
- Severity: {inc.get('severity')}
- Description: {inc.get('description')}
- Source IP: {inc.get('source_ip')}
- Username: {inc.get('username')}
- Affected System: {inc.get('affected_system')}
- Raw Logs/Alerts: {inc.get('additional_logs')}
"""
        if memories and len(memories) > 0:
            prompt += f"\nRELEVANT HINDSIGHT HISTORICAL MEMORIES:\n{json.dumps(memories, indent=2)}\n"
            prompt += "\nINSTRUCTION: Synthesize the current incident with the retrieved historical memories. Citing past successful resolutions from Hindsight makes this recommendation high confidence."
        else:
            prompt += "\nNo prior organizational memories found for this specific attack pattern."

        return prompt

    def _generate_fallback_analysis(
        self,
        inc: Dict[str, Any],
        memories: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Provides expert structured cybersecurity triage when offline or during demo"""
        inc_type = (inc.get("type") or "").lower()
        title = (inc.get("title") or "").lower()
        desc = (inc.get("description") or "").lower()
        logs = (inc.get("additional_logs") or "").lower()
        user = inc.get("username") or "unknown_identity"
        system = inc.get("affected_system") or "corporate_system"
        ip = inc.get("source_ip") or "127.0.0.1"

        # Hostile / Physical Threat / Bad Words / Harmful Language Detection
        bad_words_and_threats = [
            "kill", "killing", "murder", "harm", "destroy", "hostile", "threat", "extort", 
            "sabotage", "suicide", "abuse", "abusive", "harass", "harassment", "attack", "die", "death", 
            "violence", "violent", "bad", "hate", "toxic", "fuck", "shit", "bitch", "bastard", 
            "asshole", "idiot", "stupid", "slap", "shoot", "gun", "bomb", "knife", "punch", 
            "danger", "weapon", "execute", "hit", "beat", "curse", "ruin", "trash"
        ]
        is_hostile_threat = any(w in desc or w in title or w in logs for w in bad_words_and_threats)

        # Dynamic AI Severity Assessment
        if is_hostile_threat or "brute" in inc_type or "ssh" in title or "exfiltration" in desc or "cluster-admin" in desc or "cfo" in desc or "oauth" in desc:
            ai_severity = "HIGH"
        elif "mining" in desc or "xmrig" in desc or "malware" in inc_type or "impossible" in desc or "fatigue" in desc:
            ai_severity = "MEDIUM"
        elif "nmap" in desc or "scan" in desc or "intern" in desc:
            ai_severity = "LOW"
        else:
            ai_severity = "HIGH" if inc.get("severity") in ["AUTO", None, ""] else inc.get("severity", "HIGH")

        has_memory = bool(memories and len(memories) > 0)
        top_mem = memories[0] if has_memory else None

        if is_hostile_threat or "hostile" in inc_type or "insider" in inc_type:
            classification = "Physical Safety & Insider Threat - Hostile Language / Violence Threat Alert"
            root_cause = "Direct threat to life, workplace hostility, or malicious insider intent detected in user communications."
            indicators = [
                f"Hostile / harmful statement flagged: '{desc[:70]}...'",
                f"Originating identity '{user}' on system/channel {system}",
                f"Source IP / Location: {ip}"
            ]
            investigation_steps = [
                f"Preserve complete unedited transcript, chat logs, or email headers for '{user}'",
                "Verify real-time physical safety of target personnel and secure facility access",
                "Cross-reference source IP and user badge access logs for physical location tracking",
                "Notify Corporate Physical Security, HR Employee Relations, and Legal Counsel immediately"
            ]
            if has_memory and top_mem:
                recs = [
                    f"Immediately restrict digital and physical facility badge access for {user}",
                    "Initiate priority workplace safety and threat management escalation protocol",
                    f"Preserve all device forensic images and communication history (proven in {top_mem.get('id', 'HIST-001')})",
                    "Conduct urgent out-of-band safety check with reported victim"
                ]
                reason = f"Previous incident {top_mem.get('id')} demonstrated that rapid physical badge suspension and law enforcement/HR escalation mitigated workplace threats immediately."
                evidence = f"In historical incident '{top_mem.get('title')}' ({top_mem.get('id')}), early physical and digital isolation prevented physical harm and insider sabotage."
            else:
                recs = [
                    f"Temporarily suspend active accounts and facility access for {user}",
                    "Notify Emergency Response and Physical Security Leads immediately",
                    "Preserve all forensic communication evidence"
                ]
                reason = "Mandatory safety protocol for credible threats of violence or hostility."
                evidence = "Standard Workplace Violence & Physical Threat Incident Playbook."

            prevention = [
                "Implement automated DLP and communication monitoring for threat-to-life keywords",
                "Provide annual workplace violence prevention and anonymous whistleblower channels",
                "Integrate HR alerting with physical badge and SSO automated deprovisioning"
            ]

        elif "brute" in inc_type or "ssh" in title or "auth" in inc_type:
            classification = "Credential Access - Automated Brute Force & Password Spraying (T1110)"
            root_cause = "Directly exposed authentication port with legacy password authentication or unthrottled login endpoint."
            indicators = [
                f"High-frequency failed authentication attempts from source IP {ip}",
                f"Targeting service account '{user}' on {system}",
                "Absence of progressive exponential backoff on auth endpoint"
            ]
            investigation_steps = [
                f"Inspect SSH/auth logs on {system} to verify if any login attempts succeeded from {ip}",
                f"Check GeoIP and Threat Intelligence reputation scores for source IP {ip}",
                f"Verify if account '{user}' has multifactor authentication (MFA) actively enforced",
                "Audit PAM and firewall fail2ban delay configurations on the target host"
            ]
            
            if has_memory and top_mem:
                recs = [
                    f"Block malicious IP {ip} at perimeter WAF / Security Group immediately",
                    f"Enforce SSH key-only authentication and disable password login on {system}",
                    f"Restrict port 22/ingress to internal VPN CIDR (proven in {top_mem.get('id', 'historical incident')})",
                    f"Force immediate credential rotation for account '{user}'"
                ]
                reason = f"Historical incident {top_mem.get('id')} demonstrated that restricting ingress to VPN CIDR and disabling password auth eliminated brute-force surface permanently."
                evidence = f"In previous incident '{top_mem.get('title')}' ({top_mem.get('id')}), applying fail2ban and key-only auth resolved the breach with 0 unauthorized access."
            else:
                recs = [
                    f"Temporarily block IP {ip} at edge firewall",
                    f"Reset password for username '{user}'",
                    "Enable rate limiting on login endpoint"
                ]
                reason = "Standard mitigation procedure for high-volume automated login attacks."
                evidence = "Standard SOC baseline playbook (No previous organizational memory matched)."

            prevention = [
                "Implement automated AWS Config / Cloud Custodian rule to auto-remediate 0.0.0.0/0 on port 22",
                "Deploy Cloudflare / AWS WAF rate-limiting rule on authentication gateways",
                "Enforce FIDO2 / hardware MFA for all administrative and service accounts"
            ]

        elif "phish" in inc_type or "oauth" in title.lower() or "consent" in inc_type:
            classification = "Initial Access - Illicit OAuth Consent Grant / Spear Phishing (T1566 / T1528)"
            root_cause = "Default tenant policy allowing non-admin users to authorize unverified third-party OAuth enterprise applications."
            indicators = [
                f"UserConsent granted to high-privilege scopes (Mail.ReadWrite, User.Read) by {user}",
                f"Suspicious OAuth callback redirect detected from IP {ip}",
                "Anomalous automated mail forwarding rule created post-consent"
            ]
            investigation_steps = [
                f"Audit Entra ID / Google Workspace audit logs for OAuth grants created by {user}",
                "Inspect user inbox for hidden forwarding or deletion rules",
                "Check token issuance timeline and all recent API calls made by the client app ID",
                "Review active user sessions and recent IP logins across Microsoft 365 / Google Workspace"
            ]
            if has_memory and top_mem:
                recs = [
                    "Immediately revoke rogue OAuth enterprise application permissions and client tokens",
                    f"Terminate all active session cookies and refresh tokens for user {user}",
                    "Delete all unauthorized inbox forwarding/inbox manipulation rules",
                    "Change tenant settings to require Admin Consent for all third-party integrations"
                ]
                reason = f"Based on organizational resolution in {top_mem.get('id')}, revoking OAuth tokens and disabling self-service consent halts ongoing tenant compromise."
                evidence = f"Historical memory from {top_mem.get('id')} confirmed that disabling user consent policy eliminated recurring spear-phishing vulnerability."
            else:
                recs = [
                    "Revoke suspicious OAuth application grant",
                    f"Reset credentials for {user}",
                    "Audit user mail forwarding rules"
                ]
                reason = "Standard containment steps for compromised cloud accounts."
                evidence = "General cybersecurity best practices (No organization-specific Hindsight match)."

            prevention = [
                "Enforce tenant-wide policy requiring administrator approval for third-party OAuth apps",
                "Implement conditional access policies blocking risky cloud logins",
                "Conduct regular automated OAuth application permission audits"
            ]
        else:
            classification = f"Threat Activity - {inc.get('type', 'General Security Anomaly')}"
            root_cause = "Potential misconfiguration, credential exposure, or perimeter control gap."
            indicators = [
                f"Unusual activity telemetry detected on {system}",
                f"Traffic originating from IP {ip} involving user {user}",
                "Alert thresholds exceeded in telemetry logs"
            ]
            investigation_steps = [
                f"Isolate affected host or service {system} from network segment",
                f"Review authorization and access logs for user '{user}'",
                "Collect volatile memory and process execution telemetry for forensic analysis",
                "Cross-reference source indicators with threat intelligence databases"
            ]
            recs = [
                f"Quarantine impacted resource {system}",
                f"Invalidate active access credentials for {user}",
                f"Block source IP {ip} at network perimeter"
            ]
            reason = "Standard defense-in-depth isolation procedure."
            evidence = f"Matches organizational memory from {top_mem.get('id')}" if has_memory and top_mem else "Standard incident response protocol."
            prevention = [
                "Implement continuous posture monitoring and automated drift detection",
                "Strengthen endpoint telemetry and zero-trust authentication policies"
            ]

        return {
            "incident_classification": classification,
            "severity_assessment": ai_severity,
            "explanation": f"Automated analysis of {inc.get('title')} targeting {system}. " + (
                f"Cross-referenced with Hindsight organizational memory." if has_memory else "Analyzed without prior incident context."
            ),
            "possible_root_cause": root_cause,
            "indicators": indicators,
            "investigation_steps": investigation_steps,
            "recommended_response": recs,
            "reason_for_recommendation": reason,
            "historical_evidence": evidence,
            "prevention_suggestions": prevention
        }

ai_service = AIService()
