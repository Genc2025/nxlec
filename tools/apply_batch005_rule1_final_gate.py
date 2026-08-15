#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE = ROOT / "data/rule1_batch005_reaudit_evidence_q0782_q0831.json"
REPORT = ROOT / "FINAL_QA_BATCH005_Q0782_Q0831_RULE1_10OF10.md"
IDS = [f"V2-Q{i:04d}" for i in range(782, 832)]
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
SECONDARY_EXCEPTIONS = {"V2-Q0791"}
SUBSTANTIVE_CORRECTIONS = {
    "V2-Q0782","V2-Q0784","V2-Q0791","V2-Q0793","V2-Q0794","V2-Q0795",
    "V2-Q0796","V2-Q0799","V2-Q0801","V2-Q0804","V2-Q0811","V2-Q0812",
    "V2-Q0813","V2-Q0817","V2-Q0828","V2-Q0829",
}
CORRECTION_SIGNATURES = {
    "V2-Q0782": ("position-triggered", "BPPV"),
    "V2-Q0784": ("20 mm Hg", "10 mm Hg"),
    "V2-Q0791": ("4 to 5 half-lives", "drug-specific"),
    "V2-Q0793": ("aspiration", "fasting"),
    "V2-Q0794": ("1 to 1.5 inches", "hands"),
    "V2-Q0795": ("delirium", "multicomponent"),
    "V2-Q0796": ("calcium", "bone"),
    "V2-Q0799": ("active listening", "culture"),
    "V2-Q0801": ("prolonged grief", "impairment"),
    "V2-Q0804": ("muscle", "report"),
    "V2-Q0811": ("ceiling", "respiratory"),
    "V2-Q0812": ("horizontal evacuation", "smoke compartment"),
    "V2-Q0813": ("several days", "individual"),
    "V2-Q0817": ("Contact Precautions", "gown"),
    "V2-Q0828": ("diverticulitis", "CT"),
    "V2-Q0829": ("cholecystitis", "ultrasound"),
}
DIMS = [
    "source_verified", "blueprint_verified", "question_quality_verified",
    "correct_answer_verified", "distractors_verified", "explanation_verified",
    "currentness_verified", "independent_qa_passed", "no_unresolved_conflict",
]


def option_metrics(options: dict[str, str], key: str):
    lengths = {k: len(str(v).strip()) for k, v in options.items()}
    vals = list(lengths.values())
    ratio = max(vals) / max(min(vals), 1)
    dmean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    deviation = abs(lengths[key] - dmean) / max(dmean, 1)
    unique_extreme = (
        (lengths[key] == min(vals) and vals.count(min(vals)) == 1)
        or (lengths[key] == max(vals) and vals.count(max(vals)) == 1)
    )
    return lengths, ratio, deviation, unique_extreme


def load_evidence():
    doc = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if doc.get("standard") != "RULE_1_FINAL_10_OF_10_REAL_REAUDIT":
        raise SystemExit("Invalid Rule 1 evidence standard")
    if doc.get("batch") != "Q0782-Q0831" or doc.get("legacy_status_evidence") is not False:
        raise SystemExit("Invalid Batch 005 scope or legacy-evidence policy")
    if doc.get("criteria_names") != CRITERIA:
        raise SystemExit("Rule 1 11-criterion definition mismatch")
    if set(doc.get("secondary_source_exceptions", [])) != SECONDARY_EXCEPTIONS:
        raise SystemExit("Secondary-source exception set mismatch")
    if set(doc.get("substantive_corrections", [])) != SUBSTANTIVE_CORRECTIONS:
        raise SystemExit("Substantive-correction set mismatch")
    items = doc.get("items", [])
    by_id = {x["id"]: x for x in items}
    if len(items) != 50 or len(by_id) != 50 or set(by_id) != set(IDS):
        raise SystemExit("Batch 005 evidence must contain Q0782-Q0831 exactly once each")
    return by_id


