#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"

DIMENSIONS = [
    "source_verified",
    "blueprint_verified",
    "question_quality_verified",
    "correct_answer_verified",
    "distractors_verified",
    "explanation_verified",
    "currentness_verified",
    "independent_qa_passed",
    "no_unresolved_conflict",
]


def ensure_schema(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS question_final_gate(
          question_uid TEXT PRIMARY KEY,
          audit_date TEXT NOT NULL,
          auditor TEXT NOT NULL,
          source_locator TEXT NOT NULL,
          source_version TEXT NOT NULL,
          source_verified INTEGER NOT NULL,
          blueprint_verified INTEGER NOT NULL,
          question_quality_verified INTEGER NOT NULL,
          correct_answer_verified INTEGER NOT NULL,
          distractors_verified INTEGER NOT NULL,
          explanation_verified INTEGER NOT NULL,
          currentness_verified INTEGER NOT NULL,
          independent_qa_passed INTEGER NOT NULL,
          no_unresolved_conflict INTEGER NOT NULL,
          option_length_metrics_json TEXT NOT NULL,
          rejection_reason TEXT,
          final_status TEXT NOT NULL,
          FOREIGN KEY(question_uid) REFERENCES questions(question_uid)
        )
        """
    )


def option_metrics(item_data_json: str, correct_answer_json: str) -> str:
    try:
        data = json.loads(item_data_json)
        answer = json.loads(correct_answer_json)
        options = data.get("options", {})
        key = answer.get("correct_option")
        if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"}:
            return json.dumps({"status": "NOT_APPLICABLE_OR_INVALID_MC_SCHEMA"}, sort_keys=True)
        lengths = {k: len(str(v).strip()) for k, v in options.items()}
        mn = min(lengths.values())
        mx = max(lengths.values())
        return json.dumps(
            {
                "characters": lengths,
                "max_min_ratio": round(mx / max(mn, 1), 3),
                "correct_option": key,
                "correct_length_rank": sorted(lengths, key=lengths.get).index(key) + 1 if key in lengths else None,
            },
            sort_keys=True,
        )
    except Exception as exc:
        return json.dumps({"status": "METRICS_ERROR", "error": str(exc)}, sort_keys=True)


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"Missing master database: {DB.name}")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    ensure_schema(con)
    now = datetime.now(timezone.utc).isoformat()

    verified = con.execute(
        """
        SELECT question_uid, item_data_json, correct_answer_json, source_detail
        FROM questions
        WHERE clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%'
        ORDER BY question_uid
        """
    ).fetchall()

    created = 0
    for q in verified:
        existing = con.execute(
            "SELECT final_status FROM question_final_gate WHERE question_uid=?",
            (q["question_uid"],),
        ).fetchone()
        if existing:
            continue

        con.execute(
            """
            INSERT INTO question_final_gate(
              question_uid,audit_date,auditor,source_locator,source_version,
              source_verified,blueprint_verified,question_quality_verified,
              correct_answer_verified,distractors_verified,explanation_verified,
              currentness_verified,independent_qa_passed,no_unresolved_conflict,
              option_length_metrics_json,rejection_reason,final_status
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                q["question_uid"],
                now,
                "PENDING_INDEPENDENT_FINAL_QA",
                (q["source_detail"] or "").strip(),
                "PENDING_EXACT_VERSION_CONFIRMATION",
                1,  # Source verification was already completed in the source-audit workflow.
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                option_metrics(q["item_data_json"], q["correct_answer_json"]),
                "PENDING_STRICT_11_DIMENSION_FINAL_QA",
                "FINAL_QA_PENDING",
            ),
        )
        created += 1

    con.execute(
        """
        UPDATE questions
        SET commercial_release_ready=0
        WHERE question_uid IN (
          SELECT question_uid FROM question_final_gate
          WHERE final_status <> 'FINAL_QA_PASS'
        )
        """
    )

    total_verified = len(verified)
    total_records = con.execute(
        """
        SELECT COUNT(*) FROM question_final_gate
        WHERE question_uid IN (
          SELECT question_uid FROM questions
          WHERE clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%'
        )
        """
    ).fetchone()[0]
    passed = con.execute(
        "SELECT COUNT(*) FROM question_final_gate WHERE final_status='FINAL_QA_PASS'"
    ).fetchone()[0]
    pending = con.execute(
        "SELECT COUNT(*) FROM question_final_gate WHERE final_status='FINAL_QA_PENDING'"
    ).fetchone()[0]

    if total_records != total_verified:
        con.rollback()
        raise SystemExit(
            f"Strict-gate coverage mismatch: verified={total_verified}, records={total_records}"
        )

    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
        ("strict_final_gate_policy", "REQUIRED_11_DIMENSIONS_FOR_EVERY_QUESTION"),
    )
    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
        ("strict_final_gate_coverage", f"records={total_records};passed={passed};pending={pending}"),
    )
    con.commit()
    con.close()

    print(
        f"Strict 11-dimension gate enforced: verified={total_verified}, "
        f"records={total_records}, passed={passed}, pending={pending}, created={created}"
    )


if __name__ == "__main__":
    main()
