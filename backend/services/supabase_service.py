"""
Supabase Cloud Database Service for Incident Response Agent
Provides real-time cloud synchronization to Supabase Table Editor.
"""

import os
import json
import httpx
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class SupabaseService:
    def __init__(self):
        self.project_ref = os.getenv("SUPABASE_PROJECT_REF", "bwfrhkmtvmqadcrcvduje")
        self.api_url = os.getenv("SUPABASE_URL", f"https://{self.project_ref}.supabase.co").rstrip("/")
        self.api_key = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
        self.table_name = os.getenv("SUPABASE_TABLE_NAME", "M SRI HARI SAI ESWAR")

    @property
    def is_configured(self) -> bool:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        self.api_key = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
        return bool(self.api_key)

    async def sync_all_incidents(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pushes and upserts all local incidents directly to Supabase table.
        """
        if not self.is_configured:
            return {"status": "skipped", "message": "SUPABASE_KEY not set in .env"}

        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        # Prepare payload formatted for Supabase
        records = []
        for inc in incidents:
            records.append({
                "id": inc.get("id"),
                "title": inc.get("title"),
                "type": inc.get("type"),
                "severity": inc.get("severity"),
                "status": inc.get("status"),
                "description": inc.get("description"),
                "source_ip": inc.get("source_ip"),
                "username": inc.get("username"),
                "affected_system": inc.get("affected_system"),
                "root_cause": inc.get("root_cause"),
                "investigation_process": inc.get("investigation_process"),
                "actions_taken": inc.get("actions_taken"),
                "successful_resolution": inc.get("successful_resolution"),
                "lessons_learned": inc.get("lessons_learned"),
                "analyst_feedback": inc.get("analyst_feedback"),
                "created_at": inc.get("created_at")
            })

        target_tables = [self.table_name, "incidents"]
        success_table = None
        last_error = None

        async with httpx.AsyncClient(timeout=15.0) as client:
            for tbl in target_tables:
                try:
                    url = f"{self.api_url}/rest/v1/{tbl}"
                    res = await client.post(url, headers=headers, json=records)
                    if res.status_code in [200, 201]:
                        success_table = tbl
                        break
                    else:
                        last_error = f"HTTP {res.status_code}: {res.text[:150]}"
                except Exception as e:
                    last_error = str(e)

        if success_table:
            return {"status": "success", "table": success_table, "synced_count": len(records)}
        else:
            return {"status": "error", "message": last_error}

    async def upsert_single_incident(self, inc: Dict[str, Any]) -> bool:
        """Upserts a single incident record to Supabase in real-time."""
        if not self.is_configured:
            return False

        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        payload = {
            "id": inc.get("id"),
            "title": inc.get("title"),
            "type": inc.get("type"),
            "severity": inc.get("severity"),
            "status": inc.get("status"),
            "description": inc.get("description"),
            "source_ip": inc.get("source_ip"),
            "username": inc.get("username"),
            "affected_system": inc.get("affected_system"),
            "root_cause": inc.get("root_cause"),
            "investigation_process": inc.get("investigation_process"),
            "actions_taken": inc.get("actions_taken"),
            "successful_resolution": inc.get("successful_resolution"),
            "lessons_learned": inc.get("lessons_learned"),
            "analyst_feedback": inc.get("analyst_feedback"),
            "created_at": inc.get("created_at")
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                url = f"{self.api_url}/rest/v1/{self.table_name}"
                res = await client.post(url, headers=headers, json=[payload])
                return res.status_code in [200, 201]
            except Exception as e:
                print(f"[!] Supabase single sync error: {e}")
                return False

supabase_service = SupabaseService()
