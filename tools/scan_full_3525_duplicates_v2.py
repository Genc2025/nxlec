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
OUT = Path('RULE1_FULL_3525_DUPLICATE_SCAN_V2.json')
EXPECTED = 3525
STOP = {
    'the','a','an','and','or','of','to','in','on','for','with','by','at','from','as','is','are','was','were','be','been','being',
    'that','this','these','those','which','what','when','where','who','whom','whose','why','how','most','best','first','next','should',
    'would','could','may','might','can','will','does','do','did','has','have','had','about','into','after','before','during','while',
    'client','nurse','rn','patient','following','action','statement','response','finding','findings','indicates','appropriate','priority'
}


def norm(s: str) -> str:
    s = unicodedata.normalize('NFKC', s or '').lower()
    s = s.replace('’', "'").replace('–','-').replace('—','-')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(s: str) -> set[str]:
    return {w for w in norm(s).split() if len(w) >= 3 and w not in STOP}


def canon_json_text(s: str) -> str:
    try:
        return json.dumps(json.loads(s), ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    except Exception:
        return (s or '').strip()


def dbsha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def options_signature(item_s: str, correct_s: str):
    try:
        item = json.loads(item_s)
        corr = json.loads(correct_s)
    except Exception:
        return None
    opts = item.get('options') if isinstance(item, dict) else None
    if not isinstance(opts, dict) or not opts:
        return None
    values = [norm(str(v)) for v in opts.values()]
    if any(not v for v in values):
        return None
    correct_text = ''
    if isinstance(corr, dict):
        key = corr.get('correct_option')
        if key in opts:
            correct_text = norm(str(opts[key]))
    return (tuple(sorted(values)), correct_text)


def group_records(groups, rows, key_label):
    out=[]
    for k, ids in groups.items():
        if len(ids) <= 1:
            continue
        out.append({key_label: k if isinstance(k, str) else str(k), 'uids':[rows[i]['question_uid'] for i in ids], 'count':len(ids)})
    out.sort(key=lambda x:(-x['count'], x['uids']))
    return out


def main():
    before = dbsha(DB)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
    rows = con.execute('SELECT question_uid, mode, case_uid, stem, item_data_json, correct_answer_json FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    if integrity != 'ok' or len(rows) != EXPECTED:
        raise SystemExit(f'BLOCKED integrity={integrity} count={len(rows)}')

    uid_dups = [u for u,c in Counter(r['question_uid'] for r in rows).items() if c>1]

    full_exact = defaultdict(list)
    full_norm = defaultdict(list)
    standalone_stem = defaultdict(list)
    standalone_norm_stem = defaultdict(list)
    mc_order_independent = defaultdict(list)

    standalone_indices=[]
    for i,r in enumerate(rows):
        stem=(r['stem'] or '').strip()
        key=(stem, canon_json_text(r['item_data_json']), canon_json_text(r['correct_answer_json']))
        full_exact[key].append(i)
        keyn=(norm(stem), canon_json_text(r['item_data_json']), canon_json_text(r['correct_answer_json']))
        full_norm[keyn].append(i)
        is_standalone = r['case_uid'] in (None, '')
        if is_standalone:
            standalone_indices.append(i)
            standalone_stem[stem].append(i)
            standalone_norm_stem[norm(stem)].append(i)
        sig=options_signature(r['item_data_json'], r['correct_answer_json'])
        if sig is not None:
            mc_order_independent[(norm(stem), sig)].append(i)

    exact_full_groups=[]
    for k,ids in full_exact.items():
        if len(ids)>1:
            exact_full_groups.append({'uids':[rows[i]['question_uid'] for i in ids], 'count':len(ids), 'stem':rows[ids[0]]['stem'], 'case_uids':[rows[i]['case_uid'] for i in ids]})
    exact_full_groups.sort(key=lambda x:(-x['count'], x['uids']))

    norm_full_groups=[]
    for k,ids in full_norm.items():
        if len(ids)>1:
            norm_full_groups.append({'uids':[rows[i]['question_uid'] for i in ids], 'count':len(ids), 'stem':rows[ids[0]]['stem'], 'case_uids':[rows[i]['case_uid'] for i in ids]})
    norm_full_groups.sort(key=lambda x:(-x['count'], x['uids']))

    standalone_exact=[]
    for k,ids in standalone_stem.items():
        if k and len(ids)>1:
            standalone_exact.append({'stem':k,'uids':[rows[i]['question_uid'] for i in ids],'count':len(ids)})
    standalone_exact.sort(key=lambda x:(-x['count'],x['uids']))

    standalone_norm=[]
    for k,ids in standalone_norm_stem.items():
        if k and len(ids)>1:
            standalone_norm.append({'normalized_stem':k,'uids':[rows[i]['question_uid'] for i in ids],'count':len(ids)})
    standalone_norm.sort(key=lambda x:(-x['count'],x['uids']))

    mc_dup=[]
    for k,ids in mc_order_independent.items():
        if len(ids)>1:
            mc_dup.append({'uids':[rows[i]['question_uid'] for i in ids], 'count':len(ids), 'stem':rows[ids[0]]['stem'], 'case_uids':[rows[i]['case_uid'] for i in ids]})
    mc_dup.sort(key=lambda x:(-x['count'],x['uids']))

    # High-similarity stem scan only among standalone questions to avoid NGN template-prompt false positives.
    st_norm={i:norm(rows[i]['stem'] or '') for i in standalone_indices}
    st_tok={i:toks(rows[i]['stem'] or '') for i in standalone_indices}
    inv=defaultdict(list)
    for i in standalone_indices:
        for t in st_tok[i]:
            inv[t].append(i)
    cand=set()
    for ids in inv.values():
        if 2 <= len(ids) <= 60:
            for x in range(len(ids)):
                for y in range(x+1,len(ids)):
                    cand.add((ids[x],ids[y]))
    high=[]
    review=[]
    for a,b in cand:
        if st_norm[a] == st_norm[b]:
            continue
        ta,tb=st_tok[a],st_tok[b]
        if min(len(ta),len(tb))<6:
            continue
        inter=len(ta&tb)
        if inter<5:
            continue
        jac=inter/len(ta|tb)
        contain=inter/min(len(ta),len(tb))
        if jac<0.55 and contain<0.72:
            continue
        seq=SequenceMatcher(None,st_norm[a],st_norm[b],autojunk=False).ratio()
        rec={'uid_a':rows[a]['question_uid'],'uid_b':rows[b]['question_uid'],'jaccard':round(jac,4),'containment':round(contain,4),'sequence_ratio':round(seq,4),'stem_a':rows[a]['stem'],'stem_b':rows[b]['stem']}
        if jac>=0.82 or seq>=0.92 or contain>=0.94:
            high.append(rec)
        elif (jac>=0.72 and seq>=0.78) or (contain>=0.86 and seq>=0.72):
            review.append(rec)
    score=lambda x:max(x['jaccard'],x['containment'],x['sequence_ratio'])
    high.sort(key=score,reverse=True)
    review.sort(key=score,reverse=True)

    con.close()
    after=dbsha(DB)
    if after!=before:
        raise SystemExit('BLOCKED DB modified during scan')

    report={
        'status':'FULL_3525_CONTENT_AWARE_DUPLICATE_SCAN_PASS',
        'db_file':str(DB),
        'db_sha256_before':before,
        'db_sha256_after':after,
        'db_modified':False,
        'sqlite_integrity_check':integrity,
        'question_count':len(rows),
        'standalone_question_count':len(standalone_indices),
        'case_study_question_count':len(rows)-len(standalone_indices),
        'duplicate_question_uid_groups':len(uid_dups),
        'exact_full_question_payload_duplicate_groups':len(exact_full_groups),
        'exact_full_question_payload_duplicates':exact_full_groups,
        'normalized_full_question_payload_duplicate_groups':len(norm_full_groups),
        'normalized_full_question_payload_duplicates':norm_full_groups,
        'standalone_exact_stem_duplicate_groups':len(standalone_exact),
        'standalone_exact_stem_duplicates':standalone_exact,
        'standalone_normalized_stem_duplicate_groups':len(standalone_norm),
        'standalone_normalized_stem_duplicates':standalone_norm,
        'order_independent_mc_content_duplicate_groups':len(mc_dup),
        'order_independent_mc_content_duplicates':mc_dup,
        'standalone_lexical_candidate_pairs_screened':len(cand),
        'standalone_high_confidence_near_duplicate_pairs':len(high),
        'standalone_high_confidence_pairs':high[:300],
        'standalone_manual_review_near_duplicate_pairs':len(review),
        'standalone_manual_review_pairs_top':review[:300],
        'interpretation_note':'Exact full-payload and order-independent MC groups are strong duplicate signals. Repeated generic NGN case-study stems are not treated as duplicate questions unless their payload also matches. Near-duplicate results are restricted to standalone stems and remain screening candidates, not automatic duplicate findings.'
    }
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('DUPLICATE_SCAN_V2='+json.dumps({
        'status':report['status'],'count':report['question_count'],'standalone':report['standalone_question_count'],'case_study':report['case_study_question_count'],
        'uid_dup_groups':report['duplicate_question_uid_groups'],'exact_full_groups':report['exact_full_question_payload_duplicate_groups'],
        'normalized_full_groups':report['normalized_full_question_payload_duplicate_groups'],'standalone_exact_stem_groups':report['standalone_exact_stem_duplicate_groups'],
        'mc_content_groups':report['order_independent_mc_content_duplicate_groups'],'standalone_high_near_pairs':report['standalone_high_confidence_near_duplicate_pairs'],
        'standalone_review_pairs':report['standalone_manual_review_near_duplicate_pairs'],'integrity':integrity,'db_sha256':before
    },sort_keys=True))


if __name__=='__main__':
    main()
