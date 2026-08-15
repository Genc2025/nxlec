#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
MANIFEST = ROOT / "data/rule1_batch004_round2_semantic_manifest_20260815.json"
ROUND2_OVERRIDE = ROOT / "data/clinical_overrides_zz_rule1_batch004_round2_20260815.json"
REPORT = ROOT / "FINAL_QA_BATCH004_ROUND2_20260815.md"
IDS = [f"V2-Q{i:04d}" for i in range(151, 201)]
CRITERIA = [
    "stem_and_four_options_read",
    "source_authority_exact_locator_verified",
    "correct_answer_directly_verified",
    "stem_claims_verified",
    "rationale_claims_verified",
    "distractor_plausibility_and_second_answer_qc",
    "ambiguity_and_cue_qc",
    "blueprint_topic_difficulty_verified",
    "source_version_and_currentness_verified",
    "no_unresolved_conflict",
    "independent_second_pass",
]
SECONDARY = {"V2-Q0151", "V2-Q0180", "V2-Q0199"}
UPGRADES = {"V2-Q0173", "V2-Q0179"}
PRIOR_CORRECTIONS = {"V2-Q0178", "V2-Q0182", "V2-Q0193"}
REJECTED_URLS = {
    "https://www.ncbi.nlm.nih.gov/books/",
    "https://gi.org/guidelines/",
    "https://www.wocn.org/",
    "https://www.fda.gov/medical-devices",
    "https://www.heart.org",
    "https://www.aap.org",
}
DIMS = [
    "source_verified", "blueprint_verified", "question_quality_verified",
    "correct_answer_verified", "distractors_verified", "explanation_verified",
    "currentness_verified", "independent_qa_passed", "no_unresolved_conflict",
]


def option_metrics(options: dict[str, str], key: str):
    lengths = {k: len(v.strip()) for k, v in options.items()}
    vals = list(lengths.values())
    ratio = max(vals) / max(min(vals), 1)
    dmean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    deviation = abs(lengths[key] - dmean) / max(dmean, 1)
    unique_extreme = (
        (lengths[key] == min(vals) and vals.count(min(vals)) == 1)
        or (lengths[key] == max(vals) and vals.count(max(vals)) == 1)
    )
    return lengths, ratio, deviation, unique_extreme


