#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

DB = Path('NCLEX_FULL_3525_RULE1_1125.db')
OUT = Path('RULE1_FULL_3525_DUPLICATE_SCAN.json')
EXPECTED_COUNT = 3525

STOP = {
    'the','a','an','and','or','of','to','in','on','for','with','by','at','from','as','is','are','was','were','be','been','being',
    'that','this','these','those','which','what','when','where','who','whom','whose','why','how','most','best','first','next','should',
    'would','could','may','might','can','will','does','do','did','has','have','had','about','into','after','before','during','while',
    'client','nurse','rn','patient','following','action','statement','response','finding','findings','indicates','appropriate','priority'
}


def norm_text(s: str) -> str:
    s = unicodedata.normalize('NFKC', s or '').lower()
    s = s.replace('’', "'").replace('–', '-').replace('—', '-')
    s = re.sub(r"[^a-z0-9]+", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def tokens(s: str) -> set[str]:
    return {w for w in norm_text(s).split() if len(w) >= 3 and w not in STOP}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if not DB.exists():
        raise SystemExit(f'BLOCKED missing {DB}')
    before_sha = sha256(DB)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
    rows = con.execute('SELECT question_uid, stable_sort_key, stem FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    if integrity != 'ok' or len(rows) != EXPECTED_COUNT:
        raise SystemExit(f'BLOCKED integrity={integrity} count={len(rows)}')

    uid_counts = Counter(r['question_uid'] for r in rows)
    duplicate_uid_groups = sorted([u for u,c in uid_counts.items() if c > 1])

    raw_groups = defaultdict(list)
    norm_groups = defaultdict(list)
    for r in rows:
        stem = (r['stem'] or '').strip()
        raw_groups[stem].append(r['question_uid'])
        norm_groups[norm_text(stem)].append(r['question_uid'])

    exact_raw = [
        {'stem': k, 'uids': v, 'count': len(v)}
        for k,v in raw_groups.items() if k and len(v) > 1
    ]
    exact_norm = [
        {'normalized_stem': k, 'uids': v, 'count': len(v)}
        for k,v in norm_groups.items() if k and len(v) > 1
    ]

    stems = [r['stem'] or '' for r in rows]
    norms = [norm_text(s) for s in stems]
    toks = [tokens(s) for s in stems]
    uids = [r['question_uid'] for r in rows]

    inv = defaultdict(list)
    for i, ts in enumerate(toks):
        for t in ts:
            inv[t].append(i)

    candidates = set()
    for t, ids in inv.items():
        if 2 <= len(ids) <= 60:
            for a_pos in range(len(ids)):
                a = ids[a_pos]
                for b_pos in range(a_pos + 1, len(ids)):
                    b = ids[b_pos]
                    candidates.add((a,b))

    high = []
    review = []
    for a,b in candidates:
        if norms[a] == norms[b]:
            continue
        ta, tb = toks[a], toks[b]
        if min(len(ta), len(tb)) < 6:
            continue
        inter = len(ta & tb)
        if inter < 5:
            continue
        union = len(ta | tb)
        jac = inter / union if union else 0.0
        contain = inter / min(len(ta), len(tb))
        if jac < 0.55 and contain < 0.72:
            continue
        seq = SequenceMatcher(None, norms[a], norms[b], autojunk=False).ratio()
        rec = {
            'uid_a': uids[a], 'uid_b': uids[b],
            'jaccard': round(jac, 4), 'containment': round(contain, 4), 'sequence_ratio': round(seq, 4),
            'stem_a': stems[a], 'stem_b': stems[b],
        }
        if jac >= 0.82 or seq >= 0.92 or contain >= 0.94:
            high.append(rec)
        elif (jac >= 0.72 and seq >= 0.78) or (contain >= 0.86 and seq >= 0.72):
            review.append(rec)

    score = lambda x: max(x['jaccard'], x['containment'], x['sequence_ratio'])
    high.sort(key=score, reverse=True)
    review.sort(key=score, reverse=True)

    con.close()
    after_sha = sha256(DB)
    if after_sha != before_sha:
        raise SystemExit('BLOCKED duplicate scan modified DB')

    report = {
        'status': 'FULL_3525_DUPLICATE_SCAN_PASS',
        'db_file': str(DB),
        'db_sha256_before': before_sha,
        'db_sha256_after': after_sha,
        'db_modified': False,
        'sqlite_integrity_check': integrity,
        'question_count': len(rows),
        'duplicate_question_uid_groups': len(duplicate_uid_groups),
        'duplicate_question_uids': duplicate_uid_groups,
        'exact_raw_stem_duplicate_groups': len(exact_raw),
        'exact_raw_stem_duplicate_rows': sum(x['count'] for x in exact_raw),
        'exact_raw_stem_duplicates': exact_raw,
        'normalized_stem_duplicate_groups': len(exact_norm),
        'normalized_stem_duplicate_rows': sum(x['count'] for x in exact_norm),
        'normalized_stem_duplicates': exact_norm,
        'lexical_candidate_pairs_screened': len(candidates),
        'high_confidence_near_duplicate_pairs': len(high),
        'high_confidence_pairs': high[:250],
        'manual_review_near_duplicate_pairs': len(review),
        'manual_review_pairs_top': review[:250],
        'method_note': 'Exact duplicate checks use raw and punctuation/case-normalized stems. Near-duplicate checks use meaningful-token overlap plus character-sequence similarity; this detects identical and strongly similar wording but is not a clinical semantic-concept audit.'
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('DUPLICATE_SCAN=' + json.dumps({
        'status': report['status'],
        'question_count': report['question_count'],
        'duplicate_uid_groups': report['duplicate_question_uid_groups'],
        'exact_raw_groups': report['exact_raw_stem_duplicate_groups'],
        'normalized_groups': report['normalized_stem_duplicate_groups'],
        'high_confidence_near_pairs': report['high_confidence_near_duplicate_pairs'],
        'manual_review_pairs': report['manual_review_near_duplicate_pairs'],
        'db_sha256': before_sha,
        'integrity': integrity,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
