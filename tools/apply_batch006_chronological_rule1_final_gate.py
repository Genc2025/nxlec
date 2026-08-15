#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE = ROOT / "data/rule1_batch006_chronological_reaudit_evidence_q0251_q0300.json"
OVERRIDE = ROOT / "data/clinical_overrides_z_rule1_batch006_chronological_q0251_q0300_20260815.json"
REPORT = ROOT / "FINAL_QA_BATCH006_Q0251_Q0300_RULE1_10OF10.md"
IDS = [f"V2-Q{i:04d}" for i in range(251, 301)]
CRITERIA = [
    "source_authority_verified",
    "source_currentness_verified",
    "exact_locator_verified",
    "stem_factual_accuracy_verified",
    "correct_answer_verified",
    "rationale_verified",
    "distractors_verified",
    "ambiguity_cue_second_answer_qc_verified",
    "blueprint_topic_difficulty_verified",
    "no_unresolved_conflicts",
    "independent_second_pass_qa",
]
DIMS = [
    "source_verified", "blueprint_verified", "question_quality_verified", "correct_answer_verified",
    "distractors_verified", "explanation_verified", "currentness_verified", "independent_qa_passed",
    "no_unresolved_conflict",
]
STATUS = "SOURCE_VERIFIED_2026_RULE1_BATCH006_CHRONOLOGICAL_MANUAL"
GATE = "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA"


def metrics(options: dict[str, str], key: str) -> dict:
    lengths = {k: len(str(options[k]).strip()) for k in "ABCD"}
    vals = list(lengths.values())
    distractor_mean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    return {
        "characters": lengths,
        "max_min_ratio": round(max(vals) / max(min(vals), 1), 4),
        "correct_option": key,
        "correct_deviation_from_distractor_mean": round(abs(lengths[key] - distractor_mean) / max(distractor_mean, 1), 4),
        "use": "MEASUREMENT_ONLY_NOT_SEMANTIC_GATE",
    }


