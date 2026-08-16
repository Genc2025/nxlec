#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("NCLEX_COMMERCIAL_MASTER_CURRENT.db")
CANONICAL = Path("NCLEX_CANONICAL.db")
APPROVED = Path("approved_items")
REPORT = Path("RULE1_BATCH_Q0351_Q0400_REPORT.json")
EXPECTED_SOURCE_BLOB = "07e335d471ef1b4689406ba41eb98eaa2ca41472"
EXPECTED_CANONICAL_BLOB = "fb6d0cd1be359bbb7198bf149b286af779565927"

GATES = [
    "source_authority_verified", "currentness_verified", "exact_locator_verified", "stem_verified",
    "correct_answer_verified", "distractors_verified", "rationale_verified", "educational_objective_verified",
    "ambiguity_verified", "second_answer_excluded", "cueing_verified", "blueprint_verified",
    "independent_qa_passed", "no_unresolved_conflict",
]

REQUIRED_TOP = [
    "question_uid", "source_bank", "source_table", "source_id", "mode", "category_id", "client_need",
    "difficulty", "item_type_raw", "renderer_type", "stem", "item_data", "correct_answer", "rationale",
    "educational_objective", "source_organization", "source_document_title", "source_version_date",
    "source_accessed_date", "source_locator", "source_url", "source_claim_supported",
    "blueprint_source_organization", "blueprint_document_title", "blueprint_version", "blueprint_locator",
    "blueprint_url", "blueprint_topic", "stable_sort_key", "source_db_filename", "source_db_blob_sha",
    "source_original", "correction_summary", "audit_status", "second_pass_status", "audit_date_utc",
    "audit_reviewer", "gates", "audit_findings",
]
OPTIONAL_NULL = {"case_uid", "original_sequence", "official_case_slot", "slot_variant", "specialty", "cjmm_skill", "scoring_rule"}
JSON_COLS = ["item_data_json", "correct_answer_json", "source_original_json", "audit_findings_json"]


