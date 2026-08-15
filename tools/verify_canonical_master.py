#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
PENDING = ROOT / "data/pending_audit_next.json"


def main() -> None:
    if not DB.exists():
        raise SystemExit("Master database was not created")
    con = sqlite3.connect(DB)
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    verified = con.execute("SELECT COUNT(*) FROM questions WHERE clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%'").fetchone()[0]
    ready = con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    gate = con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    policy = con.execute("SELECT value FROM bank_metadata WHERE key='strict_final_gate_policy'").fetchone()
    metadata_keys = [
        "batch001_q0001_q0050_final_gate",
        "batch002_q0051_q0100_rule1_final_gate",
        "batch003_q0101_q0150_rule1_final_gate",
        "batch004_q0151_q0200_rule1_final_gate",
        "batch005_chronological_q0201_q0250_rule1_final_gate",
        "batch006_chronological_q0251_q0300_rule1_final_gate",
        "batch005_q0782_q0831_rule1_final_gate",
        "batch006_q0832_q0881_rule1_final_gate",
        "wave25_q0492_q0531_final_gate",
        "wave26_q0532_q0581_manual_final_gate",
        "wave27_q0582_q0631_manual_final_gate",
    ]
    meta = {k: con.execute("SELECT value FROM bank_metadata WHERE key=?", (k,)).fetchone() for k in metadata_keys}
    records = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid IN (SELECT question_uid FROM questions WHERE clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%')").fetchone()[0]
    passed = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE final_status='FINAL_QA_PASS'").fetchone()[0]
    pending_gate = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE final_status='FINAL_QA_PENDING'").fetchone()[0]

    def cp(a: str, b: str) -> int:
        return con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN ? AND ? AND final_status='FINAL_QA_PASS'", (a, b)).fetchone()[0]

    def cm(a: str, b: str) -> int:
        return con.execute("SELECT COUNT(*) FROM rule1_manual_audit WHERE question_uid BETWEEN ? AND ? AND final_disposition='FINAL_QA_PASS' AND second_pass='PASS' AND criteria_passed_count=11", (a, b)).fetchone()[0]

    b1 = cp("V2-Q0001", "V2-Q0050")
    b2, b2m = cp("V2-Q0051", "V2-Q0100"), cm("V2-Q0051", "V2-Q0100")
    b3, b3m = cp("V2-Q0101", "V2-Q0150"), cm("V2-Q0101", "V2-Q0150")
    b4, b4m = cp("V2-Q0151", "V2-Q0200"), cm("V2-Q0151", "V2-Q0200")
    b5c, b5cm = cp("V2-Q0201", "V2-Q0250"), cm("V2-Q0201", "V2-Q0250")
    b6c, b6cm = cp("V2-Q0251", "V2-Q0300"), cm("V2-Q0251", "V2-Q0300")
    off5, off5m = cp("V2-Q0782", "V2-Q0831"), cm("V2-Q0782", "V2-Q0831")
    off6, off6m = cp("V2-Q0832", "V2-Q0881"), cm("V2-Q0832", "V2-Q0881")
    w25, w26, w27 = cp("V2-Q0492", "V2-Q0531"), cp("V2-Q0532", "V2-Q0581"), cp("V2-Q0582", "V2-Q0631")
    w26_option = con.execute("SELECT COUNT(*) FROM option_length_qc WHERE question_uid BETWEEN 'V2-Q0532' AND 'V2-Q0581' AND qc_status='PASS' AND max_min_ratio<=1.15").fetchone()[0]
    w27_option = con.execute("SELECT COUNT(*) FROM option_length_qc WHERE question_uid BETWEEN 'V2-Q0582' AND 'V2-Q0631' AND qc_status='PASS' AND max_min_ratio<=1.15").fetchone()[0]
    b5ce = con.execute("SELECT COUNT(*) FROM rule1_batch005_chronological_reaudit_evidence WHERE criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    b5cbad = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0201' AND 'V2-Q0250' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    b6ce = con.execute("SELECT COUNT(*) FROM rule1_batch006_chronological_reaudit_evidence WHERE criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    b6cncsbn = con.execute("SELECT COUNT(*) FROM rule1_batch006_chronological_reaudit_evidence WHERE ncsbn_first_check=1").fetchone()[0]
    b6cbad = con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0251' AND 'V2-Q0300' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    q271 = con.execute("SELECT category_id,client_need,difficulty FROM questions WHERE question_uid='V2-Q0271'").fetchone()
    q287 = con.execute("SELECT stem,correct_answer_json FROM questions WHERE question_uid='V2-Q0287'").fetchone()
    q292 = con.execute("SELECT category_id,client_need,difficulty FROM questions WHERE question_uid='V2-Q0292'").fetchone()
    con.close()

    nextp = json.loads(PENDING.read_text(encoding="utf-8"))
    assert integrity == "ok", integrity
    assert total == 3525, total
    assert verified >= 881, verified
    assert ready == 0, ready
    assert gate and gate[0] == "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA", gate
    assert policy and policy[0] == "REQUIRED_11_DIMENSIONS_FOR_EVERY_QUESTION", policy
    assert records == verified, (records, verified)
    assert passed + pending_gate == records, (passed, pending_gate, records)
    assert meta["batch001_q0001_q0050_final_gate"] and meta["batch001_q0001_q0050_final_gate"][0] == "PASS_50_OF_50_2026_08_14" and b1 == 50
    assert meta["batch002_q0051_q0100_rule1_final_gate"] and meta["batch002_q0051_q0100_rule1_final_gate"][0] == "PASS_50_OF_50_2026_08_14_RULE1_ITEM_BY_ITEM" and b2 == 50 and b2m == 50
    assert meta["batch003_q0101_q0150_rule1_final_gate"] and meta["batch003_q0101_q0150_rule1_final_gate"][0] == "PASS_50_OF_50_2026_08_14_RULE1_ITEM_BY_ITEM" and b3 == 50 and b3m == 50
    assert meta["batch004_q0151_q0200_rule1_final_gate"] and meta["batch004_q0151_q0200_rule1_final_gate"][0] == "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15" and b4 == 50 and b4m == 50
    assert meta["batch005_chronological_q0201_q0250_rule1_final_gate"] and meta["batch005_chronological_q0201_q0250_rule1_final_gate"][0] == "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15" and b5c == 50 and b5cm == 50 and b5ce == 50 and b5cbad == 0
    assert meta["batch006_chronological_q0251_q0300_rule1_final_gate"] and meta["batch006_chronological_q0251_q0300_rule1_final_gate"][0] == "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15" and b6c == 50 and b6cm == 50 and b6ce == 50 and b6cncsbn == 14 and b6cbad == 0
    assert q271 == (3, "Safety & Infection Prevention and Control", "easy")
    assert "quiet, awake term newborn" in q287[0].lower() and json.loads(q287[1])["correct_option"] == "A"
    assert q292 == (4, "Health Promotion and Maintenance", "easy")
    assert meta["batch005_q0782_q0831_rule1_final_gate"] and meta["batch005_q0782_q0831_rule1_final_gate"][0] == "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15" and off5 == 50 and off5m == 50
    assert meta["batch006_q0832_q0881_rule1_final_gate"] and meta["batch006_q0832_q0881_rule1_final_gate"][0] == "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_15" and off6 == 50 and off6m == 50
    assert meta["wave25_q0492_q0531_final_gate"] and meta["wave25_q0492_q0531_final_gate"][0] == "PASS_40_OF_40_2026_08_14" and w25 == 40
    assert meta["wave26_q0532_q0581_manual_final_gate"] and meta["wave26_q0532_q0581_manual_final_gate"][0] == "PASS_50_OF_50_2026_08_14_ITEM_BY_ITEM_STRICT_OPTIONS" and w26 == 50 and w26_option == 50
    assert meta["wave27_q0582_q0631_manual_final_gate"] and meta["wave27_q0582_q0631_manual_final_gate"][0] == "PASS_50_OF_50_2026_08_14_ITEM_BY_ITEM_STRICT_OPTIONS" and w27 == 50 and w27_option == 50
    assert nextp.get("range") == [301, 350] and nextp.get("count") == 50, nextp.get("range")
    print(f"CANONICAL_MASTER_VERIFIED integrity={integrity} total={total} verified={verified} batch5_chrono={b5c}/50 batch6_chrono={b6c}/50 manual11={b6cm}/50 evidence11={b6ce}/50 ncsbn={b6cncsbn}/14 bad={b6cbad} next={nextp.get('range')} ready={ready}")


if __name__ == "__main__":
    main()