def main():
    evidence = load_evidence()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()

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
    con.execute("""CREATE TABLE IF NOT EXISTS rule1_batch005_reaudit_evidence(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,
      category_id INTEGER NOT NULL,client_need TEXT NOT NULL,difficulty TEXT NOT NULL,
      source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator TEXT NOT NULL,
      source_version TEXT NOT NULL,finding TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,
      second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,option_metrics_json TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")

    failures = []
    max_ratio = 0.0
    max_dev = 0.0
    correction_count = 0

    for uid in IDS:
        e = evidence[uid]
        if e.get("criteria") != 11 or e.get("second_pass") != "PASS" or e.get("final") != "FINAL_QA_PASS":
            failures.append(f"{uid}: incomplete semantic evidence")
            continue
        if e.get("reviewed_at") != "2026-08-15":
            failures.append(f"{uid}: currentness date missing")
            continue
        if e.get("authority") not in {"P", "S"}:
            failures.append(f"{uid}: invalid authority class")
            continue
        if (uid in SECONDARY_EXCEPTIONS) != (e.get("authority") == "S"):
            failures.append(f"{uid}: secondary exception mismatch")
            continue
        if not str(e.get("source_url", "")).startswith("https://"):
            failures.append(f"{uid}: invalid source URL")
            continue
        if len(str(e.get("source_locator", ""))) < 45 or len(str(e.get("source_version", ""))) < 20:
            failures.append(f"{uid}: locator/version evidence too weak")
            continue

        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if q is None:
            failures.append(f"{uid}: missing from DB")
            continue
        try:
            options = json.loads(q["item_data_json"])["options"]
            key = json.loads(q["correct_answer_json"])["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid question JSON: {exc}")
            continue
        if set(options) != {"A","B","C","D"} or any(not str(v).strip() for v in options.values()):
            failures.append(f"{uid}: invalid four-option schema")
            continue
        if len({str(v).strip().casefold() for v in options.values()}) != 4:
            failures.append(f"{uid}: duplicate option")
            continue
        if key != e["key"]:
            failures.append(f"{uid}: key mismatch DB={key} evidence={e['key']}")
            continue
        if q["category_id"] != e["category_id"] or q["client_need"] != e["client_need"] or q["difficulty"] != e["difficulty"]:
            failures.append(f"{uid}: blueprint/topic/difficulty mismatch")
            continue
        if q["source_url"].strip() != e["source_url"].strip():
            failures.append(f"{uid}: verified source URL not integrated")
            continue
        sd = (q["source_detail"] or "").casefold()
        if e["source_locator"].casefold() not in sd or e["source_version"].casefold() not in sd:
            failures.append(f"{uid}: locator/version/currentness not integrated")
            continue
        if q["clinical_qa_status"] != "SOURCE_VERIFIED_2026_RULE1_BATCH005":
            failures.append(f"{uid}: Batch 005 source-verification status missing")
            continue

        if uid in CORRECTION_SIGNATURES:
            hay = " ".join([q["stem"], q["rationale"], *options.values()]).casefold()
            sig1, sig2 = CORRECTION_SIGNATURES[uid]
            if sig1.casefold() not in hay or sig2.casefold() not in hay:
                failures.append(f"{uid}: substantive correction signature missing ({sig1!r}, {sig2!r})")
                continue
            correction_count += 1

        lengths, ratio, deviation, unique_extreme = option_metrics(options, key)
        max_ratio = max(max_ratio, ratio)
        max_dev = max(max_dev, deviation)
        if ratio > 1.15 + 1e-12:
            failures.append(f"{uid}: option max/min ratio {ratio:.4f} > 1.15")
            continue
        if deviation > 0.10 + 1e-12:
            failures.append(f"{uid}: correct-option deviation {deviation:.4f} > 0.10")
            continue
        if unique_extreme:
            failures.append(f"{uid}: correct option is unique length extreme")
            continue
        eqc = e.get("option_qc", {})
        if eqc.get("artificial_padding") is not False:
            failures.append(f"{uid}: artificial-padding evidence not explicitly false")
            continue

        metrics = {
            "characters": lengths,
            "max_min_ratio": round(ratio, 4),
            "correct_option": key,
            "correct_deviation_from_distractor_mean": round(deviation, 4),
            "correct_unique_length_extreme": False,
            "artificial_padding": False,
        }
        authority = "SECONDARY_EXCEPTION" if uid in SECONDARY_EXCEPTIONS else "PRIMARY_OR_OFFICIAL_AUTHORITATIVE"
        locator_version = f"{e['source_locator']} {e['source_version']}"
        con.execute("""INSERT OR REPLACE INTO rule1_batch005_reaudit_evidence(
          question_uid,audit_date,correct_option,category_id,client_need,difficulty,source_authority,
          source_url,source_locator,source_version,finding,criteria_passed_count,second_pass,
          final_disposition,option_metrics_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (uid,now,key,e["category_id"],e["client_need"],e["difficulty"],authority,e["source_url"],
           e["source_locator"],e["source_version"],e["finding"],11,"PASS","FINAL_QA_PASS",json.dumps(metrics,sort_keys=True)))
        con.execute("""INSERT OR REPLACE INTO rule1_manual_audit(
          question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,
          finding,criteria_passed_count,second_pass,final_disposition) VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (uid,now,key,authority,e["source_url"],locator_version,e["finding"],11,"PASS","FINAL_QA_PASS"))
        placeholders = ",".join("?" for _ in DIMS)
        con.execute(f"""INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},
          option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{placeholders},?,?,?)""",
          (uid,now,"OpenAI Rule 1 Batch 005 independent re-audit",e["source_locator"],e["source_version"],
           *([1]*len(DIMS)),json.dumps(metrics,sort_keys=True),None,"FINAL_QA_PASS"))

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))
    if correction_count != len(SUBSTANTIVE_CORRECTIONS):
        con.rollback()
        raise SystemExit(f"Substantive corrections verified {correction_count}/{len(SUBSTANTIVE_CORRECTIONS)}")

    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
                ("batch005_q0782_q0831_rule1_final_gate","PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15"))
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    ready = con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    gate = con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    if integrity != "ok" or ready != 0 or not gate or gate[0] != "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA":
        con.rollback()
        raise SystemExit(f"Commercial/integrity gate failure: integrity={integrity} ready={ready} gate={gate}")
    con.commit()

    corrections = ", ".join(sorted(SUBSTANTIVE_CORRECTIONS))
    secondary = ", ".join(sorted(SECONDARY_EXCEPTIONS))
    REPORT.write_text(f"""# Rule 1 Batch 005 — Q0782-Q0831 Real Re-audit

