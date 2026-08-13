#!/usr/bin/env python3
"""Audit and merge the repository's NCLEX SQLite banks without altering source data."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("ngn75", ROOT / "nclex ngn bank 75of75 ALL7formats FINAL.db", 0),
    ("v2", ROOT / "nclex question bank v2 inprogress 5.db", 1),
]
OUT_DB = ROOT / "nclex_commercial_merged.db"
OUT_JSON = ROOT / "NCLEX_AUDIT_REPORT.json"
OUT_MD = ROOT / "NCLEX_AUDIT_REPORT.md"

QUESTION_COLS = ["question_text", "question", "stem", "prompt", "item_text", "stem_text", "question_stem", "text"]
ANSWER_COLS = ["correct_answer", "correct_answers", "correct_option", "correct_response", "answer_key", "answer", "correct", "key"]
RATIONALE_COLS = ["rationale", "explanation", "rationales", "answer_rationale", "reasoning"]
TYPE_COLS = ["item_type", "question_type", "format", "item_format", "type"]
CATEGORY_COLS = ["client_needs", "client_need", "nclex_category", "category", "subcategory", "content_area", "domain", "topic", "specialty", "system"]
DIFFICULTY_COLS = ["difficulty", "level", "difficulty_level"]
CASE_COLS = ["case_id", "case_study_id", "scenario_id", "patient_case_id", "case_number", "set_id", "group_id"]
ORDER_COLS = ["item_number", "question_number", "sequence", "seq", "position", "order_index", "sort_order"]
PK_COLS = ["qid", "question_id", "item_id", "id", "uid", "uuid"]
REFERENCE_COLS = ["source", "sources", "reference", "references", "citation", "citations", "source_title", "source_url", "reference_text"]
OPTIONS_CONTAINER_COLS = ["options", "choices", "answer_options", "responses", "selections"]
OPTION_RE = re.compile(r"^(?:option|choice|answer)_?([a-h1-8])$", re.I)

BLUEPRINT = [
    (1, "Management of Care", 18.0, ["management of care", "management", "delegation", "prioritization", "coordination of care"]),
    (2, "Safety and Infection Prevention and Control", 13.0, ["safety and infection prevention and control", "safety and infection", "infection control", "safety"]),
    (3, "Health Promotion and Maintenance", 9.0, ["health promotion and maintenance", "health promotion", "growth and development", "antepartum", "postpartum", "newborn"]),
    (4, "Psychosocial Integrity", 9.0, ["psychosocial integrity", "psychosocial", "mental health", "psychiatric"]),
    (5, "Basic Care and Comfort", 9.0, ["basic care and comfort", "basic care", "comfort"]),
    (6, "Pharmacological and Parenteral Therapies", 16.0, ["pharmacological and parenteral therapies", "pharmacology", "medication", "parenteral"]),
    (7, "Reduction of Risk Potential", 12.0, ["reduction of risk potential", "reduction of risk", "risk potential", "diagnostic tests"]),
    (8, "Physiological Adaptation", 14.0, ["physiological adaptation", "physiologic adaptation", "acute care", "medical surgical", "med surg"]),
]


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_") or "table"


def lower_map(cols: list[str]) -> dict[str, str]:
    return {c.lower(): c for c in cols}


def pick(cols: list[str], candidates: list[str]) -> str | None:
    m = lower_map(cols)
    for c in candidates:
        if c in m:
            return m[c]
    return None


def value(row: dict[str, Any], col: str | None) -> Any:
    return row.get(col) if col else None


def as_text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bytes):
        return base64.b64encode(v).decode("ascii")
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return str(v).strip()


def json_safe(v: Any) -> Any:
    if isinstance(v, bytes):
        return {"__blob_base64__": base64.b64encode(v).decode("ascii")}
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)


def compact_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def norm_text(s: str) -> str:
    s = compact_ws(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def parse_jsonish(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (list, dict, int, float, bool)):
        return v
    s = as_text(v)
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def extract_options(row: dict[str, Any], cols: list[str]) -> Any:
    ordered = []
    for c in cols:
        m = OPTION_RE.match(c.lower())
        if m and as_text(row.get(c)):
            key = m.group(1).upper()
            ordered.append((key, row.get(c)))
    if ordered:
        ordered.sort(key=lambda x: (len(x[0]), x[0]))
        return {k: json_safe(v) for k, v in ordered}
    container = pick(cols, OPTIONS_CONTAINER_COLS)
    if container:
        return parse_jsonish(row.get(container))
    return None


def infer_item_family(raw_type: str, options: Any, answer: Any, row: dict[str, Any]) -> str:
    t = norm_text(raw_type)
    whole = " ".join([t, norm_text(as_text(row))])
    if "bow tie" in t or "bowtie" in t:
        return "bow_tie"
    if "matrix" in t or "grid" in t:
        return "matrix"
    if "cloze" in t or "drop down" in t or "dropdown" in t:
        return "cloze"
    if "highlight" in t:
        return "highlight"
    if "ordered" in t or "order response" in t or "sequence" in t or "drag and drop" in t:
        return "ordered_response"
    if "select all" in t or "sata" in t or "multiple response" in t or "select n" in t or "grouping" in t:
        return "multiple_response"
    if "multiple choice" in t or "single response" in t or "mcq" in t:
        return "multiple_choice"
    if isinstance(options, dict) and len(options) >= 2:
        if isinstance(answer, list):
            return "multiple_response"
        a = as_text(answer)
        if "," in a or ";" in a:
            return "multiple_response"
        return "multiple_choice"
    if "hotspot" in whole:
        return "hotspot"
    return "other"


def classify_blueprint(*texts: str) -> tuple[str, float, int]:
    s = norm_text(" ".join(t for t in texts if t))
    if not s:
        return "Unmapped", 0.0, 99
    best = None
    for rank, name, pct, aliases in BLUEPRINT:
        for alias in aliases:
            a = norm_text(alias)
            if a and a in s:
                score = len(a)
                if best is None or score > best[0]:
                    best = (score, name, pct, rank)
    if best:
        _, name, pct, rank = best
        return name, pct, rank
    return "Unmapped", 0.0, 99


def table_info(conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    rows = conn.execute(f"PRAGMA table_info({qident(table)})").fetchall()
    return [{"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "default": r[4], "pk": r[5]} for r in rows]


def is_question_table(table: str, cols: list[str]) -> bool:
    qcol = pick(cols, QUESTION_COLS)
    if not qcol:
        return False
    has_answer = bool(pick(cols, ANSWER_COLS))
    has_options = any(OPTION_RE.match(c.lower()) for c in cols) or bool(pick(cols, OPTIONS_CONTAINER_COLS))
    has_type = bool(pick(cols, TYPE_COLS))
    named = bool(re.search(r"question|item|bank", table, re.I))
    return has_answer or has_options or has_type or named


def integrity(conn: sqlite3.Connection) -> str:
    try:
        return str(conn.execute("PRAGMA integrity_check").fetchone()[0])
    except Exception as e:
        return f"ERROR: {e}"


def row_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {qident(table)}").fetchone()[0])


def source_audit(label: str, path: Path) -> dict[str, Any]:
    conn = sqlite3.connect(path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    result = {
        "label": label,
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "integrity_check": integrity(conn),
        "tables": [],
    }
    for table in tables:
        info = table_info(conn, table)
        cols = [x["name"] for x in info]
        result["tables"].append({
            "name": table,
            "row_count": row_count(conn, table),
            "columns": info,
            "question_like": is_question_table(table, cols),
        })
    conn.close()
    return result


def init_output(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    PRAGMA foreign_keys=ON;
    CREATE TABLE merge_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE source_schemas(source_bank TEXT, source_table TEXT, create_sql TEXT, PRIMARY KEY(source_bank, source_table));
    CREATE TABLE blueprint_2026(rank INTEGER PRIMARY KEY, client_needs TEXT UNIQUE, target_pct REAL NOT NULL);
    CREATE TABLE question_catalog(
      catalog_id INTEGER PRIMARY KEY AUTOINCREMENT,
      question_uid TEXT UNIQUE NOT NULL,
      source_bank TEXT NOT NULL,
      source_file TEXT NOT NULL,
      source_table TEXT NOT NULL,
      source_pk TEXT,
      source_rowid INTEGER,
      source_order INTEGER,
      case_group TEXT,
      case_sequence INTEGER,
      item_format_raw TEXT,
      item_family TEXT,
      client_needs_2026 TEXT,
      blueprint_target_pct REAL,
      content_area_raw TEXT,
      difficulty_raw TEXT,
      question_text TEXT,
      options_json TEXT,
      correct_answer_json TEXT,
      rationale TEXT,
      reference_text TEXT,
      stem_hash TEXT,
      content_hash TEXT,
      duplicate_of_uid TEXT,
      near_duplicate_group TEXT,
      structural_status TEXT NOT NULL,
      clinical_verification_status TEXT NOT NULL DEFAULT 'NOT_VERIFIED',
      app_ready INTEGER NOT NULL DEFAULT 0,
      commercial_order INTEGER,
      raw_json TEXT NOT NULL
    );
    CREATE TABLE question_issues(
      issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
      question_uid TEXT NOT NULL,
      severity TEXT NOT NULL,
      issue_code TEXT NOT NULL,
      detail TEXT,
      FOREIGN KEY(question_uid) REFERENCES question_catalog(question_uid)
    );
    CREATE INDEX idx_catalog_blueprint ON question_catalog(client_needs_2026, commercial_order);
    CREATE INDEX idx_catalog_case ON question_catalog(case_group, case_sequence);
    CREATE INDEX idx_catalog_stem_hash ON question_catalog(stem_hash);
    CREATE INDEX idx_catalog_app_ready ON question_catalog(app_ready, structural_status);
    """)
    conn.executemany("INSERT INTO blueprint_2026(rank,client_needs,target_pct) VALUES(?,?,?)", [(r,n,p) for r,n,p,_ in BLUEPRINT])


