"""
Creates and populates table 'M SRI HARI SAI ESWAR' in SQLite database
and exports CSV and SQL scripts for instant Supabase import.
"""

import sqlite3
import csv
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "incidents.db"
CSV_PATH = Path(__file__).resolve().parent / "data" / "M_SRI_HARI_SAI_ESWAR.csv"
SQL_PATH = Path(__file__).resolve().parent / "data" / "M_SRI_HARI_SAI_ESWAR.sql"

def setup_table_and_exports():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Create table "M SRI HARI SAI ESWAR" in SQLite
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
    
    # 2. Copy all data from incidents into "M SRI HARI SAI ESWAR"
    cursor.execute('DELETE FROM "M SRI HARI SAI ESWAR"')
    cursor.execute("""
        INSERT INTO "M SRI HARI SAI ESWAR"
        SELECT * FROM incidents
    """)
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM "M SRI HARI SAI ESWAR"')
    count = cursor.fetchone()[0]
    print(f"[+] SQLite: Created & populated table 'M SRI HARI SAI ESWAR' with {count} records!")
    
    # 3. Export to CSV for 1-click Drag & Drop in Supabase Table Editor
    cursor.execute('SELECT * FROM "M SRI HARI SAI ESWAR"')
    rows = cursor.fetchall()
    if rows:
        headers = rows[0].keys()
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in rows:
                writer.writerow([r[k] for k in headers])
        print(f"[+] CSV Export: Saved {CSV_PATH.name} ({len(rows)} rows) for Supabase Drag & Drop!")
        
    # 4. Generate SQL Script for Supabase SQL Editor
    with open(SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- SQL script to create and populate 'M SRI HARI SAI ESWAR' in Supabase\n")
        f.write('DROP TABLE IF EXISTS "M SRI HARI SAI ESWAR";\n')
        f.write('CREATE TABLE "M SRI HARI SAI ESWAR" (\n')
        f.write('    id TEXT PRIMARY KEY,\n')
        f.write('    title TEXT NOT NULL,\n')
        f.write('    type TEXT,\n')
        f.write('    severity TEXT,\n')
        f.write('    status TEXT,\n')
        f.write('    description TEXT,\n')
        f.write('    source_ip TEXT,\n')
        f.write('    username TEXT,\n')
        f.write('    affected_system TEXT,\n')
        f.write('    additional_logs TEXT,\n')
        f.write('    timestamp TEXT,\n')
        f.write('    root_cause TEXT,\n')
        f.write('    investigation_process TEXT,\n')
        f.write('    actions_taken TEXT,\n')
        f.write('    successful_resolution TEXT,\n')
        f.write('    analyst_feedback TEXT,\n')
        f.write('    lessons_learned TEXT,\n')
        f.write('    created_at TEXT,\n')
        f.write('    resolved_at TEXT,\n')
        f.write('    ai_analysis TEXT,\n')
        f.write('    hindsight_memory_id TEXT\n')
        f.write(');\n\n')
        
        for r in rows:
            cols = [f'"{k}"' for k in headers]
            vals = []
            for k in headers:
                val = r[k]
                if val is None:
                    vals.append("NULL")
                else:
                    safe_val = str(val).replace("'", "''")
                    vals.append(f"'{safe_val}'")
            f.write(f'INSERT INTO "M SRI HARI SAI ESWAR" ({", ".join(cols)}) VALUES ({", ".join(vals)});\n')
            
    print(f"[+] SQL Script: Generated {SQL_PATH.name} with full CREATE TABLE & INSERT statements!")
    conn.close()

if __name__ == "__main__":
    setup_table_and_exports()
