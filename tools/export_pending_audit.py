#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
OUT = ROOT / "data" / "pending_audit_next.json"
START = 52
END = 101

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = con.execute(
    """
    SELECT question_uid, source_id, client_need, difficulty, stem,
           item_data_json, correct_answer_json, rationale,
           source_name, source_detail, source_url, clinical_qa_status
    FROM questions
    WHERE source_bank='v2'
      AND source_id BETWEEN ? AND ?
      AND clinical_qa_status NOT LIKE 'SOURCE_VERIFIED_2026_%'
    ORDER BY source_id
    """,
    (START, END),
).fetchall()
con.close()

payload = {
    "range": [START, END],
    "count": len(rows),
    "questions": [dict(row) for row in rows],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Exported {len(rows)} pending questions to {OUT.name}")
