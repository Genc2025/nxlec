#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path

BASE_DB = Path("NCLEX_CANONICAL.db")
SOURCE_DB = Path("NCLEX_COMMERCIAL_MASTER_CURRENT.db")
REVIEW_DIR = Path("RULE1_CLEANUP_2000_REVIEWED")
SELECTOR = Path("RULE1_CLEANUP_2000_NEXT_CANDIDATE.json")
EXPECTED_CANONICAL_BLOB = "182a1e979e11d62bebc85c5ceb859056b8812963"
EXPECTED_SOURCE_BLOB = "07e335d471ef1b4689406ba41eb98eaa2ca41472"
EXPECTED_TOTAL_QUESTIONS = 2000
EXPECTED_CANDIDATES = 1322
KEYS = ["A", "B", "C", "D"]
GATES = [
    "source_authority_verified", "currentness_verified", "exact_locator_verified",
    "stem_verified", "correct_answer_verified", "distractors_verified",
    "rationale_verified", "educational_objective_verified", "ambiguity_verified",
    "second_answer_excluded", "cueing_verified", "blueprint_verified",
    "independent_qa_passed", "no_unresolved_conflict",
]
CANON_CLIENT = {
    "Management of Care": "Management of Care",
    "Safety & Infection Prevention and Control": "Safety and Infection Prevention and Control",
    "Safety and Infection Prevention and Control": "Safety and Infection Prevention and Control",
    "Health Promotion and Maintenance": "Health Promotion and Maintenance",
    "Psychosocial Integrity": "Psychosocial Integrity",
    "Basic Care and Comfort": "Basic Care and Comfort",
    "Pharmacological and Parenteral Therapies": "Pharmacological and Parenteral Therapies",
    "Reduction of Risk Potential": "Reduction of Risk Potential",
    "Physiological Adaptation": "Physiological Adaptation",
}
CANON_BP_TITLE = "2026 NCLEX-RN Test Plan"
CANON_BP_VERSION = "Effective April 1, 2026 through March 31, 2029"


