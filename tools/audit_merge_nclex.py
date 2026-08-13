#!/usr/bin/env python3
"""Build a commercial-ready NCLEX catalog from the two repository SQLite banks.

This pipeline preserves every source row, performs structural validation and exact
deduplication, keeps NGN case context intact, and separates catalog ordering from
exam-delivery rules. It does not certify clinical correctness, copyright ownership,
or affiliation with NCSBN/NCLEX.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "nclex question bank v2 inprogress 5.db"
NGN_PATH = ROOT / "nclex ngn bank 75of75 ALL7formats FINAL.db"
OUT_DB = ROOT / "nclex_commercial_merged.db"
OUT_JSON = ROOT / "NCLEX_AUDIT_REPORT.json"
OUT_MD = ROOT / "NCLEX_AUDIT_REPORT.md"

BLUEPRINT = {
    2: (1, "MGMT_CARE", "Management of Care", 15.0, 21.0, 18.0),
    3: (2, "SAFETY_INFECTION", "Safety & Infection Prevention and Control", 10.0, 16.0, 13.0),
    4: (3, "HEALTH_PROMO", "Health Promotion and Maintenance", 6.0, 12.0, 9.0),
    5: (4, "PSYCHOSOCIAL", "Psychosocial Integrity", 6.0, 12.0, 9.0),
    7: (5, "BASIC_CARE", "Basic Care and Comfort", 6.0, 12.0, 9.0),
    8: (6, "PHARM", "Pharmacological and Parenteral Therapies", 13.0, 19.0, 16.0),
    9: (7, "RISK_REDUCTION", "Reduction of Risk Potential", 9.0, 15.0, 12.0),
    10: (8, "PHYS_ADAPT", "Physiological Adaptation", 11.0, 17.0, 14.0),
}

TYPE_FAMILY = {
    "highlight": "highlight",
    "extended_multiple_response": "multiple_response",
    "matrix_grid": "matrix_grid",
    "bowtie": "bow_tie",
    "cloze_dropdown": "cloze_dropdown",
    "extended_drag_drop": "ordered_response",
    "trend": "trend",
}

SCORING_FAMILY = {
    "highlight": "plus_minus",
    "extended_multiple_response": "plus_minus",
    "matrix_grid": "zero_one_component",
    "cloze_dropdown": "zero_one_component",
    "trend": "zero_one_component",
    "bowtie": "review_required",
    "extended_drag_drop": "review_required",
}


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def hash_text(text: str) -> str:
    return hashlib.sha256(normalize(text).encode()).hexdigest()


def path_depth(url: str) -> int:
    try:
        path = urlparse(url or "").path.strip("/")
        return len([part for part in path.split("/") if part]) if path else 0
    except Exception:
        return -1


def integrity(path: Path) -> str:
    db = sqlite3.connect(path)
    try:
        return str(db.execute("PRAGMA integrity_check").fetchone()[0])
    finally:
        db.close()


def valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def create_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
    PRAGMA foreign_keys=ON;
    CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE test_blueprint_2026(
      category_id INTEGER PRIMARY KEY,
      blueprint_rank INTEGER NOT NULL,
      code TEXT NOT NULL,
      category_name TEXT NOT NULL,
      min_pct REAL NOT NULL,
      max_pct REAL NOT NULL,
      target_midpoint_pct REAL NOT NULL
    );
    CREATE TABLE core_questions(
      id INTEGER PRIMARY KEY,
      stable_uid TEXT UNIQUE NOT NULL,
      category_id INTEGER NOT NULL,
      blueprint_rank INTEGER NOT NULL,
      fingerprint_id INTEGER,
      question_text TEXT NOT NULL,
      option_a TEXT NOT NULL,
      option_b TEXT NOT NULL,
      option_c TEXT NOT NULL,
      option_d TEXT NOT NULL,
      correct_option TEXT NOT NULL,
      explanation TEXT NOT NULL,
      source_name TEXT NOT NULL,
      source_detail TEXT NOT NULL,
      source_url TEXT NOT NULL,
      source_url_depth INTEGER NOT NULL,
      source_traceability TEXT NOT NULL,
      difficulty TEXT NOT NULL,
      item_type TEXT NOT NULL,
      batch_number INTEGER,
      date_created TEXT,
      source_verified_flag INTEGER NOT NULL,
      exact_stem_hash TEXT NOT NULL,
      duplicate_of_uid TEXT,
      active INTEGER NOT NULL DEFAULT 1,
      structural_status TEXT NOT NULL,
      independent_clinical_status TEXT NOT NULL DEFAULT 'NOT_VERIFIED',
      ip_status TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED',
      FOREIGN KEY(category_id) REFERENCES test_blueprint_2026(category_id)
    );
    CREATE TABLE ngn_case_studies(
      id INTEGER PRIMARY KEY,
      stable_uid TEXT UNIQUE NOT NULL,
      category_id INTEGER NOT NULL,
      blueprint_rank INTEGER NOT NULL,
      title TEXT NOT NULL,
      specialty TEXT NOT NULL,
      setting TEXT NOT NULL,
      client_profile TEXT NOT NULL,
      stage1_scenario TEXT NOT NULL,
      stage2_scenario TEXT,
      stage3_scenario TEXT,
      difficulty TEXT NOT NULL,
      source_name TEXT,
      source_url TEXT,
      source_url_depth INTEGER NOT NULL,
      date_created TEXT,
      source_verified_flag INTEGER NOT NULL,
      structural_status TEXT NOT NULL,
      independent_clinical_status TEXT NOT NULL DEFAULT 'NOT_VERIFIED',
      ip_status TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED',
      FOREIGN KEY(category_id) REFERENCES test_blueprint_2026(category_id)
    );
    CREATE TABLE ngn_case_items(
      id INTEGER PRIMARY KEY,
      stable_uid TEXT UNIQUE NOT NULL,
      case_study_id INTEGER NOT NULL,
      sequence INTEGER NOT NULL,
      cjmm_skill TEXT NOT NULL,
      item_type TEXT NOT NULL,
      item_family TEXT NOT NULL,
      stem TEXT NOT NULL,
      item_data_json TEXT NOT NULL,
      correct_answer_json TEXT NOT NULL,
      rationale TEXT NOT NULL,
      original_scoring_rule TEXT NOT NULL,
      scoring_family TEXT NOT NULL,
      practice_use INTEGER NOT NULL DEFAULT 1,
      simulation_use INTEGER NOT NULL,
      supplemental_practice INTEGER NOT NULL,
      structural_status TEXT NOT NULL,
      independent_clinical_status TEXT NOT NULL DEFAULT 'NOT_VERIFIED',
      ip_status TEXT NOT NULL DEFAULT 'REVIEW_REQUIRED',
      FOREIGN KEY(case_study_id) REFERENCES ngn_case_studies(id)
    );
    CREATE TABLE unified_catalog(
      catalog_order INTEGER PRIMARY KEY,
      stable_uid TEXT UNIQUE NOT NULL,
      pool TEXT NOT NULL,
      source_id INTEGER NOT NULL,
      case_study_id INTEGER,
      case_sequence INTEGER,
      category_id INTEGER NOT NULL,
      blueprint_rank INTEGER NOT NULL,
      item_type TEXT NOT NULL,
      question_text TEXT NOT NULL,
      difficulty TEXT,
      active INTEGER NOT NULL,
      practice_use INTEGER NOT NULL,
      simulation_use INTEGER NOT NULL,
      structural_status TEXT NOT NULL,
      independent_clinical_status TEXT NOT NULL,
      ip_status TEXT NOT NULL
    );
    CREATE TABLE audit_issues(
      issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_type TEXT NOT NULL,
      stable_uid TEXT,
      severity TEXT NOT NULL,
      issue_code TEXT NOT NULL,
      detail TEXT NOT NULL
    );
    CREATE TABLE test_generation_rules(
      rule_key TEXT PRIMARY KEY,
      rule_json TEXT NOT NULL
    );
    CREATE VIEW v_active_core_questions AS
      SELECT * FROM core_questions WHERE active=1 AND structural_status='PASS';
    CREATE VIEW v_ngn_practice_items AS
      SELECT i.*, c.category_id, c.blueprint_rank, c.title AS case_title
      FROM ngn_case_items i JOIN ngn_case_studies c ON c.id=i.case_study_id
      WHERE i.practice_use=1 AND i.structural_status='PASS';
    CREATE VIEW v_ngn_simulation_items AS
      SELECT i.*, c.category_id, c.blueprint_rank, c.title AS case_title
      FROM ngn_case_items i JOIN ngn_case_studies c ON c.id=i.case_study_id
      WHERE i.simulation_use=1 AND i.structural_status='PASS';
    CREATE INDEX idx_core_category ON core_questions(category_id, active);
    CREATE INDEX idx_core_hash ON core_questions(exact_stem_hash);
    CREATE INDEX idx_ngn_case_seq ON ngn_case_items(case_study_id, sequence);
    CREATE INDEX idx_catalog_pool_category ON unified_catalog(pool, category_id, active);
    CREATE INDEX idx_issues_uid ON audit_issues(stable_uid, issue_code);
    """)


