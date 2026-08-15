#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
OUT = ROOT / "data" / "pending_audit_next.json"
MIN_SOURCE_ID = 1
BATCH_SIZE = 50

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = con.execute(
    """
    SELECT q.question_uid, q.source_id, q.client_need, q.difficulty, q.stem,
           q.item_data_json, q.correct_answer_json, q.rationale,
           q.source_name, q.source_detail, q.source_url, q.clinical_qa_status
    FROM questions q
    WHERE q.source_bank='v2'
      AND q.source_id >= ?
      AND NOT EXISTS (
          SELECT 1
          FROM rule1_manual_audit r
          WHERE r.question_uid=q.question_uid
            AND r.criteria_passed_count=11
            AND r.second_pass='PASS'
            AND r.final_disposition='FINAL_QA_PASS'
      )
    ORDER BY q.source_id
    LIMIT ?
    """,
    (MIN_SOURCE_ID, BATCH_SIZE),
).fetchall()
con.close()

if rows:
    source_range = [rows[0]["source_id"], rows[-1]["source_id"]]
else:
    source_range = []

payload = {
    "selection_rule": "chronological_v2_items_without_completed_rule1_manual_11of11_second_pass",
    "range": source_range,
    "count": len(rows),
    "questions": [dict(row) for row in rows],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Exported {len(rows)} chronological Rule 1 pending questions to {OUT.name}; range={source_range}")
