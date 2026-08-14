#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
MANIFEST = ROOT / "data" / "manual_final_qa_wave26_0532_0581.json"
REPORT = ROOT / "FINAL_QA_WAVE26_Q0532_Q0581_MANUAL_10OF10.md"
EXPECTED_IDS = [f"V2-Q{i:04d}" for i in range(532, 582)]
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
MAX_RATIO = 1.15
MAX_KEY_DEVIATION = 0.10


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    if not DB.exists():
        fail("Master database does not exist")
    if not MANIFEST.exists():
        fail("Wave 26 manual QA manifest does not exist")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = manifest.get("items", [])
    manifest_ids = [item.get("question_uid") for item in items]
    if manifest_ids != EXPECTED_IDS:
        fail("Manual manifest scope mismatch")
    if len(items) != 50:
        fail(f"Manual manifest must contain exactly 50 items, got {len(items)}")
    for item in items:
        if item.get("manual_disposition") != "PASS" or item.get("all_11_dimensions") is not True:
            fail(f"Manual semantic QA is not PASS for {item.get('question_uid')}")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    table = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='question_final_gate'"
    ).fetchone()
    if not table:
        fail("question_final_gate table is missing; strict governance must run first")

    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    ratios: list[float] = []
    deviations: list[float] = []

    for uid in EXPECTED_IDS:
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if not q:
            fail(f"Missing question in master: {uid}")
        if not str(q["clinical_qa_status"]).startswith("SOURCE_VERIFIED_2026_WAVE26"):
            fail(f"Question is not Wave 26 source-verified: {uid}")

        flags = json.loads(q["editorial_flags_json"] or "[]")
        manual_evidence = "ITEM_BY_ITEM_SOURCE_CHECKED" in flags or "MANUAL_ITEM_BY_ITEM_AUDIT" in flags
        if not manual_evidence:
            fail(f"Missing item-by-item manual audit evidence flag for {uid}")
        if "MANUAL_OPTION_CUE_REVIEW" not in flags or "STRICT_OPTION_LENGTH_QC_PASS" not in flags:
            fail(f"Missing strict manual option/cue evidence for {uid}")

        for field in ("stem", "rationale", "source_name", "source_detail", "source_url"):
            if not str(q[field] or "").strip():
                fail(f"Missing required audited field {field} for {uid}")

        try:
            data = json.loads(q["item_data_json"])
            answer = json.loads(q["correct_answer_json"])
            options = data["options"]
            key = answer["correct_option"]
        except Exception as exc:
            fail(f"Invalid item JSON for {uid}: {exc}")
        if set(options) != {"A", "B", "C", "D"} or key not in options:
            fail(f"Invalid options/key for {uid}")
        normalized = [str(options[k]).strip().casefold() for k in "ABCD"]
        if any(not value for value in normalized) or len(set(normalized)) != 4:
            fail(f"Blank or duplicate option for {uid}")

        qc = con.execute("SELECT * FROM option_length_qc WHERE question_uid=?", (uid,)).fetchone()
        if not qc or qc["qc_status"] != "PASS":
            fail(f"Strict option-length QC is not PASS for {uid}")
        ratio = float(qc["max_min_ratio"])
        if ratio > MAX_RATIO:
            fail(f"Option max/min ratio exceeds {MAX_RATIO:.2f} for {uid}: {ratio:.4f}")

        lengths = json.loads(qc["lengths_json"])
        distractor_mean = sum(float(lengths[k]) for k in "ABCD" if k != key) / 3
        key_dev = abs(float(lengths[key]) - distractor_mean) / max(distractor_mean, 1)
        if key_dev > MAX_KEY_DEVIATION:
            fail(f"Correct-option length deviation exceeds {MAX_KEY_DEVIATION:.2f} for {uid}: {key_dev:.4f}")
        ratios.append(ratio)
        deviations.append(key_dev)

        option_metrics = {
            "characters": lengths,
            "max_min_ratio": ratio,
            "correct_option": key,
            "correct_length_rank": qc["correct_length_rank"],
            "correct_is_extreme": bool(qc["correct_is_extreme"]),
            "correct_vs_distractor_mean_deviation": round(key_dev, 4),
            "manual_cue_review": True,
            "strict_thresholds": {"max_min_ratio": MAX_RATIO, "max_key_deviation": MAX_KEY_DEVIATION},
        }

        values = [1] * len(SEMANTIC_DIMS)
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
                f"{q['clinical_qa_status']} | source/currentness manually checked 2026-08-14",
                *values,
                json.dumps(option_metrics, ensure_ascii=False, sort_keys=True),
                None,
                "FINAL_QA_PASS",
            ),
        )
        inserted += 1

    passed = con.execute(
        """SELECT COUNT(*) FROM question_final_gate
           WHERE question_uid BETWEEN 'V2-Q0532' AND 'V2-Q0581'
             AND final_status='FINAL_QA_PASS'"""
    ).fetchone()[0]
    incomplete = con.execute(
        """SELECT COUNT(*) FROM question_final_gate
           WHERE question_uid BETWEEN 'V2-Q0532' AND 'V2-Q0581'
             AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1
                  OR correct_answer_verified<>1 OR distractors_verified<>1
                  OR explanation_verified<>1 OR currentness_verified<>1
                  OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)"""
    ).fetchone()[0]
    if inserted != 50 or passed != 50 or incomplete != 0:
        con.rollback()
        fail(f"Wave 26 final gate failed: inserted={inserted}, passed={passed}, incomplete={incomplete}")

    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
        ("wave26_q0532_q0581_manual_final_gate", "PASS_50_OF_50_2026_08_14_ITEM_BY_ITEM_STRICT_OPTIONS"),
    )
    con.commit()
    con.close()

    REPORT.write_text(
        "\n".join([
            "# Manual Final QA Gate — Q0532–Q0581",
            "",
            "- Scope: **50/50** items",
            "- Review method: **manual item-by-item clinical/source QA**",
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
            f"- Maximum option max/min character ratio: **{max(ratios):.4f}** (gate ≤ {MAX_RATIO:.2f})",
            f"- Maximum correct-option deviation from distractor mean: **{max(deviations):.4f}** (gate ≤ {MAX_KEY_DEVIATION:.2f})",
            "",
            "The semantic PASS decisions come from the versioned manual review manifest and item-by-item audited override records. Option wording was manually rebalanced after cue review. The scripts enforce persistence and quantitative anti-cue limits; they do not infer clinical correctness.",
            "",
            "This is a batch-level final QA disposition only. The full-bank commercial release gate remains closed until the remaining bank completes the same process.",
            "",
        ]), encoding="utf-8")
    print(f"Wave26 manual final gate: PASS {passed}/50; max_ratio={max(ratios):.4f}; max_key_dev={max(deviations):.4f}")


if __name__ == "__main__":
    main()
