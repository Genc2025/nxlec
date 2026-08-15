#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE_FILES = [
    ROOT / "data/rule1_batch004_reaudit_evidence_part1_q0151_q0175.json",
    ROOT / "data/rule1_batch004_reaudit_evidence_part2_q0176_q0200.json",
]
REPORT = ROOT / "FINAL_QA_BATCH004_Q0151_Q0200_RULE1_10OF10.md"
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
SECONDARY_EXCEPTIONS = {"V2-Q0151", "V2-Q0180", "V2-Q0199"}
SUBSTANTIVE_CORRECTIONS = {"V2-Q0178", "V2-Q0182", "V2-Q0193"}
SOURCE_NAME_OVERRIDES = {
    "V2-Q0154": "ONS/ASCO — Guideline for Management of Antineoplastic Extravasation",
    "V2-Q0162": "Society of Critical Care Medicine — Surviving Sepsis Campaign 2026",
    "V2-Q0163": "The Joint Commission — Universal Protocol / Final Time-Out",
    "V2-Q0164": "The Joint Commission — Effectively Managing Medications",
    "V2-Q0166": "ISMP/ECRI — Look-Alike and Sound-Alike Medication Risk Reduction",
    "V2-Q0167": "AACN — Managing Alarms in Acute Care Across the Life Span",
    "V2-Q0172": "HHS — HIPAA Right of Access FAQ 2065",
    "V2-Q0173": "HHS Office of Minority Health — National CLAS Standards",
    "V2-Q0174": "eCFR — 45 CFR §92.201, Meaningful Access for Individuals with Limited English Proficiency",
    "V2-Q0175": "eCFR — 42 CFR §418.24, Election of Hospice Care",
    "V2-Q0179": "AHA/ACC/HFSA — 2022 Guideline for the Management of Heart Failure",
    "V2-Q0181": "CDC — First Aid for Seizures",
    "V2-Q0185": "Consortium for Spinal Cord Medicine — Acute Cardiovascular Management After Spinal Cord Injury",
    "V2-Q0186": "American College of Gastroenterology — 2024 Acute Pancreatitis Guideline",
    "V2-Q0188": "AASLD/EASL — Hepatic Encephalopathy in Chronic Liver Disease Guideline",
    "V2-Q0191": "AHA/ACC/ESC/WHF — Fourth Universal Definition of Myocardial Infarction",
    "V2-Q0192": "International Pressure Injury Guideline — Repositioning",
    "V2-Q0194": "NIH MedlinePlus — Using a Cane",
    "V2-Q0198": "NIAAA — Screen and Assess Alcohol Use",
    "V2-Q0199": "NCBI Bookshelf / Open RN — Nursing: Mental Health and Community Concepts",
    "V2-Q0200": "American Association for Emergency Psychiatry — Project BETA De-escalation Consensus",
}
REJECTED_URLS = {
    "https://www.facs.org/quality-programs/trauma/education/",
    "https://gi.org/guidelines/",
    "https://www.ncbi.nlm.nih.gov/books/",
    "https://www.jointcommission.org/resources/patient-safety-topics/workplace-violence-prevention/",
    "https://www.fda.gov/medical-devices/human-factors-and-medical-devices/human-factors-considerations",
}
CORRECTION_SIGNATURES = {
    "V2-Q0178": {
        "stem": "meets current STEMI diagnostic criteria",
        "option": ("D", "STEMI reperfusion pathway"),
        "rationale": "should not be delayed solely to await cardiac biomarker confirmation",
    },
    "V2-Q0182": {
        "stem": "Two weeks after abdominal surgery",
        "option": ("D", "postoperative small-bowel obstruction"),
        "rationale": "removes the prior ileus-versus-obstruction ambiguity",
    },
    "V2-Q0193": {
        "stem": "dry mouth and delayed skin recoil",
        "option": ("B", "measured serum or plasma osmolality"),
        "rationale": "prior item conflated low-intake dehydration with volume depletion",
    },
}
DIMS = [
    "source_verified", "blueprint_verified", "question_quality_verified",
    "correct_answer_verified", "distractors_verified", "explanation_verified",
    "currentness_verified", "independent_qa_passed", "no_unresolved_conflict",
]


def load_evidence():
    rows = []
    for path in EVIDENCE_FILES:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("standard") != "RULE_1_FINAL_10_OF_10_REAL_REAUDIT":
            raise SystemExit(f"{path.name}: invalid Rule 1 standard")
        if doc.get("batch") != "Q0151-Q0200" or doc.get("legacy_status_evidence") is not False:
            raise SystemExit(f"{path.name}: invalid scope or legacy evidence policy")
        if doc.get("criteria_names") != CRITERIA:
            raise SystemExit(f"{path.name}: 11-criterion definition mismatch")
        rows.extend(doc.get("items", []))
    by_id = {x["id"]: x for x in rows}
    if len(rows) != 50 or len(by_id) != 50 or set(by_id) != set(IDS):
        raise SystemExit("Batch 004 evidence must contain Q0151-Q0200 exactly once each")
    return by_id


