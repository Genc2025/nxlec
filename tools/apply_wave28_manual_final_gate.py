#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
MANIFEST = ROOT / "data" / "manual_final_qa_wave28_0632_0681.json"
REPORT = ROOT / "FINAL_QA_WAVE28_Q0632_Q0681_MANUAL_10OF10.md"
EXPECTED_IDS = [f"V2-Q{i:04d}" for i in range(632, 682)]
SEMANTIC_DIMS = [
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


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    if not DB.exists():
        fail("Master database does not exist")
    if not MANIFEST.exists():
        fail("Wave 28 manual QA manifest does not exist")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = manifest.get("items", [])
    ids = [item.get("question_uid") for item in items]
    if ids != EXPECTED_IDS or len(items) != 50:
        fail("Wave 28 manual manifest scope mismatch")
    for item in items:
        uid = item.get("question_uid")
        if item.get("manual_disposition") != "PASS":
            fail(f"Manual disposition is not PASS for {uid}")
        if item.get("all_11_dimensions") is not True:
            fail(f"All 11 dimensions not verified for {uid}")
        if item.get("second_pass_verified") is not True:
            fail(f"Second-pass QA missing for {uid}")
        if not str(item.get("source_locator") or "").strip():
            fail(f"Source locator evidence missing for {uid}")
        if not str(item.get("source_url") or "").startswith("https://"):
            fail(f"Source URL evidence missing for {uid}")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    table = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='question_final_gate'"
    ).fetchone()
    if not table:
        fail("question_final_gate table is missing")

    now = datetime.now(timezone.utc).isoformat()
    ratios: list[float] = []
    deviations: list[float] = []
    required_flags = {
        "MANUAL_ITEM_BY_ITEM_AUDIT",
        "SOURCE_CURRENTNESS_CHECKED",
        "KEY_VERIFIED",
        "DISTRACTORS_REVIEWED",
        "RATIONALE_VERIFIED",
        "AMBIGUITY_REVIEWED",
        "SECOND_PASS_MANUAL_QA",
    }

    for item in items:
        uid = item["question_uid"]
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if not q:
            fail(f"Missing question: {uid}")
        if q["clinical_qa_status"] != "SOURCE_VERIFIED_2026_WAVE28_ITEM_BY_ITEM":
            fail(f"Unexpected QA status for {uid}: {q['clinical_qa_status']}")

        flags = set(json.loads(q["editorial_flags_json"] or "[]"))
        if not required_flags.issubset(flags):
            fail(f"Missing manual audit evidence flags for {uid}")

        for field in ("stem", "rationale", "source_name", "source_detail", "source_url"):
            if not str(q[field] or "").strip():
                fail(f"Missing {field} for {uid}")
        if q["source_url"] != item["source_url"] or q["source_detail"] != item["source_locator"]:
            fail(f"Persisted source provenance mismatch for {uid}")

        data = json.loads(q["item_data_json"])
        answer = json.loads(q["correct_answer_json"])
        options = data.get("options", {})
        key = answer.get("correct_option")
        if set(options) != {"A", "B", "C", "D"} or key not in options:
            fail(f"Invalid option/key structure for {uid}")
        normalized = [str(options[k]).strip().casefold() for k in "ABCD"]
        if any(not value for value in normalized) or len(set(normalized)) != 4:
            fail(f"Blank or duplicate option for {uid}")

        qc = con.execute("SELECT * FROM option_length_qc WHERE question_uid=?", (uid,)).fetchone()
        if not qc or qc["qc_status"] != "PASS":
            fail(f"Option QC record missing or not PASS for {uid}")

        lengths = {k: len(str(options[k]).strip()) for k in "ABCD"}
        minimum = min(lengths.values())
        maximum = max(lengths.values())
        ratio = maximum / max(minimum, 1)
        distractor_mean = sum(v for k, v in lengths.items() if k != key) / 3
        deviation = abs(lengths[key] - distractor_mean) / max(distractor_mean, 1)
        ratios.append(ratio)
        deviations.append(deviation)
        if ratio > 1.15 + 1e-9:
            fail(f"Option max/min ratio exceeds 1.15 for {uid}: {ratio:.4f}")
        if deviation > 0.10 + 1e-9:
            fail(f"Correct-option length deviation exceeds 0.10 for {uid}: {deviation:.4f}")
        if abs(float(qc["max_min_ratio"]) - round(ratio, 4)) > 0.00011:
            fail(f"Persisted option metric mismatch for {uid}")

        metrics = {
            "characters": lengths,
            "max_min_ratio": round(ratio, 4),
            "correct_option": key,
            "correct_vs_distractor_mean_deviation": round(deviation, 4),
            "manual_cue_review": True,
            "second_pass_verified": True,
        }

        con.execute(
            f"""INSERT OR REPLACE INTO question_final_gate(
                question_uid,audit_date,auditor,source_locator,source_version,
                {','.join(SEMANTIC_DIMS)},option_length_metrics_json,rejection_reason,final_status
            ) VALUES(?,?,?,?,?,{','.join('?' for _ in SEMANTIC_DIMS)},?,?,?)""",
            (
                uid,
                now,
                manifest["reviewer"],
                q["source_detail"],
                f"{q['clinical_qa_status']} | currentness/source manually checked 2026-08-14",
                *([1] * len(SEMANTIC_DIMS)),
                json.dumps(metrics, ensure_ascii=False, sort_keys=True),
                None,
                "FINAL_QA_PASS",
            ),
        )

    passed = con.execute(
        """SELECT COUNT(*) FROM question_final_gate
           WHERE question_uid BETWEEN 'V2-Q0632' AND 'V2-Q0681'
             AND final_status='FINAL_QA_PASS'"""
    ).fetchone()[0]
    incomplete = con.execute(
        """SELECT COUNT(*) FROM question_final_gate
           WHERE question_uid BETWEEN 'V2-Q0632' AND 'V2-Q0681'
             AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1
                  OR correct_answer_verified<>1 OR distractors_verified<>1
                  OR explanation_verified<>1 OR currentness_verified<>1
                  OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)"""
    ).fetchone()[0]
    if passed != 50 or incomplete != 0:
        con.rollback()
        fail(f"Wave 28 final gate failed: passed={passed}, incomplete={incomplete}")

    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
        ("wave28_q0632_q0681_manual_final_gate", "PASS_50_OF_50_2026_08_14_ITEM_BY_ITEM_STRICT_OPTIONS"),
    )
    con.commit()
    con.close()

    REPORT.write_text(
        "\n".join([
            "# Manual Final QA Gate — Q0632–Q0681",
            "",
            "- Scope: **50/50** items",
            "- Review method: **manual item-by-item clinical/source QA + separate second pass**",
            "- Final-gate result: **PASS 50/50**",
            "- Source Verified: **PASS**",
            "- Blueprint Verified: **PASS**",
            "- Question Quality Verified: **PASS**",
            "- Correct Answer Verified: **PASS**",
            "- Distractors Verified: **PASS**",
            "- Explanation Verified: **PASS**",
            "- Currentness Verified: **PASS**",
            "- Independent QA: **PASS**",
            "- No unresolved conflicts: **PASS**",
            "- Source locator/version: **PASS**",
            "- Option-length/cue QC: **PASS 50/50**",
            f"- Maximum option max/min character ratio: **{max(ratios):.4f}** (gate ≤ 1.15)",
            f"- Maximum correct-option deviation from distractor mean: **{max(deviations):.4f}** (gate ≤ 0.10)",
            "",
            "Semantic PASS decisions come from the versioned manual review manifest and audited override records. The script validates persisted provenance, structure, option metrics, and second-pass evidence; it does not infer clinical correctness.",
            "",
            "The full-bank commercial release gate remains closed until the remaining bank completes the same process.",
            "",
        ]),
        encoding="utf-8",
    )
    print(
        f"Wave28 manual final gate: PASS 50/50; max_ratio={max(ratios):.4f}; "
        f"max_key_dev={max(deviations):.4f}"
    )


if __name__ == "__main__":
    main()