def sh(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def cjson(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload_sha(payload: dict) -> str:
    return hashlib.sha256(cjson(payload).encode("utf-8")).hexdigest()


def protected_fingerprint(con: sqlite3.Connection) -> tuple[str, int]:
    rows = con.execute(
        "SELECT * FROM questions WHERE question_uid BETWEEN 'V2-Q0001' AND 'V2-Q0350' ORDER BY question_uid"
    ).fetchall()
    packed = [list(row) for row in rows]
    digest = hashlib.sha256(json.dumps(packed, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    return digest, len(rows)


def db_values(payload: dict, created_at: str) -> dict:
    p = payload
    return {
        "question_uid": p["question_uid"], "source_bank": p["source_bank"], "source_table": p["source_table"],
        "source_id": p["source_id"], "mode": p["mode"], "case_uid": p.get("case_uid"),
        "original_sequence": p.get("original_sequence"), "official_case_slot": p.get("official_case_slot"),
        "slot_variant": p.get("slot_variant"), "category_id": p["category_id"], "client_need": p["client_need"],
        "specialty": p.get("specialty"), "difficulty": p["difficulty"], "cjmm_skill": p.get("cjmm_skill"),
        "item_type_raw": p["item_type_raw"], "renderer_type": p["renderer_type"], "stem": p["stem"],
        "item_data_json": cjson(p["item_data"]), "correct_answer_json": cjson(p["correct_answer"]),
        "rationale": p["rationale"], "scoring_rule": p.get("scoring_rule"),
        "educational_objective": p["educational_objective"], "source_organization": p["source_organization"],
        "source_document_title": p["source_document_title"], "source_version_date": p["source_version_date"],
        "source_accessed_date": p["source_accessed_date"], "source_locator": p["source_locator"],
        "source_url": p["source_url"], "source_claim_supported": p["source_claim_supported"],
        "blueprint_source_organization": p["blueprint_source_organization"],
        "blueprint_document_title": p["blueprint_document_title"], "blueprint_version": p["blueprint_version"],
        "blueprint_locator": p["blueprint_locator"], "blueprint_url": p["blueprint_url"],
        "blueprint_topic": p["blueprint_topic"], "stable_sort_key": p["stable_sort_key"],
        "source_db_filename": p["source_db_filename"], "source_db_blob_sha": p["source_db_blob_sha"],
        "source_original_json": cjson(p["source_original"]), "correction_summary": p["correction_summary"],
        "audit_status": p["audit_status"], "second_pass_status": p["second_pass_status"],
        "audit_date_utc": p["audit_date_utc"], "audit_reviewer": p["audit_reviewer"],
        **{gate: int(p["gates"][gate]) for gate in GATES},
        "audit_findings_json": cjson(p["audit_findings"]), "payload_sha256": payload_sha(p),
        "created_at_utc": created_at,
    }


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    expected_uids = [f"V2-Q{i:04d}" for i in range(351, 401)]
    expected_files = {f"{uid}.json" for uid in expected_uids}
    actual_files = {path.name for path in APPROVED.glob("*.json")}
    if actual_files != expected_files:
        fail(f"approved_items mismatch count={len(actual_files)} missing={sorted(expected_files-actual_files)} extra={sorted(actual_files-expected_files)}")

    payloads: list[dict] = []
    for uid in expected_uids:
        path = APPROVED / f"{uid}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"Bad JSON {path}: {exc}")
        missing = [key for key in REQUIRED_TOP if key not in payload or (payload[key] in ("", None) and key not in OPTIONAL_NULL)]
        if missing:
            fail(f"{uid} missing required payload fields: {missing}")
        if payload["question_uid"] != uid:
            fail(f"{uid} filename/payload UID mismatch")
        if payload["source_bank"] != "v2" or payload["source_id"] != int(uid[-4:]):
            fail(f"{uid} source identity mismatch")
        if payload["audit_status"] != "FINAL_QA_PASS" or payload["second_pass_status"] != "PASS":
            fail(f"{uid} final status invalid")
        bad_gates = [gate for gate in GATES if payload["gates"].get(gate) != 1]
        if bad_gates:
            fail(f"{uid} failed gates: {bad_gates}")
        if payload["source_db_filename"] != SOURCE.name or payload["source_db_blob_sha"] != EXPECTED_SOURCE_BLOB:
            fail(f"{uid} source DB metadata mismatch")
        payloads.append(payload)

    if len(payloads) != 50 or len({p["question_uid"] for p in payloads}) != 50:
        fail("approved payload count/UID uniqueness failure")

    head_source = sh("git", "rev-parse", f"HEAD:{SOURCE}")
    head_canonical = sh("git", "rev-parse", f"HEAD:{CANONICAL}")
    source_hash_before = sh("git", "hash-object", str(SOURCE))
    canonical_hash_before = sh("git", "hash-object", str(CANONICAL))
    if head_source != EXPECTED_SOURCE_BLOB or source_hash_before != EXPECTED_SOURCE_BLOB:
        fail(f"Source blob moved HEAD={head_source} file={source_hash_before}")
    if head_canonical != EXPECTED_CANONICAL_BLOB or canonical_hash_before != EXPECTED_CANONICAL_BLOB:
        fail(f"Canonical base blob moved HEAD={head_canonical} file={canonical_hash_before}")

    src = sqlite3.connect(SOURCE)
    src.row_factory = sqlite3.Row
    con = sqlite3.connect(CANONICAL)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")

    if src.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        fail("source PRAGMA integrity_check failed")
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        fail("canonical pre-write PRAGMA integrity_check failed")

    pre_count = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    pre_dup = con.execute(
        "SELECT COUNT(*) FROM (SELECT question_uid, COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)"
    ).fetchone()[0]
    if pre_count != 350 or pre_dup != 0:
        fail(f"canonical precondition failed count={pre_count} duplicate_uid={pre_dup}")
    existing_batch = [row[0] for row in con.execute(
        "SELECT question_uid FROM questions WHERE question_uid BETWEEN 'V2-Q0351' AND 'V2-Q0400' ORDER BY question_uid"
    )]
    if existing_batch:
        fail(f"batch UID already present: {existing_batch}")

    protected_before, protected_count = protected_fingerprint(con)
    if protected_count != 350:
        fail(f"protected Q0001-Q0350 count={protected_count}, expected 350")

    # Validate each approved payload against the real immutable source row before any write.
    for payload in payloads:
        row = src.execute("SELECT * FROM questions WHERE question_uid=?", (payload["question_uid"],)).fetchone()
        if row is None:
            fail(f"source row missing {payload['question_uid']}")
        if row["source_bank"] != payload["source_bank"] or row["source_id"] != payload["source_id"] or row["source_table"] != payload["source_table"]:
            fail(f"source identity moved {payload['question_uid']}")
        if row["stable_sort_key"] != payload["stable_sort_key"]:
            fail(f"stable_sort_key mismatch {payload['question_uid']}")
        original = payload["source_original"]
        exact = {
            "stem": row["stem"] == original["stem"],
            "options": json.loads(row["item_data_json"])["options"] == original["options"],
            "correct_option": json.loads(row["correct_answer_json"])["correct_option"] == original["correct_option"],
            "rationale": row["rationale"] == original["rationale"],
            "source_url": row["source_url"] == original["source_url"],
            "source_detail": row["source_detail"] == original["source_detail"],
            "difficulty": row["difficulty"] == original["difficulty"],
        }
        if not all(exact.values()):
            fail(f"source snapshot mismatch {payload['question_uid']}: {exact}")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    # Exactly one SQLite transaction for the 50 approved inserts.
    try:
        con.execute("BEGIN IMMEDIATE")
        for payload in payloads:
            values = db_values(payload, now)
            columns = list(values)
            con.execute(
                f"INSERT INTO questions ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [values[column] for column in columns],
            )
        con.commit()
    except Exception:
        con.rollback()
        raise

    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    post_count = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    duplicate_uid = con.execute(
        "SELECT COUNT(*) FROM (SELECT question_uid, COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)"
    ).fetchone()[0]
    if integrity != "ok" or post_count != 400 or duplicate_uid != 0:
        fail(f"post-write core failure integrity={integrity} count={post_count} duplicate_uid={duplicate_uid}")

    schema = list(con.execute("PRAGMA table_info(questions)"))
    required_db_cols = {row[1] for row in schema if row[3] == 1}
    required_db_cols.add("question_uid")
    missing_required = 0
    for row in con.execute("SELECT * FROM questions"):
        for column in required_db_cols:
            value = row[column]
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_required += 1
    if missing_required != 0:
        fail(f"missing_required={missing_required}")

    bad_json = 0
    for row in con.execute("SELECT * FROM questions"):
        for column in JSON_COLS:
            try:
                json.loads(row[column])
            except Exception:
                bad_json += 1
    if bad_json != 0:
        fail(f"bad_json={bad_json}")

    gate_predicate = " OR ".join(f"{gate}<>1" for gate in GATES)
    failed_gate_rows = con.execute(
        f"SELECT COUNT(*) FROM questions WHERE audit_status<>'FINAL_QA_PASS' OR second_pass_status<>'PASS' OR {gate_predicate}"
    ).fetchone()[0]
    if failed_gate_rows != 0:
        fail(f"rows failing FINAL_QA_PASS/PASS/14 gates={failed_gate_rows}")

    reread_exact = 0
    mismatches: dict[str, list[str]] = {}
    for payload in payloads:
        saved = con.execute("SELECT * FROM questions WHERE question_uid=?", (payload["question_uid"],)).fetchone()
        expected = db_values(payload, now)
        different = [column for column, value in expected.items() if saved[column] != value]
        if different:
            mismatches[payload["question_uid"]] = different
        else:
            reread_exact += 1
    if reread_exact != 50:
        fail(f"reread_exact={reread_exact}/50 mismatches={mismatches}")

    protected_after, protected_count_after = protected_fingerprint(con)
    protected_unchanged = (
        protected_before == protected_after and protected_count == protected_count_after == 350
    )
    if not protected_unchanged:
        fail("Q0001-Q0350 changed during batch")

    completed = {row[0] for row in con.execute("SELECT question_uid FROM questions")}
    next_uid = None
    for row in src.execute(
        "SELECT question_uid FROM questions WHERE source_bank='v2' ORDER BY stable_sort_key ASC, source_id ASC"
    ):
        if row["question_uid"] not in completed:
            next_uid = row["question_uid"]
            break
    if next_uid != "V2-Q0401":
        fail(f"next UID expected V2-Q0401, got {next_uid}")

    con.close()
    src.close()

    source_hash_after = sh("git", "hash-object", str(SOURCE))
    source_diff = sh("git", "diff", "--name-only", "--", str(SOURCE))
    if source_hash_after != EXPECTED_SOURCE_BLOB or source_diff:
        fail(f"source DB changed hash={source_hash_after} diff={source_diff!r}")

    canonical_new_blob = sh("git", "hash-object", str(CANONICAL))
    report = {
        "status": "PASS",
        "batch": "V2-Q0351-V2-Q0400",
        "approved_items_count": 50,
        "approved_json_valid": 50,
        "canonical_base_blob": EXPECTED_CANONICAL_BLOB,
        "canonical_new_blob": canonical_new_blob,
        "source_blob_before": EXPECTED_SOURCE_BLOB,
        "source_blob_after": source_hash_after,
        "source_db_unchanged": True,
        "canonical_integrity": integrity,
        "canonical_question_count_before": pre_count,
        "canonical_question_count_after": post_count,
        "duplicate_uid_count": duplicate_uid,
        "missing_required_count": missing_required,
        "bad_json_count": bad_json,
        "reread_exact": "50/50",
        "all_14_gates_pass_rows": "400/400",
        "protected_q0001_q0350_unchanged": protected_unchanged,
        "protected_q0001_q0350_fingerprint_before": protected_before,
        "protected_q0001_q0350_fingerprint_after": protected_after,
        "next_uid": next_uid,
        "single_sqlite_transaction": True,
        "verified_at_utc": now,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
