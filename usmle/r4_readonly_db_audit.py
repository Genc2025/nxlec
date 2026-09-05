#!/usr/bin/env python3
"""Read-only production DB audit for Q1221-Q1225 R4.

This script never writes to SQLite. It reports the production count/statuses,
PRAGMA integrity_check, the DB SHA-256, exact construct-term hits, and TF-IDF
lexical nearest neighbours for the five R3 item texts (R4 changes evidence
metadata only). Similarity output is review evidence, not an automatic
originality or production-acceptance verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
STOP = {
    "a","an","and","are","as","at","be","been","by","can","cell","cells",
    "does","during","for","from","has","have","her","his","in","is","it",
    "most","normal","not","of","on","or","patient","patients","the","their",
    "this","to","which","with","woman","women","boy","girl","man","men",
    "year","years","old","shows","show","following","best","explains",
    "directly","identifies","evaluation","testing","test","results","result"
}

TERMS = {
    "Q1221": ["ghrhr", "growth hormone-releasing hormone", "somatotroph"],
    "Q1222": ["abcc8", "atp-sensitive potassium", "congenital hyperinsulinism"],
    "Q1223": ["gck", "glucokinase", "maturity-onset diabetes of the young"],
    "Q1224": ["lepr", "leptin receptor", "leptin-receptor"],
    "Q1225": ["lhcgr", "leydig cell hypoplasia", "human chorionic gonadotropin"]
}


def recursive_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from recursive_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from recursive_strings(value)


def item_text(item):
    return " ".join(recursive_strings(item))


def tokens(text):
    return [t for t in TOKEN_RE.findall(text.casefold()) if len(t) > 2 and t not in STOP]


def cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[k] * b[k] for k in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def tfidf_vector(tok, idf):
    counts = Counter(tok)
    return {k: (1.0 + math.log(v)) * idf.get(k, 1.0) for k, v in counts.items()}


def compact_item(item):
    return {
        "vignette": item.get("vignette"),
        "lead_in": item.get("lead_in"),
        "options": item.get("options"),
        "intended_key": item.get("intended_key"),
        "tested_construct": item.get("tested_construct"),
    }


def main():
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    ap.add_argument("--db", type=Path, default=here / "data" / "usmle-step1.db")
    ap.add_argument("--candidates", type=Path,
                    default=here / "reviewed" / "q1221_q1225_direct_chatgpt_r3.json")
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()

    db = args.db.resolve(strict=True)
    candidate_path = args.candidates.resolve(strict=True)
    db_sha = hashlib.sha256(db.read_bytes()).hexdigest()

    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as con:
        con.execute("PRAGMA query_only=ON")
        integrity = [r[0] for r in con.execute("PRAGMA integrity_check").fetchall()]
        status_counts = dict(con.execute(
            "SELECT final_status, COUNT(*) FROM step2_final_items GROUP BY final_status"
        ).fetchall())
        rows = con.execute(
            "SELECT candidate_id, payload_json, payload_sha256, final_status "
            "FROM step2_final_items ORDER BY candidate_id"
        ).fetchall()

    prod = []
    hash_mismatches = []
    for cid, payload, stored_hash, status in rows:
        computed = hashlib.sha256(payload.encode()).hexdigest()
        if computed != stored_hash:
            hash_mismatches.append({"candidate_id": cid, "stored": stored_hash, "computed": computed})
        parsed = json.loads(payload)
        item = parsed.get("item", parsed)
        text = item_text(item)
        prod.append({"candidate_id": cid, "status": status, "item": item, "text": text})

    candidate_doc = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidates = {}
    for wrapper in candidate_doc["items"]:
        q = f"Q{int(wrapper['num']):04d}"
        candidates[q] = wrapper["item"]

    # Exact/specific construct-term retrieval against production item fields.
    term_hits = {}
    for q, term_list in TERMS.items():
        qhits = {}
        for term in term_list:
            needle = term.casefold()
            hits = []
            for row in prod:
                if needle in row["text"].casefold():
                    hits.append({
                        "candidate_id": row["candidate_id"],
                        "status": row["status"],
                        "item": compact_item(row["item"]),
                    })
            qhits[term] = hits
        term_hits[q] = qhits

    # TF-IDF nearest-neighbour retrieval for adversarial duplicate review.
    prod_tokens = [tokens(row["text"]) for row in prod]
    n = len(prod_tokens)
    df = Counter()
    for tok in prod_tokens:
        df.update(set(tok))
    idf = {t: math.log((n + 1) / (freq + 1)) + 1.0 for t, freq in df.items()}
    prod_vectors = [tfidf_vector(tok, idf) for tok in prod_tokens]

    nearest = {}
    for q, item in candidates.items():
        ctok = tokens(item_text(item))
        cvec = tfidf_vector(ctok, idf)
        scored = []
        cset = set(ctok)
        for row, ptok, pvec in zip(prod, prod_tokens, prod_vectors):
            score = cosine(cvec, pvec)
            pset = set(ptok)
            overlap = sorted(cset & pset, key=lambda t: idf.get(t, 0), reverse=True)[:15]
            scored.append((score, row, overlap))
        scored.sort(key=lambda x: x[0], reverse=True)
        nearest[q] = [
            {
                "candidate_id": row["candidate_id"],
                "status": row["status"],
                "tfidf_cosine": round(score, 6),
                "highest_idf_overlap": overlap,
                "item": compact_item(row["item"]),
            }
            for score, row, overlap in scored[: args.top]
        ]

    report = {
        "audit": "Q1221-Q1225 R4 read-only DB audit",
        "database": str(db),
        "database_sha256": db_sha,
        "sqlite_integrity_check": integrity,
        "row_count": len(rows),
        "status_counts": status_counts,
        "payload_hash_mismatches": hash_mismatches,
        "candidate_source": str(candidate_path),
        "term_hits": term_hits,
        "nearest_neighbours": nearest,
        "limitations": [
            "Term retrieval and TF-IDF similarity do not prove semantic originality.",
            "Human/adversarial review of retrieved neighbours remains required.",
            "This script does not write to the database or authorize production import."
        ]
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