def copy_raw_tables(out: sqlite3.Connection, label: str, path: Path) -> None:
    src = sqlite3.connect(path)
    tables = [r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for table in tables:
        sqlrow = src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        out.execute("INSERT OR REPLACE INTO source_schemas(source_bank,source_table,create_sql) VALUES(?,?,?)", (label, table, sqlrow[0] if sqlrow else ""))
        info = table_info(src, table)
        cols = [x["name"] for x in info]
        raw_name = f"raw_{label}__{safe_name(table)}"
        col_defs = ",".join(f"{qident(c)}" for c in cols)
        out.execute(f"CREATE TABLE {qident(raw_name)} ({','.join(qident(c) for c in cols)})")
        cur = src.execute(f"SELECT {col_defs} FROM {qident(table)}")
        ph = ",".join("?" for _ in cols)
        out.executemany(f"INSERT INTO {qident(raw_name)} VALUES({ph})", cur)
    src.close()


def extract_catalog(out: sqlite3.Connection, label: str, path: Path, source_priority: int, report: dict[str, Any]) -> None:
    src = sqlite3.connect(path)
    src.row_factory = sqlite3.Row
    table_reports = {t["name"]: t for t in report["tables"]}
    for table, tr in table_reports.items():
        if not tr["question_like"]:
            continue
        cols = [c["name"] for c in tr["columns"]]
        qcol = pick(cols, QUESTION_COLS)
        acol = pick(cols, ANSWER_COLS)
        rcol = pick(cols, RATIONALE_COLS)
        tcol = pick(cols, TYPE_COLS)
        ccols = [c for c in CATEGORY_COLS if c in lower_map(cols)]
        ccols = [lower_map(cols)[c] for c in ccols]
        dcol = pick(cols, DIFFICULTY_COLS)
        casecol = pick(cols, CASE_COLS)
        ordercol = pick(cols, ORDER_COLS)
        pkcol = pick(cols, PK_COLS)
        refcols = [lower_map(cols)[c] for c in REFERENCE_COLS if c in lower_map(cols)]
        cur = src.execute(f"SELECT rowid AS __rowid__, * FROM {qident(table)}")
        source_seq = 0
        for rr in cur:
            source_seq += 1
            row = {k: rr[k] for k in rr.keys() if k != "__rowid__"}
            rowid = int(rr["__rowid__"])
            qtext = compact_ws(as_text(value(row, qcol)))
            if not qtext:
                continue
            ans_obj = parse_jsonish(value(row, acol))
            options_obj = extract_options(row, cols)
            rationale = compact_ws(as_text(value(row, rcol)))
            raw_type = compact_ws(as_text(value(row, tcol)))
            family = infer_item_family(raw_type, options_obj, ans_obj, row)
            content_parts = [compact_ws(as_text(row.get(c))) for c in ccols if as_text(row.get(c))]
            content_raw = " | ".join(dict.fromkeys(content_parts))
            client_needs, target_pct, blueprint_rank = classify_blueprint(content_raw, raw_type)
            difficulty = compact_ws(as_text(value(row, dcol)))
            ref_text = " | ".join(dict.fromkeys(compact_ws(as_text(row.get(c))) for c in refcols if as_text(row.get(c))))
            source_pk = compact_ws(as_text(value(row, pkcol))) or str(rowid)
            case_val = compact_ws(as_text(value(row, casecol)))
            case_group = f"{label}:{table}:{case_val}" if case_val else None
            try:
                case_sequence = int(value(row, ordercol)) if ordercol and value(row, ordercol) is not None else source_seq
            except Exception:
                case_sequence = source_seq
            try:
                source_order = int(value(row, ordercol)) if ordercol and value(row, ordercol) is not None else source_seq
            except Exception:
                source_order = source_seq
            opts_norm = norm_text(json.dumps(options_obj, ensure_ascii=False, sort_keys=True) if options_obj is not None else "")
            stem_hash = sha(norm_text(qtext))
            content_hash = sha(norm_text(qtext) + "|" + opts_norm)
            uid = f"{label}:{safe_name(table)}:{source_pk}"
            issues = []
            if len(qtext) < 20:
                issues.append(("WARN", "SHORT_STEM", f"Question text has {len(qtext)} characters"))
            if ans_obj in (None, "", [], {}):
                issues.append(("ERROR", "MISSING_ANSWER", "No recognizable correct-answer field/value"))
            if family in {"multiple_choice", "multiple_response"} and options_obj in (None, "", [], {}):
                issues.append(("ERROR", "MISSING_OPTIONS", f"{family} item has no recognizable options"))
            if not rationale:
                issues.append(("WARN", "MISSING_RATIONALE", "No recognizable rationale/explanation"))
            if not ref_text:
                issues.append(("INFO", "MISSING_REFERENCE", "No recognizable source/reference metadata"))
            if family == "other":
                issues.append(("INFO", "UNMAPPED_ITEM_FORMAT", raw_type or "No explicit item format"))
            if client_needs == "Unmapped":
                issues.append(("INFO", "UNMAPPED_BLUEPRINT", content_raw or "No recognizable Client Needs metadata"))
            structural_status = "PASS" if not any(sev == "ERROR" for sev, _, _ in issues) else "REVIEW"
            app_ready = 1 if structural_status == "PASS" else 0
            raw_json = json.dumps({k: json_safe(v) for k, v in row.items()}, ensure_ascii=False, sort_keys=True)
            out.execute("""
                INSERT INTO question_catalog(
                  question_uid,source_bank,source_file,source_table,source_pk,source_rowid,source_order,
                  case_group,case_sequence,item_format_raw,item_family,client_needs_2026,blueprint_target_pct,
                  content_area_raw,difficulty_raw,question_text,options_json,correct_answer_json,rationale,
                  reference_text,stem_hash,content_hash,structural_status,app_ready,raw_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                uid,label,path.name,table,source_pk,rowid,source_order,case_group,case_sequence,raw_type,family,
                client_needs,target_pct,content_raw,difficulty,qtext,
                json.dumps(options_obj,ensure_ascii=False,sort_keys=True) if options_obj is not None else None,
                json.dumps(ans_obj,ensure_ascii=False,sort_keys=True) if ans_obj is not None else None,
                rationale,ref_text,stem_hash,content_hash,structural_status,app_ready,raw_json
            ))
            out.executemany("INSERT INTO question_issues(question_uid,severity,issue_code,detail) VALUES(?,?,?,?)", [(uid,*x) for x in issues])
    src.close()


def mark_duplicates(out: sqlite3.Connection) -> dict[str, Any]:
    rows = out.execute("SELECT question_uid,source_bank,source_table,source_order,stem_hash,question_text,structural_status FROM question_catalog ORDER BY catalog_id").fetchall()
    groups = defaultdict(list)
    for r in rows:
        groups[r[4]].append(r)
    exact_groups = []
    for stem_hash, items in groups.items():
        if len(items) < 2:
            continue
        # Prefer structurally valid items; on ties prefer the finalized NGN bank, then original order.
        items_sorted = sorted(items, key=lambda r: (0 if r[6] == "PASS" else 1, 0 if r[1] == "ngn75" else 1, r[3] or 10**9, r[0]))
        canonical = items_sorted[0][0]
        exact_groups.append({"canonical": canonical, "members": [x[0] for x in items_sorted], "stem": items_sorted[0][5][:240]})
        for x in items_sorted[1:]:
            out.execute("UPDATE question_catalog SET duplicate_of_uid=?, app_ready=0 WHERE question_uid=?", (canonical, x[0]))
            out.execute("INSERT INTO question_issues(question_uid,severity,issue_code,detail) VALUES(?,?,?,?)", (x[0], "WARN", "EXACT_DUPLICATE_STEM", f"Duplicate of {canonical}"))

    # Conservative near-duplicate candidate detection: only compare items in small lexical/length blocks.
    candidates = []
    active = [(r[0], r[5], norm_text(r[5])) for r in rows]
    blocks = defaultdict(list)
    for uid, text, n in active:
        toks = n.split()
        key = (" ".join(toks[:3]), len(n)//80)
        if toks:
            blocks[key].append((uid,text,n))
    seen = set()
    near_group_no = 0
    for block in blocks.values():
        if len(block) < 2 or len(block) > 80:
            continue
        for i in range(len(block)):
            for j in range(i+1, len(block)):
                a, b = block[i], block[j]
                pair = tuple(sorted((a[0],b[0])))
                if pair in seen:
                    continue
                seen.add(pair)
                if a[2] == b[2]:
                    continue
                ratio = SequenceMatcher(None, a[2], b[2]).ratio()
                if ratio >= 0.94:
                    near_group_no += 1
                    gid = f"ND{near_group_no:04d}"
                    out.execute("UPDATE question_catalog SET near_duplicate_group=COALESCE(near_duplicate_group,?) WHERE question_uid IN (?,?)", (gid,a[0],b[0]))
                    out.execute("INSERT INTO question_issues(question_uid,severity,issue_code,detail) VALUES(?,?,?,?)", (a[0],"INFO","NEAR_DUPLICATE_CANDIDATE",f"{b[0]} similarity={ratio:.3f}"))
                    out.execute("INSERT INTO question_issues(question_uid,severity,issue_code,detail) VALUES(?,?,?,?)", (b[0],"INFO","NEAR_DUPLICATE_CANDIDATE",f"{a[0]} similarity={ratio:.3f}"))
                    candidates.append({"a":a[0],"b":b[0],"similarity":round(ratio,4)})
    return {"exact_duplicate_groups": exact_groups, "near_duplicate_candidates": candidates}


def apply_commercial_order(out: sqlite3.Connection) -> None:
    # Stable storage order: official 2026 Client Needs rank -> case cohesion -> source -> source order.
    rank_map = {name: rank for rank, name, _, _ in BLUEPRINT}
    rows = out.execute("SELECT question_uid,client_needs_2026,case_group,case_sequence,source_bank,source_table,source_order,catalog_id FROM question_catalog").fetchall()
    def key(r: tuple[Any,...]):
        uid, cat, case_group, case_seq, bank, table, source_order, catalog_id = r
        rank = rank_map.get(cat, 99)
        case_key = case_group or f"~single:{bank}:{table}:{source_order or catalog_id:09d}"
        bank_rank = 0 if bank == "v2" else 1
        return (rank, case_key, case_seq or 0, bank_rank, source_order or catalog_id, uid)
    ordered = sorted(rows, key=key)
    out.executemany("UPDATE question_catalog SET commercial_order=? WHERE question_uid=?", [(i+1,r[0]) for i,r in enumerate(ordered)])


def summarize(out: sqlite3.Connection, source_reports: list[dict[str, Any]], dup: dict[str, Any]) -> dict[str, Any]:
    total = out.execute("SELECT COUNT(*) FROM question_catalog").fetchone()[0]
    ready = out.execute("SELECT COUNT(*) FROM question_catalog WHERE app_ready=1").fetchone()[0]
    hold = total - ready
    by_bank = dict(out.execute("SELECT source_bank,COUNT(*) FROM question_catalog GROUP BY source_bank"))
    by_family = dict(out.execute("SELECT item_family,COUNT(*) FROM question_catalog GROUP BY item_family ORDER BY COUNT(*) DESC"))
    by_blueprint = {r[0]: {"count": r[1], "target_pct": r[2]} for r in out.execute("SELECT client_needs_2026,COUNT(*),MAX(blueprint_target_pct) FROM question_catalog WHERE app_ready=1 GROUP BY client_needs_2026 ORDER BY COUNT(*) DESC")}
    issues = {r[0]: r[1] for r in out.execute("SELECT issue_code,COUNT(*) FROM question_issues GROUP BY issue_code ORDER BY COUNT(*) DESC")}
    cases = out.execute("SELECT COUNT(DISTINCT case_group) FROM question_catalog WHERE case_group IS NOT NULL").fetchone()[0]
    case_items = out.execute("SELECT COUNT(*) FROM question_catalog WHERE case_group IS NOT NULL").fetchone()[0]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_scope": "structural/schema/deduplication/ordering only; clinical correctness remains unverified",
        "source_databases": source_reports,
        "catalog": {
            "total_recognized_question_rows": total,
            "app_ready_structurally": ready,
            "held_for_structural_review_or_duplicate": hold,
            "by_source_bank": by_bank,
            "by_item_family": by_family,
            "by_2026_client_needs": by_blueprint,
            "case_groups_detected": cases,
            "items_in_case_groups": case_items,
        },
        "issues": issues,
        "duplicates": dup,
        "ordering_policy": {
            "storage_order": "2026 Client Needs rank, then keep inferred case-study groups contiguous, then source order",
            "test_delivery": "Do not serve by storage order. Build tests using blueprint-weighted sampling and keep case-study item sets intact.",
            "dedupe_priority": "structural PASS first; then ngn75 FINAL over v2 inprogress for exact duplicate stems",
        },
        "clinical_verification_status": "NOT_VERIFIED",
    }


def write_markdown(report: dict[str, Any]) -> None:
    c = report["catalog"]
    lines = [
        "# NCLEX Commercial Bank Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "> Scope: structural/schema/deduplication/ordering audit. This does **not** certify clinical correctness or source licensing.",
        "",
        "## Executive summary",
        "",
        f"- Recognized question rows: **{c['total_recognized_question_rows']}**",
        f"- Structurally app-ready after exact dedupe: **{c['app_ready_structurally']}**",
        f"- Held for review/duplicate: **{c['held_for_structural_review_or_duplicate']}**",
        f"- Detected case-study groups: **{c['case_groups_detected']}** ({c['items_in_case_groups']} items)",
        f"- Exact duplicate stem groups: **{len(report['duplicates']['exact_duplicate_groups'])}**",
        f"- Near-duplicate candidates: **{len(report['duplicates']['near_duplicate_candidates'])}**",
        "",
        "## Source databases",
        "",
    ]
    for s in report["source_databases"]:
        lines += [f"### {s['label']} — `{s['file']}`", f"- Size: {s['size_bytes']:,} bytes", f"- SQLite integrity: `{s['integrity_check']}`", "- Tables:"]
        for t in s["tables"]:
            marker = "question-like" if t["question_like"] else "support/raw"
            lines.append(f"  - `{t['name']}` — {t['row_count']:,} rows — {marker}")
        lines.append("")
    lines += ["## Item families", ""]
    for k,v in c["by_item_family"].items():
        lines.append(f"- {k}: **{v}**")
    lines += ["", "## 2026 Client Needs mapping (structurally app-ready unique items)", ""]
    for k,v in c["by_2026_client_needs"].items():
        lines.append(f"- {k}: **{v['count']}** items; official midpoint target stored: **{v['target_pct']}%**")
    lines += ["", "## Audit issue counts", ""]
    for k,v in report["issues"].items():
        lines.append(f"- {k}: **{v}**")
    lines += [
        "",
        "## Ordering and app usage",
        "",
        "`question_catalog.commercial_order` is a stable catalog order, not an exam sequence. It groups by the 2026 Client Needs framework and keeps inferred NGN case-study item sets together. Commercial tests should sample from the catalog by blueprint weights, rather than simply taking consecutive rows.",
        "",
        "## Safety gate",
        "",
        "Every normalized item is marked `clinical_verification_status = NOT_VERIFIED`. A structural PASS means the record can be rendered by an app; it does not mean the medical answer/rationale has been independently verified.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    missing = [str(p) for _, p, _ in SOURCES if not p.exists()]
    if missing:
        print("Missing source databases:", *missing, sep="\n- ", file=sys.stderr)
        return 2
    source_reports = [source_audit(label, path) for label, path, _ in SOURCES]
    if OUT_DB.exists():
        OUT_DB.unlink()
    out = sqlite3.connect(OUT_DB)
    init_output(out)
    out.execute("INSERT INTO merge_metadata(key,value) VALUES(?,?)", ("generated_at", datetime.now(timezone.utc).isoformat()))
    out.execute("INSERT INTO merge_metadata(key,value) VALUES(?,?)", ("clinical_verification_status", "NOT_VERIFIED"))
    out.execute("INSERT INTO merge_metadata(key,value) VALUES(?,?)", ("blueprint", "2026 NCLEX-RN Test Plan; midpoint distribution 18/13/9/9/9/16/12/14"))
    for label, path, priority in SOURCES:
        copy_raw_tables(out, label, path)
        report = next(r for r in source_reports if r["label"] == label)
        extract_catalog(out, label, path, priority, report)
    dup = mark_duplicates(out)
    apply_commercial_order(out)
    out.commit()
    report = summarize(out, source_reports, dup)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)
    out.execute("INSERT OR REPLACE INTO merge_metadata(key,value) VALUES(?,?)", ("audit_report_json", OUT_JSON.name))
    out.execute("INSERT OR REPLACE INTO merge_metadata(key,value) VALUES(?,?)", ("audit_report_md", OUT_MD.name))
    out.commit()
    check = out.execute("PRAGMA integrity_check").fetchone()[0]
    out.close()
    if check != "ok":
        print(f"Merged DB integrity failed: {check}", file=sys.stderr)
        return 3
    print(json.dumps({
        "merged_db": OUT_DB.name,
        "audit_json": OUT_JSON.name,
        "audit_md": OUT_MD.name,
        "recognized_questions": report["catalog"]["total_recognized_question_rows"],
        "app_ready": report["catalog"]["app_ready_structurally"],
        "held": report["catalog"]["held_for_structural_review_or_duplicate"],
        "exact_duplicate_groups": len(report["duplicates"]["exact_duplicate_groups"]),
        "near_duplicate_candidates": len(report["duplicates"]["near_duplicate_candidates"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
