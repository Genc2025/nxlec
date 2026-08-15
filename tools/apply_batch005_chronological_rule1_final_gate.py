#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE=ROOT/"data/rule1_batch005_chronological_reaudit_evidence_q0201_q0250.json"
REPORT=ROOT/"FINAL_QA_BATCH005_Q0201_Q0250_RULE1_10OF10.md"
IDS=[f"V2-Q{i:04d}" for i in range(201,251)]
CRITERIA=[
"stem_and_four_options_read","source_authority_exact_locator_verified","correct_answer_directly_verified",
"stem_claims_verified","rationale_claims_verified","distractor_plausibility_and_second_answer_qc","ambiguity_and_cue_qc",
"blueprint_topic_difficulty_verified","source_version_and_currentness_verified","no_unresolved_conflict","independent_second_pass"]
SECONDARY={"V2-Q0243"}
SUBSTANTIVE={"V2-Q0205","V2-Q0220","V2-Q0236"}
SIGNATURES={
"V2-Q0205":("hyperglycemia","assessed separately"),
"V2-Q0220":("nurse-leader competencies","specific leadership theory"),
"V2-Q0236":("creatinine-cystatin C","muscle mass"),
}
DIMS=["source_verified","blueprint_verified","question_quality_verified","correct_answer_verified","distractors_verified","explanation_verified","currentness_verified","independent_qa_passed","no_unresolved_conflict"]

def option_metrics(options,key):
    lengths={k:len(str(v).strip()) for k,v in options.items()}; vals=list(lengths.values())
    ratio=max(vals)/max(min(vals),1); dm=sum(lengths[k] for k in "ABCD" if k!=key)/3
    dev=abs(lengths[key]-dm)/max(dm,1)
    unique=((lengths[key]==min(vals) and vals.count(min(vals))==1) or (lengths[key]==max(vals) and vals.count(max(vals))==1))
    return lengths,ratio,dev,unique