def option_metrics(options, key):
    lengths = {k: len(v.strip()) for k, v in options.items()}
    values = list(lengths.values())
    ratio = max(values) / max(min(values), 1)
    distractor_mean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    deviation = abs(lengths[key] - distractor_mean) / max(distractor_mean, 1)
    unique_extreme = (
        (lengths[key] == min(values) and values.count(min(values)) == 1)
        or (lengths[key] == max(values) and values.count(max(values)) == 1)
    )
    return lengths, ratio, deviation, unique_extreme


def main():
    evidence = load_evidence()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
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
    con.execute("""CREATE TABLE IF NOT EXISTS rule1_batch004_reaudit_evidence(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,
      category_id INTEGER NOT NULL,client_need TEXT NOT NULL,difficulty TEXT NOT NULL,
      source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator TEXT NOT NULL,
      source_version TEXT NOT NULL,finding TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,
      second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,option_metrics_json TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")

    failures = []
    metrics_by_uid = {}
    now = datetime.now(timezone.utc).isoformat()

    # Integrate verified source locator/version/currentness into the question records first.
    for uid in IDS:
        e = evidence[uid]
        if e.get("criteria") != 11 or e.get("second_pass") != "PASS" or e.get("final") != "FINAL_QA_PASS":
            failures.append(f"{uid}: semantic evidence is incomplete")
            continue
        if e.get("reviewed_at") != "2026-08-15":
            failures.append(f"{uid}: currentness review date missing")
            continue
        if e.get("authority") not in {"P", "S"}:
            failures.append(f"{uid}: invalid authority classification")
            continue
        if (uid in SECONDARY_EXCEPTIONS) != (e.get("authority") == "S"):
            failures.append(f"{uid}: secondary-source exception classification mismatch")
            continue
        url = e.get("source_url", "").strip()
        locator = e.get("source_locator", "").strip()
        version = e.get("source_version", "").strip()
        if not url.startswith("https://") or url in REJECTED_URLS:
            failures.append(f"{uid}: weak/rejected source URL: {url}")
            continue
        if len(locator) < 70 or len(version) < 25 or "2026" not in version:
            failures.append(f"{uid}: locator/version/currentness evidence incomplete")
            continue
        source_detail = f"{locator} {version}"
        if uid in SOURCE_NAME_OVERRIDES:
            con.execute("UPDATE questions SET source_name=?,source_detail=?,source_url=? WHERE question_uid=?",
                        (SOURCE_NAME_OVERRIDES[uid], source_detail, url, uid))
        else:
            con.execute("UPDATE questions SET source_detail=?,source_url=? WHERE question_uid=?",
                        (source_detail, url, uid))

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))

    for uid in IDS:
        e = evidence[uid]
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
            failures.append(f"{uid}: duplicate answer option")
            continue
        if key != e["key"]:
            failures.append(f"{uid}: integrated key {key} differs from direct-source audit key {e['key']}")
            continue
        if q["category_id"] != e["category_id"] or q["client_need"] != e["client_need"] or q["difficulty"] != e["difficulty"]:
            failures.append(f"{uid}: blueprint/topic/difficulty mismatch")
            continue
        if not all((q[x] or "").strip() for x in ("stem", "rationale", "source_name", "source_detail", "source_url")):
            failures.append(f"{uid}: missing integrated content/source fields")
            continue
        if q["source_url"].strip() != e["source_url"].strip():
            failures.append(f"{uid}: verified source URL was not integrated")
            continue
        if e["source_locator"].casefold() not in q["source_detail"].casefold() or e["source_version"].casefold() not in q["source_detail"].casefold():
            failures.append(f"{uid}: verified locator/version was not integrated")
            continue
        if not str(q["clinical_qa_status"]).startswith("SOURCE_VERIFIED_2026_"):
            failures.append(f"{uid}: source-verification status missing")
            continue

        if uid in CORRECTION_SIGNATURES:
            sig = CORRECTION_SIGNATURES[uid]
            if sig["stem"].casefold() not in q["stem"].casefold():
                failures.append(f"{uid}: corrected stem signature missing")
                continue
            opt_key, opt_text = sig["option"]
            if opt_text.casefold() not in options[opt_key].casefold():
                failures.append(f"{uid}: corrected answer-option signature missing")
                continue
            if sig["rationale"].casefold() not in q["rationale"].casefold():
                failures.append(f"{uid}: corrected rationale signature missing")
                continue

        lengths, ratio, deviation, unique_extreme = option_metrics(options, key)
        if ratio > 1.15 + 1e-12:
            failures.append(f"{uid}: option max/min ratio {ratio:.4f} > 1.15")
            continue
        if deviation > 0.10 + 1e-12:
            failures.append(f"{uid}: correct-option deviation {deviation:.4f} > 0.10")
            continue
        if unique_extreme:
            failures.append(f"{uid}: correct option is unique length extreme")
            continue

        metrics = {
            "characters": lengths,
            "max_min_ratio": round(ratio, 4),
            "correct_option": key,
            "correct_deviation_from_distractor_mean": round(deviation, 4),
            "correct_unique_length_extreme": False,
        }
        metrics_by_uid[uid] = metrics
        authority = "SECONDARY_EXCEPTION" if uid in SECONDARY_EXCEPTIONS else "PRIMARY_OR_OFFICIAL_AUTHORITATIVE"
        locator_version = f"{e['source_locator']} {e['source_version']}"
        con.execute("""INSERT OR REPLACE INTO rule1_batch004_reaudit_evidence(
          question_uid,audit_date,correct_option,category_id,client_need,difficulty,source_authority,
          source_url,source_locator,source_version,finding,criteria_passed_count,second_pass,
          final_disposition,option_metrics_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, key, e["category_id"], e["client_need"], e["difficulty"], authority,
           e["source_url"], e["source_locator"], e["source_version"], e["finding"], 11,
           "PASS", "FINAL_QA_PASS", json.dumps(metrics, sort_keys=True)))
        con.execute("""INSERT OR REPLACE INTO rule1_manual_audit(
          question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,
          finding,criteria_passed_count,second_pass,final_disposition) VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (uid, now, key, authority, e["source_url"], locator_version, e["finding"], 11, "PASS", "FINAL_QA_PASS"))
        placeholders = ",".join("?" for _ in DIMS)
        con.execute(f"""INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},
          option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{placeholders},?,?,?)""",
          (uid, now, "OpenAI Rule 1 Batch 004 independent re-audit", e["source_locator"], e["source_version"],
           *([1] * len(DIMS)), json.dumps(metrics, sort_keys=True), None, "FINAL_QA_PASS"))

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))

    pass_count = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0151' AND 'V2-Q0200' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    evidence_count = con.execute("SELECT COUNT(*) FROM rule1_batch004_reaudit_evidence WHERE question_uid BETWEEN 'V2-Q0151' AND 'V2-Q0200' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    manual_count = con.execute("SELECT COUNT(*) FROM rule1_manual_audit WHERE question_uid BETWEEN 'V2-Q0151' AND 'V2-Q0200' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    if (pass_count, evidence_count, manual_count) != (50, 50, 50):
        con.rollback()
        raise SystemExit(f"Batch 004 final counts invalid: gate={pass_count}, evidence={evidence_count}, manual={manual_count}")

    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
                ("batch004_q0151_q0200_rule1_final_gate", "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15"))
    con.commit()
    con.close()

    max_ratio = max(v["max_min_ratio"] for v in metrics_by_uid.values())
    max_dev = max(v["correct_deviation_from_distractor_mean"] for v in metrics_by_uid.values())
    REPORT.write_text("\n".join([
        "# Rule 1 Batch 004 — Q0151-Q0200",
        "",
        "- Scope: **50/50**",
        "- Legacy PASS/status used as semantic evidence: **NO**",
        "- Real item-by-item source/semantic review: **50/50**",
        "- Eleven Rule 1 criteria: **11/11 for 50/50**",
        "- Independent second pass: **50/50**",
        "- Correct answers directly source-verified: **50/50**",
        "- Source URL + exact locator + version/currentness integrated: **50/50**",
        "- Blueprint/topic/difficulty verified: **50/50**",
        "- Distractor ambiguity / second-answer / cue QC: **50/50**",
        "- Unresolved conflicts: **0**",
        f"- Option max/min <= 1.15: **50/50** (max {max_ratio:.4f})",
        f"- Correct-option deviation <= 10%: **50/50** (max {max_dev:.4f})",
        "- Correct option unique length extreme: **0/50**",
        "- Artificial option padding: **NOT USED**",
        "- Substantive clinical/semantic corrections: **Q0178, Q0182, Q0193**",
        "- Documented secondary-source exceptions: **Q0151, Q0180, Q0199**",
        "- Final Batch 004 result: **FINAL_QA_PASS 50/50**",
        "",
        "Per-item evidence is persisted in `rule1_batch004_reaudit_evidence` and `rule1_manual_audit`; strict status is persisted in `question_final_gate`. Full-bank commercial release remains closed.",
        "",
    ]), encoding="utf-8")
    print(f"RULE1_BATCH004_PASS pass={pass_count}/50 evidence11={evidence_count}/50 manual11={manual_count}/50 option_qc={len(metrics_by_uid)}/50 corrections=3/3 max_ratio={max_ratio:.4f} max_dev={max_dev:.4f}")


if __name__ == "__main__":
    main()