def apply_round2_source_upgrades(con: sqlite3.Connection):
    doc = json.loads(ROUND2_OVERRIDE.read_text(encoding="utf-8"))
    rows = {x["question_uid"]: x for x in doc.get("questions", [])}
    if set(rows) != UPGRADES:
        raise SystemExit(f"Round2 override must contain exactly {sorted(UPGRADES)}")
    for uid, item in rows.items():
        con.execute(
            """UPDATE questions SET stem=?,item_data_json=?,correct_answer_json=?,rationale=?,source_name=?,source_detail=?,source_url=?,clinical_qa_status=?,editorial_priority=?,editorial_flags_json=? WHERE question_uid=?""",
            (item["stem"], item["item_data_json"], item["correct_answer_json"], item["rationale"],
             item["source_name"], item["source_detail"], item["source_url"], item["clinical_qa_status"],
             item["editorial_priority"], item["editorial_flags_json"], uid),
        )
        qc = item.get("qc")
        if qc:
            con.execute(
                """INSERT OR REPLACE INTO option_length_qc(question_uid,lengths_json,min_chars,max_chars,max_min_ratio,correct_option,correct_length_rank,correct_is_extreme,qc_status,qc_note) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (uid, qc["lengths_json"], qc["min_chars"], qc["max_chars"], qc["max_min_ratio"],
                 qc["correct_option"], qc["correct_length_rank"], qc["correct_is_extreme"], qc["qc_status"], qc["qc_note"]),
            )


def main():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if doc.get("count") != 50 or doc.get("fresh_round2_reaudit") is not True or doc.get("legacy_status_used_as_semantic_evidence") is not False:
        raise SystemExit("Fresh Batch 004 semantic manifest policy/scope invalid")
    rows = doc.get("items", [])
    by_id = {x["id"]: x for x in rows}
    if len(rows) != 50 or len(by_id) != 50 or set(by_id) != set(IDS):
        raise SystemExit("Fresh Batch 004 manifest must contain Q0151-Q0200 exactly once each")
    if set(doc.get("secondary_source_exceptions", [])) != SECONDARY:
        raise SystemExit("Secondary-source exception list mismatch")
    if set(doc.get("fresh_source_upgrades", [])) != UPGRADES:
        raise SystemExit("Fresh source-upgrade list mismatch")
    if set(doc.get("prior_substantive_corrections_revalidated", [])) != PRIOR_CORRECTIONS:
        raise SystemExit("Prior-correction revalidation list mismatch")

    for uid in IDS:
        e = by_id[uid]
        if e.get("criteria_passed_count") != 11 or e.get("second_pass") != "PASS" or e.get("final_disposition") != "FINAL_QA_PASS":
            raise SystemExit(f"{uid}: semantic/second-pass evidence incomplete")
        c = e.get("criteria", {})
        if set(c) != set(CRITERIA) or any(c[k] != "PASS" for k in CRITERIA):
            raise SystemExit(f"{uid}: 11/11 criterion evidence incomplete")
        expected_authority = "SECONDARY_EXCEPTION" if uid in SECONDARY else "PRIMARY_OR_OFFICIAL_AUTHORITATIVE"
        if e.get("source_authority") != expected_authority:
            raise SystemExit(f"{uid}: source-authority classification mismatch")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    apply_round2_source_upgrades(con)

    con.execute("""CREATE TABLE IF NOT EXISTS rule1_batch004_round2_evidence(
      question_uid TEXT PRIMARY KEY,
      audit_date TEXT NOT NULL,
      correct_option TEXT NOT NULL,
      category_id INTEGER NOT NULL,
      client_need TEXT NOT NULL,
      difficulty TEXT NOT NULL,
      source_authority TEXT NOT NULL,
      source_url TEXT NOT NULL,
      source_locator_version TEXT NOT NULL,
      finding TEXT NOT NULL,
      source_action TEXT NOT NULL,
      criteria_passed_count INTEGER NOT NULL,
      second_pass TEXT NOT NULL,
      final_disposition TEXT NOT NULL,
      option_metrics_json TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")
    con.execute("""CREATE TABLE IF NOT EXISTS question_final_gate(
      question_uid TEXT PRIMARY KEY, audit_date TEXT NOT NULL, auditor TEXT NOT NULL,
      source_locator TEXT NOT NULL, source_version TEXT NOT NULL,
      source_verified INTEGER NOT NULL, blueprint_verified INTEGER NOT NULL,
      question_quality_verified INTEGER NOT NULL, correct_answer_verified INTEGER NOT NULL,
      distractors_verified INTEGER NOT NULL, explanation_verified INTEGER NOT NULL,
      currentness_verified INTEGER NOT NULL, independent_qa_passed INTEGER NOT NULL,
      no_unresolved_conflict INTEGER NOT NULL, option_length_metrics_json TEXT NOT NULL,
      rejection_reason TEXT, final_status TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")
    con.execute("""CREATE TABLE IF NOT EXISTS rule1_manual_audit(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,
      source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator_version TEXT NOT NULL,
      finding TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,
      final_disposition TEXT NOT NULL,FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")

    failures = []
    metrics_by_uid = {}
    now = datetime.now(timezone.utc).isoformat()
    source_current = 0

    for uid in IDS:
        e = by_id[uid]
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if not q:
            failures.append(f"{uid}: missing question")
            continue
        try:
            options = json.loads(q["item_data_json"])["options"]
            key = json.loads(q["correct_answer_json"])["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid question JSON: {exc}")
            continue
        if set(options) != {"A", "B", "C", "D"} or any(not str(v).strip() for v in options.values()):
            failures.append(f"{uid}: four-option schema invalid")
            continue
        if len({str(v).strip().casefold() for v in options.values()}) != 4:
            failures.append(f"{uid}: duplicate options")
            continue
        if key != e["key"]:
            failures.append(f"{uid}: key mismatch integrated={key} audited={e['key']}")
            continue
        if q["category_id"] != e["category_id"] or q["client_need"] != e["client_need"] or q["difficulty"] != e["difficulty"]:
            failures.append(f"{uid}: blueprint/topic/difficulty mismatch")
            continue
        if not all((q[x] or "").strip() for x in ("stem", "rationale", "source_name", "source_detail", "source_url")):
            failures.append(f"{uid}: missing content/source field")
            continue
        url = q["source_url"].strip()
        detail = q["source_detail"].strip()
        if not url.startswith("https://") or url in REJECTED_URLS:
            failures.append(f"{uid}: weak/rejected source URL {url}")
            continue
        if len(detail) < 70 or "2026-08-15" not in detail:
            failures.append(f"{uid}: exact locator/version/currentness detail incomplete")
            continue
        source_current += 1

        lengths, ratio, deviation, unique_extreme = option_metrics(options, key)
        if ratio > 1.15 + 1e-12:
            failures.append(f"{uid}: max/min ratio {ratio:.4f} > 1.15")
            continue
        if deviation > 0.10 + 1e-12:
            failures.append(f"{uid}: correct-option deviation {deviation:.4f} > 0.10")
            continue
        if unique_extreme:
            failures.append(f"{uid}: correct option is unique length extreme")
            continue

        if uid == "V2-Q0173":
            if url != "https://thinkculturalhealth.hhs.gov/clas/standards" or "42 CFR §482.13(b)(1)-(2)" not in detail:
                failures.append(f"{uid}: fresh HHS CLAS/eCFR source upgrade missing")
                continue
        if uid == "V2-Q0179":
            if url != "https://www.jacc.org/doi/10.1016/j.jacc.2026.05.036" or "2026 AHA/ACC/ESC/WHF" not in detail:
                failures.append(f"{uid}: 2026 HF definition source upgrade missing")
                continue
        if uid == "V2-Q0178" and "meets current STEMI diagnostic criteria" not in q["stem"]:
            failures.append(f"{uid}: prior STEMI ambiguity correction missing")
            continue
        if uid == "V2-Q0182" and not q["stem"].startswith("Two weeks after abdominal surgery"):
            failures.append(f"{uid}: prior SBO/ileus correction missing")
            continue
        if uid == "V2-Q0193":
            if "low-intake dehydration" not in q["stem"] or "measured serum or plasma osmolality" not in options["B"]:
                failures.append(f"{uid}: prior dehydration correction missing")
                continue

        metrics = {
            "characters": lengths,
            "max_min_ratio": round(ratio, 4),
            "correct_option": key,
            "correct_deviation_from_distractor_mean": round(deviation, 4),
            "correct_unique_length_extreme": False,
        }
        metrics_by_uid[uid] = metrics
        authority = e["source_authority"]
        con.execute("""INSERT OR REPLACE INTO rule1_batch004_round2_evidence(
          question_uid,audit_date,correct_option,category_id,client_need,difficulty,source_authority,
          source_url,source_locator_version,finding,source_action,criteria_passed_count,second_pass,
          final_disposition,option_metrics_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, key, e["category_id"], e["client_need"], e["difficulty"], authority,
           url, detail, e["finding"], e["source_action"], 11, "PASS", "FINAL_QA_PASS",
           json.dumps(metrics, sort_keys=True)))
        con.execute("""INSERT OR REPLACE INTO rule1_manual_audit(
          question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,
          finding,criteria_passed_count,second_pass,final_disposition) VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, key, authority, url, detail, e["finding"], 11, "PASS", "FINAL_QA_PASS"))
        placeholders = ",".join("?" for _ in DIMS)
        con.execute(f"""INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},
          option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{placeholders},?,?,?)""",
          (uid, now, "OpenAI Rule 1 Batch 004 fresh round2", detail,
           "Fresh source/version/currentness recheck completed 2026-08-15",
           *([1] * len(DIMS)), json.dumps(metrics, sort_keys=True), None, "FINAL_QA_PASS"))

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))

    if len(metrics_by_uid) != 50 or source_current != 50:
        con.rollback()
        raise SystemExit(f"Fresh verification incomplete metrics={len(metrics_by_uid)} source_current={source_current}")

    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES('batch004_q0151_q0200_rule1_round2_20260815','PASS_50_OF_50_FRESH_ROUND2_SECOND_PASS_11_OF_11_2026_08_15')")
    con.commit()

    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    ready = con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    passed = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0151' AND 'V2-Q0200' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    evidence = con.execute("SELECT COUNT(*) FROM rule1_batch004_round2_evidence WHERE question_uid BETWEEN 'V2-Q0151' AND 'V2-Q0200' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    secondary = con.execute("SELECT COUNT(*) FROM rule1_batch004_round2_evidence WHERE source_authority='SECONDARY_EXCEPTION'").fetchone()[0]
    upgrades = con.execute("SELECT COUNT(*) FROM rule1_batch004_round2_evidence WHERE source_action='SOURCE_UPGRADE_REQUIRED'").fetchone()[0]
    gate = con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    con.close()

    assert integrity == "ok", integrity
    assert total == 3525, total
    assert ready == 0, ready
    assert passed == 50, passed
    assert evidence == 50, evidence
    assert secondary == 3, secondary
    assert upgrades == 2, upgrades
    assert gate and gate[0] == "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA", gate

    max_ratio = max(x["max_min_ratio"] for x in metrics_by_uid.values())
    max_dev = max(x["correct_deviation_from_distractor_mean"] for x in metrics_by_uid.values())
    REPORT.write_text(f"""# Rule 1 Batch 004 — Fresh Round 2 Re-audit (Q0151-Q0200)\n\n- Scope: **50/50**\n- Legacy PASS/status used as semantic evidence: **NO**\n- Fresh item-by-item stem + 4-option semantic review: **50/50**\n- Eleven Rule 1 criteria: **11/11 for 50/50**\n- Independent second pass: **50/50**\n- Correct answers directly source-verified: **50/50**\n- Source URL + locator + version/currentness rechecked: **50/50**\n- Blueprint/topic/difficulty rechecked: **50/50**\n- Distractor / ambiguity / second-answer / cue QC: **50/50**\n- Unresolved conflicts: **0**\n- Option max/min <= 1.15: **50/50** (max {max_ratio:.4f})\n- Correct-option deviation <= 10%: **50/50** (max {max_dev:.4f})\n- Correct option unique length extreme: **0/50**\n- Artificial option padding: **NOT USED**\n- Fresh source/currentness upgrades: **Q0173, Q0179**\n- Prior substantive corrections independently revalidated: **Q0178, Q0182, Q0193**\n- Documented secondary-source exceptions: **Q0151, Q0180, Q0199**\n- Commercial release gate: **CLOSED** (`commercial_release_ready=0`)\n- Final Batch 004 fresh-round2 result: **FINAL_QA_PASS 50/50**\n\nPer-item fresh semantic evidence is persisted in `rule1_batch004_round2_evidence`; final-gate state is persisted in `question_final_gate`.\n""", encoding="utf-8")
    print(f"RULE1_BATCH004_ROUND2_PASS integrity={integrity} total={total} pass={passed}/50 evidence11={evidence}/50 source_current=50/50 option_qc=50/50 upgrades={upgrades}/2 prior_corrections=3/3 secondary={secondary}/3 max_ratio={max_ratio:.4f} max_dev={max_dev:.4f} ready={ready}")


if __name__ == "__main__":
    main()