def cjson(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def payload_from_row(r: sqlite3.Row) -> dict:
    return {
        "question_uid": r["question_uid"], "source_bank": r["source_bank"],
        "source_table": r["source_table"], "source_id": r["source_id"], "mode": r["mode"],
        "case_uid": r["case_uid"], "original_sequence": r["original_sequence"],
        "official_case_slot": r["official_case_slot"], "slot_variant": r["slot_variant"],
        "category_id": r["category_id"], "client_need": r["client_need"], "specialty": r["specialty"],
        "difficulty": r["difficulty"], "cjmm_skill": r["cjmm_skill"], "item_type_raw": r["item_type_raw"],
        "renderer_type": r["renderer_type"], "stem": r["stem"],
        "item_data": json.loads(r["item_data_json"]), "correct_answer": json.loads(r["correct_answer_json"]),
        "rationale": r["rationale"], "scoring_rule": r["scoring_rule"],
        "educational_objective": r["educational_objective"],
        "source_organization": r["source_organization"], "source_document_title": r["source_document_title"],
        "source_version_date": r["source_version_date"], "source_accessed_date": r["source_accessed_date"],
        "source_locator": r["source_locator"], "source_url": r["source_url"],
        "source_claim_supported": r["source_claim_supported"],
        "blueprint_source_organization": r["blueprint_source_organization"],
        "blueprint_document_title": r["blueprint_document_title"], "blueprint_version": r["blueprint_version"],
        "blueprint_locator": r["blueprint_locator"], "blueprint_url": r["blueprint_url"],
        "blueprint_topic": r["blueprint_topic"], "stable_sort_key": r["stable_sort_key"],
        "source_db_filename": r["source_db_filename"], "source_db_blob_sha": r["source_db_blob_sha"],
        "source_original": json.loads(r["source_original_json"]), "correction_summary": r["correction_summary"],
        "audit_status": r["audit_status"], "second_pass_status": r["second_pass_status"],
        "audit_date_utc": r["audit_date_utc"], "audit_reviewer": r["audit_reviewer"],
        "gates": {g: int(r[g]) for g in GATES}, "audit_findings": json.loads(r["audit_findings_json"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected-reviewed", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    output = Path(args.output)
    report_path = Path(args.report)

    canonical_blob = git_blob(str(BASE_DB))
    source_blob = git_blob(str(SOURCE_DB))
    if canonical_blob != EXPECTED_CANONICAL_BLOB:
        raise SystemExit(f"BLOCKED canonical blob {canonical_blob}")
    if source_blob != EXPECTED_SOURCE_BLOB:
        raise SystemExit(f"BLOCKED source blob {source_blob}")

    selector = json.loads(SELECTOR.read_text(encoding="utf-8"))
    selector_reviewed = int(selector["reviewed_staging_uid_count"])
    candidate_total = int(selector["candidate_uid_count_from_scan"])
    if selector_reviewed != args.expected_reviewed:
        raise SystemExit(f"BLOCKED selector reviewed={selector_reviewed}, expected={args.expected_reviewed}")
    if candidate_total != EXPECTED_CANDIDATES:
        raise SystemExit(f"BLOCKED candidate total {candidate_total}")

    review_files = sorted(REVIEW_DIR.glob("*.json"))
    reviews = []
    for path in review_files:
        obj = json.loads(path.read_text(encoding="utf-8"))
        uid = obj.get("question_uid")
        if not uid:
            raise SystemExit(f"BLOCKED missing question_uid in {path}")
        if obj.get("status") != "FINAL_QA_PASS" or obj.get("audit_status") != "FINAL_QA_PASS":
            raise SystemExit(f"BLOCKED non-final review {uid}")
        if obj.get("second_pass_status") != "PASS":
            raise SystemExit(f"BLOCKED second pass {uid}")
        gates = obj.get("gates") or {}
        missing_gates = [g for g in GATES if int(gates.get(g, 0)) != 1]
        if missing_gates:
            raise SystemExit(f"BLOCKED gates {uid}: {missing_gates}")
        reviews.append(obj)

    uids = [r["question_uid"] for r in reviews]
    duplicates = sorted(uid for uid, n in Counter(uids).items() if n != 1)
    if duplicates:
        raise SystemExit(f"BLOCKED duplicate review UIDs: {duplicates[:20]}")
    if len(reviews) != args.expected_reviewed:
        raise SystemExit(f"BLOCKED reviewed files={len(reviews)}, expected={args.expected_reviewed}")

    shutil.copyfile(BASE_DB, output)
    con = sqlite3.connect(output)
    con.row_factory = sqlite3.Row
    try:
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise SystemExit("BLOCKED integrity before")
        total_before = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if total_before != EXPECTED_TOTAL_QUESTIONS:
            raise SystemExit(f"BLOCKED expected {EXPECTED_TOTAL_QUESTIONS} questions, got {total_before}")

        columns = {r[1] for r in con.execute("PRAGMA table_info(questions)")}
        required_cols = {
            "question_uid", "category_id", "client_need", "difficulty", "stem", "item_data_json",
            "correct_answer_json", "rationale", "educational_objective", "source_organization",
            "source_document_title", "source_version_date", "source_accessed_date", "source_locator",
            "source_url", "source_claim_supported", "blueprint_document_title", "blueprint_version",
            "blueprint_locator", "blueprint_url", "blueprint_topic", "correction_summary",
            "audit_status", "second_pass_status", "audit_findings_json", "payload_sha256",
            *GATES,
        }
        missing_cols = sorted(required_cols - columns)
        if missing_cols:
            raise SystemExit(f"BLOCKED missing DB columns: {missing_cols}")

        db_uids = {r[0] for r in con.execute("SELECT question_uid FROM questions")}
        missing_uids = sorted(set(uids) - db_uids)
        if missing_uids:
            raise SystemExit(f"BLOCKED review UIDs missing from DB: {missing_uids[:20]}")

        con.execute("BEGIN IMMEDIATE")
        applied = 0
        for review in reviews:
            uid = review["question_uid"]
            row = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
            if row is None:
                raise SystemExit(f"BLOCKED missing row {uid}")

            item_data = json.loads(row["item_data_json"])
            correct_answer = json.loads(row["correct_answer_json"])
            options = review.get("options")
            if not isinstance(options, dict) or sorted(options) != KEYS:
                raise SystemExit(f"BLOCKED malformed options {uid}")
            correct_option = review.get("correct_option")
            if correct_option not in KEYS:
                raise SystemExit(f"BLOCKED malformed correct_option {uid}")
            if not str(options[correct_option]).strip():
                raise SystemExit(f"BLOCKED empty correct answer text {uid}")
            item_data["options"] = {k: options[k] for k in KEYS}
            correct_answer["correct_option"] = correct_option

            client_need = review.get("client_need", row["client_need"])
            if client_need not in CANON_CLIENT:
                raise SystemExit(f"BLOCKED unknown client need {uid}: {client_need}")
            difficulty = review.get("difficulty", row["difficulty"])
            if difficulty == "moderate":
                difficulty = "medium"
            if difficulty not in {"easy", "medium", "hard"}:
                raise SystemExit(f"BLOCKED difficulty {uid}: {difficulty}")

            vals = {
                "category_id": review.get("category_id", row["category_id"]),
                "client_need": CANON_CLIENT[client_need],
                "difficulty": difficulty,
                "stem": review["stem"],
                "item_data_json": cjson(item_data),
                "correct_answer_json": cjson(correct_answer),
                "rationale": review["rationale"],
                "educational_objective": review["educational_objective"],
                "source_organization": review["source_organization"],
                "source_document_title": review["source_document_title"],
                "source_version_date": review["source_version_date"],
                "source_accessed_date": review["source_accessed_date"],
                "source_locator": review["source_locator"],
                "source_url": review["source_url"],
                "source_claim_supported": review["source_claim_supported"],
                "blueprint_document_title": CANON_BP_TITLE,
                "blueprint_version": CANON_BP_VERSION,
                "blueprint_locator": review.get("blueprint_locator", row["blueprint_locator"]),
                "blueprint_url": review.get("blueprint_url", row["blueprint_url"]),
                "blueprint_topic": review.get("blueprint_topic", review.get("client_need", row["blueprint_topic"])),
                "correction_summary": review.get("correction_summary", row["correction_summary"]),
                "audit_status": "FINAL_QA_PASS",
                "second_pass_status": "PASS",
                "audit_findings_json": cjson(review.get("audit_findings", {})),
            }
            for g in GATES:
                vals[g] = 1
            sets = ",".join(f"{k}=?" for k in vals)
            con.execute(f"UPDATE questions SET {sets} WHERE question_uid=?", [*vals.values(), uid])

            updated = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
            payload_sha = hashlib.sha256(cjson(payload_from_row(updated)).encode("utf-8")).hexdigest()
            con.execute("UPDATE questions SET payload_sha256=? WHERE question_uid=?", (payload_sha, uid))
            applied += 1

        con.commit()

        total_after = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        duplicate_uid_groups = con.execute(
            "SELECT COUNT(*) FROM (SELECT question_uid, COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)"
        ).fetchone()[0]
        applied_rows = con.execute(
            f"SELECT COUNT(*) FROM questions WHERE question_uid IN ({','.join('?' for _ in uids)})",
            uids,
        ).fetchone()[0]
        if total_after != total_before or total_after != EXPECTED_TOTAL_QUESTIONS:
            raise SystemExit(f"BLOCKED total changed {total_before}->{total_after}")
        if integrity != "ok" or duplicate_uid_groups != 0 or applied_rows != args.expected_reviewed:
            raise SystemExit(
                f"BLOCKED postcheck integrity={integrity} dup={duplicate_uid_groups} applied_rows={applied_rows}"
            )
    finally:
        con.close()

    report = {
        "status": "RULE1_REVIEWED_SNAPSHOT_PASS",
        "input_canonical_file": str(BASE_DB),
        "input_canonical_blob": canonical_blob,
        "source_db_file": str(SOURCE_DB),
        "source_db_blob": source_blob,
        "output_db_file": str(output),
        "output_db_sha256": sha256_file(output),
        "total_questions_before": total_before,
        "total_questions_after": total_after,
        "candidate_uid_count_from_scan": candidate_total,
        "reviewed_staging_uid_count": selector_reviewed,
        "review_files_validated": len(reviews),
        "reviewed_changes_applied": applied,
        "remaining_cleanup_candidates": candidate_total - selector_reviewed,
        "next_selector_uid": (selector.get("candidate") or {}).get("question_uid"),
        "missing_review_uids": 0,
        "duplicate_review_uids": 0,
        "duplicate_db_uid_groups": duplicate_uid_groups,
        "sqlite_integrity_check": integrity,
        "canonical_db_modified": False,
        "source_db_modified": False,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RULE1_REVIEWED_SNAPSHOT=" + cjson(report))


if __name__ == "__main__":
    main()