def main():
    doc=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if doc.get("standard")!="RULE_1_FINAL_10_OF_10_REAL_REAUDIT" or doc.get("batch")!="Q0201-Q0250" or doc.get("legacy_status_evidence") is not False:
        raise SystemExit("Invalid chronological Batch005 Rule 1 evidence header")
    if doc.get("criteria_names")!=CRITERIA: raise SystemExit("11-criterion definition mismatch")
    if set(doc.get("secondary_source_exceptions",[]))!=SECONDARY: raise SystemExit("Secondary exception set mismatch")
    if set(doc.get("substantive_corrections",[]))!=SUBSTANTIVE: raise SystemExit("Substantive correction set mismatch")
    items=doc.get("items",[]); evidence={x["id"]:x for x in items}
    if len(items)!=50 or len(evidence)!=50 or set(evidence)!=set(IDS): raise SystemExit("Evidence must contain Q0201-Q0250 exactly once")

    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; now=datetime.now(timezone.utc).isoformat()
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
    con.execute("""CREATE TABLE IF NOT EXISTS rule1_batch005_chronological_reaudit_evidence(
      question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,category_id INTEGER NOT NULL,client_need TEXT NOT NULL,difficulty TEXT NOT NULL,
      source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator TEXT NOT NULL,source_version TEXT NOT NULL,finding TEXT NOT NULL,
      criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,option_metrics_json TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))""")

    failures=[]; max_ratio=0.0; max_dev=0.0; option_ok=0; corrections=0; secondary=0
    for uid in IDS:
        e=evidence[uid]
        if e.get("criteria")!=11 or e.get("second_pass")!="PASS" or e.get("final")!="FINAL_QA_PASS" or e.get("reviewed_at")!="2026-08-15":
            failures.append(f"{uid}: incomplete 11/11/second-pass evidence"); continue
        if e.get("authority") not in {"P","S"} or ((uid in SECONDARY)!=(e.get("authority")=="S")):
            failures.append(f"{uid}: authority/secondary classification mismatch"); continue
        q=con.execute("SELECT * FROM questions WHERE question_uid=?",(uid,)).fetchone()
        if q is None: failures.append(f"{uid}: missing DB row"); continue
        try:
            options=json.loads(q["item_data_json"])["options"]; key=json.loads(q["correct_answer_json"])["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid JSON {exc}"); continue
        if set(options)!=set("ABCD") or len({str(v).strip().casefold() for v in options.values()})!=4:
            failures.append(f"{uid}: invalid/duplicate options"); continue
        if key!=e["key"]: failures.append(f"{uid}: key mismatch DB={key} evidence={e['key']}"); continue
        if (q["category_id"],q["client_need"],q["difficulty"])!=(e["category_id"],e["client_need"],e["difficulty"]):
            failures.append(f"{uid}: blueprint/topic/difficulty mismatch"); continue
        if (q["source_url"] or "").strip()!=e["source_url"].strip(): failures.append(f"{uid}: source URL not integrated"); continue
        detail=(q["source_detail"] or "").casefold()
        if e["source_locator"].casefold() not in detail or e["source_version"].casefold() not in detail or "2026-08-15" not in detail:
            failures.append(f"{uid}: locator/version/currentness not integrated"); continue
        if q["clinical_qa_status"]!="SOURCE_VERIFIED_2026_RULE1_BATCH005_CHRONOLOGICAL":
            failures.append(f"{uid}: chronological Batch005 source status not integrated"); continue
        if not all((q[x] or "").strip() for x in ("stem","rationale","source_name","source_detail","source_url")):
            failures.append(f"{uid}: missing production content/source fields"); continue
        if uid in SIGNATURES:
            hay=" ".join([q["stem"],q["rationale"],*options.values()]).casefold(); a,b=SIGNATURES[uid]
            if a.casefold() not in hay or b.casefold() not in hay:
                failures.append(f"{uid}: correction signature missing ({a},{b})"); continue
            corrections+=1
        lengths,ratio,dev,unique=option_metrics(options,key); max_ratio=max(max_ratio,ratio); max_dev=max(max_dev,dev)
        if ratio>1.15+1e-12 or dev>0.10+1e-12 or unique:
            failures.append(f"{uid}: option QC ratio={ratio:.4f} dev={dev:.4f} unique={unique}"); continue
        eqc=e.get("option_qc",{})
        if eqc.get("artificial_padding") is not False or eqc.get("correct_unique_length_extreme") is not False:
            failures.append(f"{uid}: option-QC evidence incomplete"); continue
        option_ok+=1; secondary+=int(uid in SECONDARY)
        metrics={"characters":lengths,"max_min_ratio":round(ratio,4),"correct_option":key,
                 "correct_deviation_from_distractor_mean":round(dev,4),"correct_unique_length_extreme":False,"artificial_padding":False}
        authority="SECONDARY_EXCEPTION" if uid in SECONDARY else "PRIMARY_OR_OFFICIAL_AUTHORITATIVE"
        locator_version=f"{e['source_locator']} {e['source_version']}"
        con.execute("""INSERT OR REPLACE INTO rule1_batch005_chronological_reaudit_evidence(
          question_uid,audit_date,correct_option,category_id,client_need,difficulty,source_authority,source_url,source_locator,source_version,finding,
          criteria_passed_count,second_pass,final_disposition,option_metrics_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (uid,now,key,e["category_id"],e["client_need"],e["difficulty"],authority,e["source_url"],e["source_locator"],e["source_version"],e["finding"],11,"PASS","FINAL_QA_PASS",json.dumps(metrics,sort_keys=True)))
        con.execute("""INSERT OR REPLACE INTO rule1_manual_audit(
          question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,finding,criteria_passed_count,second_pass,final_disposition)
          VALUES(?,?,?,?,?,?,?,?,?,?)""",(uid,now,key,authority,e["source_url"],locator_version,e["finding"],11,"PASS","FINAL_QA_PASS"))
        placeholders=",".join("?" for _ in DIMS)
        con.execute(f"""INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{placeholders},?,?,?)""",
          (uid,now,"OpenAI Rule 1 chronological Batch 005 independent re-audit",e["source_locator"],e["source_version"],*([1]*len(DIMS)),json.dumps(metrics,sort_keys=True),None,"FINAL_QA_PASS"))
    if failures:
        con.rollback(); raise SystemExit("\n".join(failures))
    if (option_ok,corrections,secondary)!=(50,3,1):
        con.rollback(); raise SystemExit(f"Gate counts invalid option={option_ok}/50 corrections={corrections}/3 secondary={secondary}/1")
    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",("batch005_chronological_q0201_q0250_rule1_final_gate","PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15"))
    integrity=con.execute("PRAGMA integrity_check").fetchone()[0]; total=con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    ready=con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    gate=con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    pass_count=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0201' AND 'V2-Q0250' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    manual=con.execute("SELECT COUNT(*) FROM rule1_manual_audit WHERE question_uid BETWEEN 'V2-Q0201' AND 'V2-Q0250' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    evcount=con.execute("SELECT COUNT(*) FROM rule1_batch005_chronological_reaudit_evidence WHERE criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    bad=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0201' AND 'V2-Q0250' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    if integrity!="ok" or total!=3525 or ready!=0 or not gate or gate[0]!="CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA" or (pass_count,manual,evcount,bad)!=(50,50,50,0):
        con.rollback(); raise SystemExit(f"Integrated gate failure integrity={integrity} total={total} ready={ready} pass={pass_count} manual={manual} evidence={evcount} bad={bad} gate={gate}")
    con.commit(); con.close()
    REPORT.write_text("\n".join([
        "# Rule 1 Chronological Batch 005 — Q0201-Q0250","",
        "- Scope: **50/50**","- Legacy PASS/status used as semantic evidence: **NO**",
        "- Real item-by-item stem + all four options + rationale review: **50/50**","- Eleven Rule 1 criteria: **11/11 for 50/50**",
        "- Independent second pass: **50/50**","- Correct answers directly source-verified: **50/50**",
        "- Source URL + exact locator + version/currentness integrated: **50/50**","- Blueprint/topic/difficulty verified: **50/50**",
        "- Distractor / ambiguity / second-answer / cue QC: **50/50**","- Unresolved conflicts: **0**",
        f"- Option max/min <= 1.15: **50/50** (max {max_ratio:.4f})",f"- Correct-option deviation <= 10%: **50/50** (max {max_dev:.4f})",
        "- Correct option unique length extreme: **0/50**","- Artificial option padding: **NOT USED**",
        "- Substantive corrections: **Q0205, Q0220, Q0236**","- Documented secondary-source exception: **Q0243 only**",
        "- Final chronological Batch 005 result: **FINAL_QA_PASS 50/50**","",
        "Per-item evidence is persisted in `rule1_batch005_chronological_reaudit_evidence` and `rule1_manual_audit`; strict status is persisted in `question_final_gate`. Full-bank commercial release remains closed.","",
    ]),encoding="utf-8")
    print(f"RULE1_BATCH005_CHRONOLOGICAL_PASS integrity={integrity} total={total} pass={pass_count}/50 evidence11={evcount}/50 manual11={manual}/50 option_qc={option_ok}/50 corrections={corrections}/3 secondary={secondary}/1 bad={bad} max_ratio={max_ratio:.4f} max_dev={max_dev:.4f} ready={ready}")

if __name__=="__main__": main()