def copy_blueprint(db: sqlite3.Connection) -> None:
    for category_id, (rank, code, name, lo, hi, midpoint) in BLUEPRINT.items():
        db.execute(
            "INSERT INTO test_blueprint_2026 VALUES(?,?,?,?,?,?,?)",
            (category_id, rank, code, name, lo, hi, midpoint),
        )


def load_core(db: sqlite3.Connection) -> dict:
    src = sqlite3.connect(CORE_PATH)
    src.row_factory = sqlite3.Row
    rows = src.execute("SELECT * FROM questions ORDER BY id").fetchall()
    category_counts = Counter()
    difficulty_counts = Counter()
    answer_counts = Counter()
    completeness = Counter()
    hashes = defaultdict(list)

    for r in rows:
        q = dict(r)
        uid = f"MCQ-{q['id']:04d}"
        h = hash_text(q["question_text"])
        hashes[h].append(q["id"])
        depth = path_depth(q["source_url"])
        trace = "HOMEPAGE_ONLY" if depth == 0 else "DEEP_LINK"
        rank = BLUEPRINT[q["category_id"]][0]
        structural = "PASS"
        required = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation", "source_name", "source_detail", "source_url"]
        if any(q.get(k) in (None, "") for k in required) or q["correct_option"] not in {"A", "B", "C", "D"}:
            structural = "REVIEW"
        db.execute("""
          INSERT INTO core_questions(
            id,stable_uid,category_id,blueprint_rank,fingerprint_id,question_text,
            option_a,option_b,option_c,option_d,correct_option,explanation,
            source_name,source_detail,source_url,source_url_depth,source_traceability,
            difficulty,item_type,batch_number,date_created,source_verified_flag,
            exact_stem_hash,active,structural_status
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            q["id"],uid,q["category_id"],rank,q["fingerprint_id"],q["question_text"],
            q["option_a"],q["option_b"],q["option_c"],q["option_d"],q["correct_option"],q["explanation"],
            q["source_name"],q["source_detail"],q["source_url"],depth,trace,q["difficulty"],
            q["item_type"],q["batch_number"],q["date_created"],int(q["verified"] or 0),h,1,structural
        ))
        category_counts[q["category_id"]] += 1
        difficulty_counts[q["difficulty"]] += 1
        answer_counts[q["correct_option"]] += 1
        if structural != "PASS":
            completeness["structural_review"] += 1
        if depth == 0:
            db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                       ("core_question",uid,"INFO","SOURCE_TRACEABILITY_REVIEW","Source URL points to a site root/homepage; retain source_detail but review locator precision before strong verification claims."))

    exact_groups = []
    for h, ids in hashes.items():
        if len(ids) > 1:
            ids = sorted(ids)
            canonical = ids[0]
            canonical_uid = f"MCQ-{canonical:04d}"
            exact_groups.append(ids)
            for duplicate_id in ids[1:]:
                duplicate_uid = f"MCQ-{duplicate_id:04d}"
                db.execute("UPDATE core_questions SET duplicate_of_uid=?,active=0 WHERE id=?", (canonical_uid, duplicate_id))
                db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                           ("core_question",duplicate_uid,"WARN","EXACT_DUPLICATE_STEM",f"Exact normalized stem duplicate of {canonical_uid}; source row retained but excluded from active commercial pool."))
    src.close()
    return {
        "rows": len(rows),
        "category_counts": dict(category_counts),
        "difficulty_counts": dict(difficulty_counts),
        "answer_counts": dict(answer_counts),
        "exact_duplicate_groups": exact_groups,
        "homepage_only_sources": sum(1 for _ in db.execute("SELECT 1 FROM core_questions WHERE source_traceability='HOMEPAGE_ONLY'")),
        "active_unique": db.execute("SELECT COUNT(*) FROM core_questions WHERE active=1 AND structural_status='PASS'").fetchone()[0],
        "all_verified_flag": db.execute("SELECT MIN(source_verified_flag) FROM core_questions").fetchone()[0] == 1,
    }


def load_ngn(db: sqlite3.Connection) -> dict:
    src = sqlite3.connect(NGN_PATH)
    src.row_factory = sqlite3.Row
    cases = src.execute("SELECT * FROM case_studies ORDER BY id").fetchall()
    items = src.execute("SELECT * FROM case_study_items ORDER BY case_study_id,sequence,id").fetchall()
    standalone_count = src.execute("SELECT COUNT(*) FROM standalone_ngn_items").fetchone()[0]
    by_case = defaultdict(list)
    type_counts = Counter()
    cjmm_counts = Counter()
    category_case_counts = Counter()
    bad_json = []

    for r in cases:
        c = dict(r)
        rank = BLUEPRINT[c["category_id"]][0]
        depth = path_depth(c["source_url"] or "")
        structural = "PASS" if c["title"] and c["client_profile"] and c["stage1_scenario"] else "REVIEW"
        uid = f"NGN-C{c['id']:03d}"
        db.execute("""
          INSERT INTO ngn_case_studies(
            id,stable_uid,category_id,blueprint_rank,title,specialty,setting,client_profile,
            stage1_scenario,stage2_scenario,stage3_scenario,difficulty,source_name,source_url,
            source_url_depth,date_created,source_verified_flag,structural_status
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            c["id"],uid,c["category_id"],rank,c["title"],c["specialty"],c["setting"],c["client_profile"],
            c["stage1_scenario"],c["stage2_scenario"],c["stage3_scenario"],c["difficulty"],c["source_name"],
            c["source_url"],depth,c["date_created"],int(c["verified"] or 0),structural
        ))
        category_case_counts[c["category_id"]] += 1
        if "wikijournalclub.org" in (urlparse(c["source_url"] or "").netloc.lower()):
            db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                       ("ngn_case",uid,"WARN","SECONDARY_SOURCE_REVIEW","Case cites WikiJournalClub for ARDSNet. Replace/augment with the original trial or current primary guideline before commercial clinical verification."))

    for r in items:
        i = dict(r)
        by_case[i["case_study_id"]].append(i)
        type_counts[i["item_type"]] += 1
        cjmm_counts[i["cjmm_skill"]] += 1
        uid = f"NGN-C{i['case_study_id']:03d}-I{i['sequence']:02d}"
        family = TYPE_FAMILY.get(i["item_type"], "other")
        scoring_family = SCORING_FAMILY.get(i["item_type"], "review_required")
        item_json_ok = valid_json(i["item_data_json"])
        answer_json_ok = valid_json(i["correct_answer_json"])
        structural = "PASS" if i["stem"] and i["rationale"] and item_json_ok and answer_json_ok else "REVIEW"
        # The source bank contains two Recognize Cues formats. Preserve all seven for practice,
        # but use only one of sequence 1/2 per case so simulation has six CJMM items per case.
        if i["sequence"] == 1:
            simulation_use = 1 if i["case_study_id"] % 2 == 1 else 0
        elif i["sequence"] == 2:
            simulation_use = 1 if i["case_study_id"] % 2 == 0 else 0
        else:
            simulation_use = 1
        supplemental = 0 if simulation_use else 1
        db.execute("""
          INSERT INTO ngn_case_items(
            id,stable_uid,case_study_id,sequence,cjmm_skill,item_type,item_family,stem,
            item_data_json,correct_answer_json,rationale,original_scoring_rule,scoring_family,
            practice_use,simulation_use,supplemental_practice,structural_status
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            i["id"],uid,i["case_study_id"],i["sequence"],i["cjmm_skill"],i["item_type"],family,i["stem"],
            i["item_data_json"],i["correct_answer_json"],i["rationale"],i["scoring_rule"],scoring_family,
            1,simulation_use,supplemental,structural
        ))
        if not item_json_ok or not answer_json_ok:
            bad_json.append(uid)
            db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                       ("ngn_item",uid,"ERROR","INVALID_JSON","item_data_json or correct_answer_json is invalid JSON."))
        if scoring_family == "review_required":
            db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                       ("ngn_item",uid,"WARN","SCORING_RULE_REVIEW","Original scoring semantics require mapping to a currently supported NCLEX partial-credit scoring method before exact-simulation claims."))

    invalid_cases = []
    for case_id, case_items in sorted(by_case.items()):
        seqs = [x["sequence"] for x in case_items]
        if len(case_items) != 7 or sorted(seqs) != list(range(1,8)):
            invalid_cases.append(case_id)
        case_uid = f"NGN-C{case_id:03d}"
        db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                   ("ngn_case",case_uid,"INFO","SEVEN_FORMAT_PRACTICE_SET","Source case contains seven practice formats, including two Recognize Cues items. Commercial simulation view selects six items while retaining all seven for study mode."))

    if standalone_count == 0:
        db.execute("INSERT INTO audit_issues(entity_type,stable_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)",
                   ("bank",None,"WARN","MISSING_STANDALONE_NGN_POOL","standalone_ngn_items contains 0 rows. The current bank can support case-study NGN practice but not a complete stand-alone clinical-judgment pool."))
    src.close()
    return {
        "case_count": len(cases),
        "case_item_count": len(items),
        "standalone_ngn_count": standalone_count,
        "category_case_counts": dict(category_case_counts),
        "item_type_counts": dict(type_counts),
        "cjmm_counts": dict(cjmm_counts),
        "invalid_case_sequence_sets": invalid_cases,
        "invalid_json_items": bad_json,
        "simulation_item_count": db.execute("SELECT COUNT(*) FROM ngn_case_items WHERE simulation_use=1").fetchone()[0],
        "practice_item_count": db.execute("SELECT COUNT(*) FROM ngn_case_items WHERE practice_use=1").fetchone()[0],
        "all_verified_flag": db.execute("SELECT MIN(source_verified_flag) FROM ngn_case_studies").fetchone()[0] == 1,
    }


def build_catalog(db: sqlite3.Connection) -> None:
    rows = []
    for r in db.execute("""
      SELECT q.stable_uid,'core_mcq',q.id,NULL,NULL,q.category_id,q.blueprint_rank,
             q.item_type,q.question_text,q.difficulty,q.active,1,1,q.structural_status,
             q.independent_clinical_status,q.ip_status
      FROM core_questions q
    """):
        rows.append(tuple(r))
    for r in db.execute("""
      SELECT i.stable_uid,'ngn_case',i.id,i.case_study_id,i.sequence,c.category_id,c.blueprint_rank,
             i.item_type,i.stem,c.difficulty,1,i.practice_use,i.simulation_use,i.structural_status,
             i.independent_clinical_status,i.ip_status
      FROM ngn_case_items i JOIN ngn_case_studies c ON c.id=i.case_study_id
    """):
        rows.append(tuple(r))
    pool_rank = {"core_mcq": 1, "ngn_case": 2}
    rows.sort(key=lambda r: (pool_rank[r[1]], r[6], r[3] or 0, r[4] or 0, r[2]))
    for n, r in enumerate(rows, 1):
        db.execute("INSERT INTO unified_catalog VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (n, *r))


def add_rules(db: sqlite3.Connection) -> None:
    rules = {
        "catalog_order": {
            "purpose": "stable admin/import order only",
            "rule": "pool -> blueprint rank -> case -> sequence/source id",
            "warning": "Do not deliver commercial exams by consecutive catalog_order. Sample by blueprint and randomize where clinically appropriate."
        },
        "core_blueprint_sampling": {
            "targets_pct": {BLUEPRINT[k][2]: BLUEPRINT[k][5] for k in BLUEPRINT},
            "rule": "Use midpoint targets for balanced practice/test generation; allow configurable ranges for longer adaptive simulations."
        },
        "ngn_case_simulation": {
            "case_sets": 3,
            "items_per_case": 6,
            "total_case_items": 18,
            "selection": "Keep each selected case contiguous and in case sequence. Sequences 3-7 always included; use sequence 1 for odd case IDs and sequence 2 for even case IDs to choose one Recognize Cues format."
        },
        "ngn_practice": {
            "items_per_case": 7,
            "rule": "All seven source formats remain available in study/practice mode."
        },
        "commercial_release_gate": {
            "required": ["independent clinical answer/rationale verification", "source locator/currentness review", "IP/licensing review", "scoring-model review for flagged NGN types"],
            "current_status": "NOT_CLEARED_FOR_FINAL_PRODUCTION_CLAIMS"
        }
    }
    db.executemany("INSERT INTO test_generation_rules(rule_key,rule_json) VALUES(?,?)",
                   [(k, json.dumps(v, ensure_ascii=False, sort_keys=True)) for k,v in rules.items()])


def audit_report(db: sqlite3.Connection, core: dict, ngn: dict) -> dict:
    category_rows = db.execute("""
      SELECT b.category_id,b.category_name,b.min_pct,b.max_pct,b.target_midpoint_pct,
             COUNT(q.id) AS core_count,
             ROUND(COUNT(q.id)*100.0/(SELECT COUNT(*) FROM core_questions),2) AS core_pct,
             (SELECT COUNT(*) FROM ngn_case_studies c WHERE c.category_id=b.category_id) AS ngn_cases,
             (SELECT COUNT(*) FROM ngn_case_items i JOIN ngn_case_studies c ON c.id=i.case_study_id WHERE c.category_id=b.category_id) AS ngn_items
      FROM test_blueprint_2026 b LEFT JOIN core_questions q ON q.category_id=b.category_id
      GROUP BY b.category_id ORDER BY b.blueprint_rank
    """).fetchall()
    distribution = [
        {"category_id":r[0],"category":r[1],"official_range_pct":[r[2],r[3]],"midpoint_pct":r[4],"core_count":r[5],"core_pct":r[6],"ngn_cases":r[7],"ngn_items":r[8]}
        for r in category_rows
    ]
    issue_counts = {r[0]: r[1] for r in db.execute("SELECT issue_code,COUNT(*) FROM audit_issues GROUP BY issue_code ORDER BY COUNT(*) DESC")}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Structural integrity, schema normalization, exact-stem deduplication, case cohesion, source-traceability flags, scoring-map flags, and commercial app ordering. Clinical correctness and commercial IP rights are not independently certified.",
        "source_integrity": {CORE_PATH.name: integrity(CORE_PATH), NGN_PATH.name: integrity(NGN_PATH)},
        "core_bank": core,
        "ngn_bank": ngn,
        "distribution": distribution,
        "issue_counts": issue_counts,
        "master_db": {
            "core_rows": db.execute("SELECT COUNT(*) FROM core_questions").fetchone()[0],
            "active_unique_core": db.execute("SELECT COUNT(*) FROM v_active_core_questions").fetchone()[0],
            "ngn_cases": db.execute("SELECT COUNT(*) FROM ngn_case_studies").fetchone()[0],
            "ngn_practice_items": db.execute("SELECT COUNT(*) FROM v_ngn_practice_items").fetchone()[0],
            "ngn_simulation_items": db.execute("SELECT COUNT(*) FROM v_ngn_simulation_items").fetchone()[0],
            "catalog_rows": db.execute("SELECT COUNT(*) FROM unified_catalog").fetchone()[0],
            "sqlite_integrity": db.execute("PRAGMA integrity_check").fetchone()[0],
        },
        "release_status": "STRUCTURALLY_MERGED__CLINICAL_AND_IP_REVIEW_REQUIRED"
    }


def write_markdown(report: dict) -> None:
    core = report["core_bank"]
    ngn = report["ngn_bank"]
    master = report["master_db"]
    lines = [
        "# NCLEX Commercial Bank Audit — Corrected Merge",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Result",
        "",
        f"- Core MCQ source rows: **{core['rows']:,}**",
        f"- Active unique core MCQ after exact-stem dedupe: **{core['active_unique']:,}**",
        f"- NGN case studies: **{ngn['case_count']:,}**",
        f"- NGN practice items: **{ngn['practice_item_count']:,}** (7 formats per case)",
        f"- NGN simulation items: **{ngn['simulation_item_count']:,}** (6 per case)",
        f"- Stand-alone NGN items currently present: **{ngn['standalone_ngn_count']:,}**",
        f"- Unified catalog rows: **{master['catalog_rows']:,}**",
        f"- Final SQLite integrity: **{master['sqlite_integrity']}**",
        "",
        "## Core blueprint distribution",
        "",
        "| Category | Core | Core % | Range | Midpoint | NGN cases | NGN items |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for d in report["distribution"]:
        lo, hi = d["official_range_pct"]
        lines.append(f"| {d['category']} | {d['core_count']} | {d['core_pct']:.2f}% | {lo:.0f}-{hi:.0f}% | {d['midpoint_pct']:.0f}% | {d['ngn_cases']} | {d['ngn_items']} |")
    lines += [
        "",
        "## Exact deduplication",
        "",
        f"- Exact core stem groups: **{len(core['exact_duplicate_groups'])}**",
        f"- Groups: `{core['exact_duplicate_groups']}`",
        "- Duplicate source rows remain in `core_questions`; duplicates are `active=0` and point to `duplicate_of_uid`.",
        "- NGN stems are **not** deduplicated across case studies because a generic stem can have different meaning under different case context.",
        "",
        "## Ordering semantics",
        "",
        "1. `unified_catalog.catalog_order` is a stable admin/import order: pool → Client Needs rank → case/sequence or source ID.",
        "2. It is **not** the exam delivery order.",
        "3. Core tests should be sampled using the blueprint weights/ranges stored in `test_blueprint_2026`.",
        "4. NGN simulation keeps each selected case together and uses six items per case. All seven source formats remain available in practice mode.",
        "",
        "## Important commercial gates",
        "",
        f"- Homepage-only core source URLs flagged for traceability review: **{core['homepage_only_sources']:,}**.",
        "- All source rows carry an internal `verified` flag, but the merged DB deliberately labels independent clinical status as `NOT_VERIFIED` until answer/rationale review is performed independently.",
        "- NGN `extended_drag_drop` and `bowtie` source scoring rules are flagged for scoring-model review before claiming exact NCLEX scoring behavior.",
        f"- Stand-alone NGN pool has **{ngn['standalone_ngn_count']}** items, so the current bank should not yet be marketed as a complete replication of every current clinical-judgment delivery component.",
        "- IP/licensing review remains required before commercial publication; source attribution is not the same as permission to reproduce copyrighted material.",
        "",
        "## Release status",
        "",
        f"**{report['release_status']}**",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if integrity(CORE_PATH) != "ok" or integrity(NGN_PATH) != "ok":
        raise SystemExit("Source SQLite integrity check failed")
    if OUT_DB.exists():
        OUT_DB.unlink()
    db = sqlite3.connect(OUT_DB)
    try:
        create_schema(db)
        copy_blueprint(db)
        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "generated_at": now,
            "source_core": CORE_PATH.name,
            "source_ngn": NGN_PATH.name,
            "purpose": "Commercial NCLEX preparation app catalog",
            "clinical_status": "NOT_INDEPENDENTLY_VERIFIED",
            "ip_status": "REVIEW_REQUIRED",
            "ordering_version": "commercial-v1",
        }
        db.executemany("INSERT INTO metadata(key,value) VALUES(?,?)", list(meta.items()))
        core = load_core(db)
        ngn = load_ngn(db)
        build_catalog(db)
        add_rules(db)
        db.commit()
        report = audit_report(db, core, ngn)
        if report["master_db"]["sqlite_integrity"] != "ok":
            raise SystemExit("Merged SQLite integrity check failed")
        OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        write_markdown(report)
        print(json.dumps(report["master_db"], indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