- Scope: **50/50**
- Legacy PASS/status used as semantic evidence: **NO**
- Real item-by-item stem + 4-option semantic review: **50/50**
- Eleven Rule 1 criteria: **11/11 for 50/50**
- Independent second pass: **50/50**
- Correct answers directly source-verified: **50/50**
- Source URL + exact locator + version/currentness integrated: **50/50**
- Blueprint/topic/difficulty verified: **50/50**
- Distractor / ambiguity / second-answer / cue QC: **50/50**
- Unresolved conflicts: **0**
- Option max/min <= 1.15: **50/50** (max {max_ratio:.4f})
- Correct-option deviation <= 10%: **50/50** (max {max_dev:.4f})
- Correct option unique length extreme: **0/50**
- Artificial option padding: **NOT USED**
- Substantive corrections: **{corrections}**
- Documented secondary-source exception: **{secondary}**
- Commercial release gate: **CLOSED** (`commercial_release_ready=0`)
- Final Batch 005 result: **FINAL_QA_PASS 50/50**

Per-item semantic evidence is persisted in `rule1_batch005_reaudit_evidence`; final-gate state is persisted in `question_final_gate`.
""", encoding="utf-8")
    print(f"RULE1_BATCH005_PASS pass=50/50 evidence11=50/50 manual11=50/50 option_qc=50/50 corrections={correction_count}/16 secondary=1/1 max_ratio={max_ratio:.4f} max_dev={max_dev:.4f} ready={ready}")


if __name__ == "__main__":
    main()