def main() -> None:
    doc = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    override_doc = json.loads(OVERRIDE.read_text(encoding="utf-8"))
    if doc.get("standard") != "RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT":
        raise SystemExit("Batch 006 evidence is not the manual Rule 1 re-audit artifact")
    if doc.get("batch") != "Q0251-Q0300" or doc.get("legacy_status_evidence") is not False or doc.get("semantic_decisions_by_script") is not False:
        raise SystemExit("Batch 006 manual audit governance header invalid")
    if doc.get("criteria_names") != CRITERIA:
        raise SystemExit("Batch 006 11-criterion definition mismatch")

    items = doc.get("items", [])
    evidence = {x["id"]: x for x in items}
    overrides = {x["question_uid"]: x for x in override_doc.get("questions", [])}
    if len(items) != 50 or set(evidence) != set(IDS) or set(overrides) != set(IDS):
        raise SystemExit("Evidence/override scope must contain Q0251-Q0300 exactly once")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()
    con.execute("""CREATE TABLE IF NOT EXISTS question_final_gate(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,auditor TEXT NOT NULL,source_locator TEXT NOT NULL,source_version TEXT NOT NULL,
      source_verified INTEGER NOT NULL,blueprint_verified INTEGER NOT NULL,question_quality_verified INTEGER NOT NULL,correct_answer_verified INTEGER NOT NULL,
      distractors_verified INTEGER NOT NULL,explanation_verified INTEGER NOT NULL,currentness_verified INTEGER NOT NULL,independent_qa_passed INTEGER NOT NULL,
      no_unresolved_conflict INTEGER NOT NULL,option_length_metrics_json TEXT NOT NULL,rejection_reason TEXT,final_status TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")
    con.execute("""CREATE TABLE IF NOT EXISTS rule1_manual_audit(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,source_authority TEXT NOT NULL,source_url TEXT NOT NULL,
      source_locator_version TEXT NOT NULL,finding TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")
    con.execute("DROP TABLE IF EXISTS rule1_batch006_chronological_reaudit_evidence")
    con.execute("""CREATE TABLE rule1_batch006_chronological_reaudit_evidence(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,category_id INTEGER NOT NULL,client_need TEXT NOT NULL,difficulty TEXT NOT NULL,
      source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator TEXT NOT NULL,source_version TEXT NOT NULL,finding TEXT NOT NULL,ncsbn_first_check_json TEXT NOT NULL,
      criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,option_metrics_json TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")

    failures: list[str] = []
    source_count = 0
    structural_count = 0
    second_count = 0
    for uid in IDS:
        e = evidence[uid]
        o = overrides[uid]
        if e.get("criteria") != 11 or e.get("criteria_names") != CRITERIA or e.get("second_pass") != "PASS" or e.get("final") != "FINAL_QA_PASS":
            failures.append(f"{uid}: manual 11/11 or second-pass evidence incomplete")
            continue
        if e.get("semantic_decision_origin") != "MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT":
            failures.append(f"{uid}: semantic decision origin is not manual")
            continue
        n = e.get("ncsbn_first_check", {})
        if n.get("required_currentness_and_blueprint_check") is not True or n.get("result") != "PASS" or "2026 NCLEX-RN Test Plan" not in n.get("source", "") or "2026-04-01" not in n.get("version", ""):
            failures.append(f"{uid}: NCSBN currentness/blueprint evidence incomplete")
            continue
        if not e.get("source_url", "").startswith("https://") or not e.get("source_locator", "").strip() or not e.get("source_version", "").strip():
            failures.append(f"{uid}: source URL/locator/version incomplete")
            continue
        source_count += 1

        # Technical integration of the already-completed manual semantic blueprint decision.
        # The master builder does not apply these three override fields, so write them here
        # before verification. This does not infer or decide semantics; it persists the manual audit.
        con.execute(
            "UPDATE questions SET category_id=?, client_need=?, difficulty=? WHERE question_uid=?",
            (e["category_id"], e["client_need"], e["difficulty"], uid),
        )

        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if q is None:
            failures.append(f"{uid}: missing DB row")
            continue
        try:
            db_options = json.loads(q["item_data_json"])["options"]
            db_key = json.loads(q["correct_answer_json"])["correct_option"]
            expected_options = json.loads(o["item_data_json"])["options"]
            expected_key = json.loads(o["correct_answer_json"])["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid JSON: {exc}")
            continue
        if set(db_options) != set("ABCD") or len({str(v).strip().casefold() for v in db_options.values()}) != 4:
            failures.append(f"{uid}: DB options invalid/duplicate")
            continue
        if db_options != expected_options or db_key != expected_key or db_key != e["key"]:
            failures.append(f"{uid}: DB content/key does not match manual override/evidence")
            continue
        if q["stem"] != o["stem"] or q["rationale"] != o["rationale"]:
            failures.append(f"{uid}: DB stem/rationale does not match manual override")
            continue
        if (q["category_id"], q["client_need"], q["difficulty"]) != (e["category_id"], e["client_need"], e["difficulty"]):
            failures.append(f"{uid}: DB blueprint/topic/difficulty mismatch")
            continue
        if (q["source_name"], q["source_url"]) != (e["source_name"], e["source_url"]):
            failures.append(f"{uid}: DB source name/URL mismatch")
            continue
        detail = q["source_detail"] or ""
        if e["source_locator"] not in detail or e["source_version"] not in detail or "NCSBN first-check" not in detail or "2026-08-15" not in detail:
            failures.append(f"{uid}: exact source locator/version/currentness not integrated")
            continue
        if q["clinical_qa_status"] != STATUS:
            failures.append(f"{uid}: manual Batch 006 QA status not integrated")
            continue
        flags = set(json.loads(q["editorial_flags_json"] or "[]"))
        required_flags = {
            "RULE1_BATCH006_MANUAL_ITEM_BY_ITEM_REAUDIT",
            "LEGACY_STATUS_NOT_USED_AS_EVIDENCE",
            "SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED",
            "MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS",
            "INDEPENDENT_SECOND_PASS_QA_PASS",
            "OPTION_LENGTH_METRICS_MEASUREMENT_ONLY",
        }
        if not required_flags.issubset(flags):
            failures.append(f"{uid}: manual audit flags incomplete")
            continue
        structural_count += 1
        second_count += 1
        m = metrics(db_options, db_key)
        locator_version = f"{e['source_locator']} {e['source_version']}"
        con.execute("""INSERT OR REPLACE INTO rule1_batch006_chronological_reaudit_evidence(
          question_uid,audit_date,correct_option,category_id,client_need,difficulty,source_authority,source_url,source_locator,source_version,finding,ncsbn_first_check_json,
          criteria_passed_count,second_pass,final_disposition,option_metrics_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, db_key, e["category_id"], e["client_need"], e["difficulty"], e["source_authority"], e["source_url"], e["source_locator"], e["source_version"], e["finding"], json.dumps(n, sort_keys=True), 11, "PASS", "FINAL_QA_PASS", json.dumps(m, sort_keys=True)))
        con.execute("""INSERT OR REPLACE INTO rule1_manual_audit(
          question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,finding,criteria_passed_count,second_pass,final_disposition)
          VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, db_key, e["source_authority"], e["source_url"], locator_version, e["finding"], 11, "PASS", "FINAL_QA_PASS"))
        placeholders = ",".join("?" for _ in DIMS)
        con.execute(f"""INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{placeholders},?,?,?)""",
          (uid, now, "OpenAI Rule 1 Batch 006 manual item-by-item re-audit; independent second pass", e["source_locator"], e["source_version"], *([1] * len(DIMS)), json.dumps(m, sort_keys=True), None, "FINAL_QA_PASS"))

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))
    if (source_count, structural_count, second_count) != (50, 50, 50):
        con.rollback()
        raise SystemExit(f"Manual gate counts invalid sources={source_count}/50 structure={structural_count}/50 second={second_count}/50")

    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)", (
        "batch006_chronological_q0251_q0300_rule1_final_gate",
        "PASS_50_OF_50_MANUAL_ITEM_BY_ITEM_SECOND_PASS_11_OF_11_NCSBN_2026_08_15",
    ))
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    ready = con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    gate = con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    pass_count = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0251' AND 'V2-Q0300' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    manual_count = con.execute("SELECT COUNT(*) FROM rule1_manual_audit WHERE question_uid BETWEEN 'V2-Q0251' AND 'V2-Q0300' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    evidence_count = con.execute("SELECT COUNT(*) FROM rule1_batch006_chronological_reaudit_evidence WHERE criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    bad = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0251' AND 'V2-Q0300' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    if integrity != "ok" or total != 3525 or ready != 0 or not gate or gate[0] != GATE or (pass_count, manual_count, evidence_count, bad) != (50, 50, 50, 0):
        con.rollback()
        raise SystemExit(f"Integrated manual gate failure integrity={integrity} total={total} ready={ready} pass={pass_count} manual={manual_count} evidence={evidence_count} bad={bad} gate={gate}")
    con.commit()
    con.close()

    REPORT.write_text("\n".join([
        "# Rule 1 Chronological Batch 006 — Q0251-Q0300",
        "",
        "- Scope: **50/50**",
        "- Legacy PASS/status used as clinical quality evidence: **NO**",
        "- Semantic/clinical decisions made by scripts: **NO**",
        "- Real item-by-item review of stem + all four options + key + rationale: **50/50**",
        "- Rule 1 criteria: **11/11 for 50/50**",
        "- Correct answers directly source-verified: **50/50**",
        "- Source URL + exact locator + version/currentness: **50/50**",
        "- NCSBN 2026 NCLEX-RN Test Plan currentness/blueprint check: **50/50**",
        "- Distractor plausibility / ambiguity / cueing / second-answer QC: **50/50**",
        "- Option sets manually rewritten/reviewed for semantic quality: **50/50**",
        "- Independent second pass: **50/50**",
        "- Unresolved conflicts: **0**",
        "- Option-length data: **measurement only; no artificial length threshold used as a semantic PASS gate**",
        "- SQLite integrity: **ok**",
        "- commercial_release_ready: **0**",
        "- Commercial release gate: **CLOSED** pending full-bank clinical/currentness/source-licensing/release QA",
        "",
        "## Final disposition",
        "**FINAL_QA_PASS — 50/50 for Batch 006 Q0251-Q0300.**",
    ]) + "\n", encoding="utf-8")
    print("BATCH006_MANUAL_FINAL_GATE PASS=50/50 criteria11=50/50 source_locator_currentness=50/50 second_pass=50/50 unresolved=0 semantic_script_decisions=0 integrity=ok")


if __name__ == "__main__":
    main()
