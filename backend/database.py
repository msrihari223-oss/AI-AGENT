"""
Incident Response Agent - SQLite Relational Database Engine
Provides ACID persistent storage for incidents, AI triages, and SOC audit trails.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "incidents.db"
JSON_BACKUP_PATH = Path(__file__).resolve().parent.parent / "data" / "incidents.json"

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and performs auto-migration from existing JSON."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                source_ip TEXT,
                username TEXT,
                affected_system TEXT,
                additional_logs TEXT,
                timestamp TEXT,
                root_cause TEXT,
                investigation_process TEXT,
                actions_taken TEXT,
                successful_resolution TEXT,
                analyst_feedback TEXT,
                lessons_learned TEXT,
                created_at TEXT,
                resolved_at TEXT,
                ai_analysis TEXT,
                hindsight_memory_id TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "M SRI HARI SAI ESWAR" (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                source_ip TEXT,
                username TEXT,
                affected_system TEXT,
                additional_logs TEXT,
                timestamp TEXT,
                root_cause TEXT,
                investigation_process TEXT,
                actions_taken TEXT,
                successful_resolution TEXT,
                analyst_feedback TEXT,
                lessons_learned TEXT,
                created_at TEXT,
                resolved_at TEXT,
                ai_analysis TEXT,
                hindsight_memory_id TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Check if table is empty; if so, populate from JSON backup
        cursor.execute("SELECT COUNT(*) FROM incidents")
        count = cursor.fetchone()[0]
        if count == 0 and JSON_BACKUP_PATH.exists():
            try:
                with open(JSON_BACKUP_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    incidents = data.get("incidents", [])
                    for inc in incidents:
                        insert_incident_row(cursor, inc)
                conn.commit()
                print(f"[+] SQLite Database: Successfully migrated {len(incidents)} incidents into {DB_PATH.name}")
            except Exception as e:
                print(f"[!] Warning migrating JSON to SQLite: {e}")

def insert_incident_row(cursor: sqlite3.Cursor, inc: Dict[str, Any]):
    """Helper to insert an incident dict into SQLite."""
    ai_str = json.dumps(inc.get("ai_analysis")) if isinstance(inc.get("ai_analysis"), dict) else inc.get("ai_analysis")
    params = (
        inc.get("id"),
        inc.get("title"),
        inc.get("type"),
        inc.get("severity", "HIGH"),
        inc.get("status", "OPEN"),
        inc.get("description"),
        inc.get("source_ip"),
        inc.get("username"),
        inc.get("affected_system"),
        inc.get("additional_logs"),
        inc.get("timestamp"),
        inc.get("root_cause"),
        inc.get("investigation_process"),
        inc.get("actions_taken"),
        inc.get("successful_resolution"),
        inc.get("analyst_feedback"),
        inc.get("lessons_learned"),
        inc.get("created_at"),
        inc.get("resolved_at"),
        ai_str,
        inc.get("hindsight_memory_id")
    )
    cursor.execute("""
        INSERT OR REPLACE INTO incidents (
            id, title, type, severity, status, description, source_ip, username,
            affected_system, additional_logs, timestamp, root_cause,
            investigation_process, actions_taken, successful_resolution,
            analyst_feedback, lessons_learned, created_at, resolved_at,
            ai_analysis, hindsight_memory_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, params)
    cursor.execute("""
        INSERT OR REPLACE INTO "M SRI HARI SAI ESWAR" (
            id, title, type, severity, status, description, source_ip, username,
            affected_system, additional_logs, timestamp, root_cause,
            investigation_process, actions_taken, successful_resolution,
            analyst_feedback, lessons_learned, created_at, resolved_at,
            ai_analysis, hindsight_memory_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, params)

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a SQLite row into an incident dictionary."""
    d = dict(row)
    if d.get("ai_analysis") and isinstance(d["ai_analysis"], str):
        try:
            d["ai_analysis"] = json.loads(d["ai_analysis"])
        except Exception:
            pass
    return d

def db_get_all(status: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all incidents filtered by optional status and severity."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        if status:
            query += " AND UPPER(status) = ?"
            params.append(status.upper())
        if severity:
            query += " AND UPPER(severity) = ?"
            params.append(severity.upper())
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]

def db_get_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single incident by ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None

def db_save_incident(inc: Dict[str, Any]):
    """Saves or updates an incident in the database."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        insert_incident_row(cursor, inc)
        conn.commit()

def db_get_stats() -> Dict[str, Any]:
    """Returns database telemetry and health stats."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status IN ('OPEN', 'INVESTIGATING')")
        open_cnt = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'RESOLVED'")
        res_cnt = cursor.fetchone()[0]
        return {
            "database_type": "SQLite3 (Relational Persistent DB)",
            "db_path": str(DB_PATH),
            "file_size_bytes": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
            "total_records": total,
            "open_records": open_cnt,
            "resolved_records": res_cnt
        }

# Run initialization on import
init_db()
