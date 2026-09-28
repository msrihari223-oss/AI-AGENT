import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY", "")
url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").rstrip("/")
bank_id = os.getenv("HINDSIGHT_BANK_ID", "sentinelmind-soc-bank")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data_file = Path(__file__).resolve().parent / "data" / "incidents.json"
if data_file.exists():
    with open(data_file, "r", encoding="utf-8") as f:
        incidents = json.load(f).get("incidents", [])

    resolved = [inc for inc in incidents if inc.get("status") == "RESOLVED" and inc.get("root_cause")]
    print(f"[*] Found {len(resolved)} resolved incidents.")

    items = []
    for inc in resolved:
        content = (
            f"Incident {inc['id']}: {inc['title']}. Type: {inc['type']}. "
            f"Description: {inc['description']}. Root Cause: {inc['root_cause']}. "
            f"Investigation Steps: {inc.get('investigation_process', 'Standard forensic triage')}. "
            f"Actions Taken: {inc.get('actions_taken', '')}. "
            f"Successful Resolution: {inc.get('successful_resolution', '')}. "
            f"Lessons Learned: {inc.get('lessons_learned', '')}."
        )
        items.append({
            "content": content,
            "context": f"cybersecurity_incident_{inc['type']}",
            "document_id": inc["id"]
        })

    import time
    success_count = 0
    # Send in chunks of 4 to prevent server deadlock
    chunk_size = 4
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i+chunk_size]
        try:
            response = httpx.post(
                f"{url}/v1/default/banks/{bank_id}/memories",
                headers=headers,
                json={"items": chunk},
                timeout=30.0
            )
            if response.status_code in [200, 201]:
                success_count += len(chunk)
                print(f"[+] Synced chunk {i//chunk_size + 1}: {len(chunk)} memories (Status {response.status_code})")
            else:
                print(f"[!] Warning chunk {i//chunk_size + 1} status {response.status_code}: {response.text[:120]}")
            time.sleep(0.4)
        except Exception as e:
            print(f"[-] Error on chunk {i}: {e}")
            time.sleep(0.5)

    print(f"\n[+] Total {success_count}/{len(items)} memories successfully synced to Hindsight bank '{bank_id}'!")
