# ⚡ INCIDENT RESPONSE AGENT
### *AI-Powered Cybersecurity Incident Response Agent with Hindsight Persistent Memory*

---

## 🏆 Project Highlights
- **Hackathon Track**: *AI Agents That Learn Using Hindsight*
- **Problem Statement**: Incident Response Agent
- **Core Innovation**: Persistent Organizational Memory for SOC Incident Triage and Post-Mortems using **Vectorize Hindsight**.
- **Safety Compliance**: 100% Defensive cybersecurity architecture. Uses synthetic incident telemetry and strictly enforces **Human-in-the-Loop approval** for all remediation actions.

---

## 🎯 Project Objective
During critical production and cybersecurity incidents, every minute counts. Traditional AI triage systems are **stateless** — they forget past breaches, runbooks that worked, recurring root causes, and analyst feedback.

| Why Memory Matters | Business Case |
| :--- | :--- |
| Remembers past incidents, their root causes, resolution steps, and which runbooks worked. Learns from post-mortems to suggest faster fixes for similar issues. | When production is down, every minute counts. An agent that recalls exactly how similar incidents were resolved before is invaluable. |

**Incident Response Agent** transforms incident response by integrating **Hindsight persistent memory**:
1. **Memory Ingestion**: Whenever an incident is resolved, its root cause, investigation steps, resolution actions, lessons learned, and analyst feedback are persisted into Hindsight.
2. **Context-Aware Recall**: When a new incident occurs, Incident Response Agent searches Hindsight for similar historical attacks.
3. **Memory-Aware Triage**: It synthesizes incoming telemetry with historical post-mortems to produce high-confidence investigation steps, root-cause assessments, and containment actions citing past evidence.
4. **Human-in-the-Loop Approval**: Defensively requires SOC analyst review before finalizing resolutions.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **📊 SOC Command Dashboard** | Real-time metrics (Total, Open, Resolved, High/Med/Low severity), MITRE-aligned category distribution, and interactive 7-day threat trend chart via Chart.js. |
| **🚨 Incident Intake & Telemetry** | Intake form capturing title, attack type, severity, affected assets, attacker IPs, affected usernames, timestamps, and raw syslog/EDR/CloudTrail logs. |
| **🧠 Hindsight Persistent Memory** | Official integration with **Vectorize Hindsight** storing post-mortems, investigation playbooks, and resolution techniques across 9 core fields. |
| **🔍 Memory-Aware AI Analysis** | LLM-driven structured triage returning classification, root cause, indicators, investigation steps, prevention suggestions, and **historical evidence citations**. |
| **🛡️ Human-in-the-Loop Controls** | Approve/Reject action plan controls with audit trail logging and resolution finalization modal. |
| **🔍 Organizational Security Memory** | Natural-language query portal (`/memory`) enabling analysts to ask questions like *"How did we resolve the previous brute-force attack?"*. |
| **📄 Post-Mortem Reports & Export** | Executive and technical incident post-mortem documentation generator with Print/PDF and JSON export capabilities. |

---

## 🛠️ Technology Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Persistent AI Memory**: [Vectorize Hindsight](https://hindsight.vectorize.io/) (Hindsight Cloud & Local Synced Bank)
- **AI / LLM Engine**: Groq (Llama 3.3 70B Versatile) / OpenAI compatible
- **Frontend**: Vanilla HTML5, High-Tech Cyber CSS3, Vanilla JavaScript, Chart.js
- **Relational Database**: SQLite3 ACID Relational Engine (`data/incidents.db`) with automatic JSON backup sync (`data/incidents.json`)

---

## 🏗️ Architecture & Memory Flow

```
+-------------------------------------------------------------+
|                Incoming Incident Telemetry                  |
|          (Syslog, GuardDuty, Falco, Auth Logs)              |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|            FastAPI Backend & Incident Service               |
+-------------------------------------------------------------+
            |                                   |
            v                                   v
+-----------------------+           +-----------------------+
|  Hindsight Memory     |           |     LLM AI Engine     |
|  Vectorize Bank       |           |   (Groq / Llama-3.3)  |
|  - Semantic Recall    |           |   - Threat Triage     |
|  - Past Post-Mortems  |           |   - Root Cause Pred.  |
+-----------------------+           +-----------------------+
            \                                   /
             \---> [ Memory-Aware Synthesis ] <---/
                              |
                              v
+-------------------------------------------------------------+
|    Structured Response Plan & Historical Evidence Match     |
|        (e.g., "98% Match to INC-2026-0812 Bastion Fix")      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               Human-in-the-Loop SOC Analyst                 |
|             [ Approve ] [ Reject ] [ Resolve ]              |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|     Resolution & Lessons Learned Persisted to Hindsight     |
+-------------------------------------------------------------+
```

---

## ⚡ Quick Start & Installation

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-org/sentinelmind.git
cd sentinelmind
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configure your API keys in `.env`:
```env
HOST=127.0.0.1
PORT=5000

# Hindsight Vectorize API (https://ui.hindsight.vectorize.io) - Promo: MEMHACK99
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=sentinelmind-soc-bank

# LLM API (https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
```
*(Note: If API keys are omitted, Incident Response Agent runs in High-Fidelity Synthetic Local Mode for seamless offline demos).*

### 3. Run Application
```powershell
python run.py
```

Open your browser at:
- **SOC Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)
- **Incident Intake**: [http://127.0.0.1:5000/incident](http://127.0.0.1:5000/incident)
- **Security Memory**: [http://127.0.0.1:5000/memory](http://127.0.0.1:5000/memory)
- **Post-Mortems**: [http://127.0.0.1:5000/reports](http://127.0.0.1:5000/reports)
- **Swagger API Docs**: [http://127.0.0.1:5000/api/docs](http://127.0.0.1:5000/api/docs)

---

## 🎬 Demonstration Workflow

### Step 1: Baseline Historical Memory
1. Visit `/memory` or `/dashboard`.
2. Inspect incident `#INC-2026-0812` (*"Distributed SSH Brute-Force Attack on Auth Gateway"*).
3. Notice its recorded root cause (*Exposed port 22 with legacy password auth*) and successful resolution (*Enforced SSH key-only auth and restricted port 22 to VPN CIDR*).

### Step 2: Ingest a New Incident
1. Go to `/incident`.
2. Click the preset: **`🎯 SSH Brute-Force Attack`**.
3. Click **`⚡ Analyze Incident (AI + Hindsight)`**.

### Step 3: Observe Memory-Aware AI Investigation
- The Agent automatically recalls `#INC-2026-0812` from Hindsight with a **98% Similarity Score**.
- Under **Rationale & Historical Evidence**, Incident Response Agent explicitly explains:
  > *"Historical incident INC-2026-0812 demonstrated that restricting ingress to VPN CIDR and disabling password auth eliminated brute-force surface permanently."*
- Click **`✓ Approve Recommendation`** to log analyst authorization.
- Click **`✓ Mark Resolved & Store in Hindsight`** to save new lessons learned.

---

## 🔒 Safety & Ethical Guidelines
Incident Response Agent is built strictly for **defensive cybersecurity operations**:
- **Synthetic Data**: All incident logs, IPs, and usernames are synthetic demonstrations.
- **No Active Exploitation**: The agent does not scan networks, exploit vulnerabilities, or perform offensive attacks.
- **Human-in-the-Loop**: No firewall changes or credential resets are performed autonomously without explicit analyst approval.

---

## 📜 License
MIT License. Built for the Microsoft / Vectorize AI Agents Hackathon.
