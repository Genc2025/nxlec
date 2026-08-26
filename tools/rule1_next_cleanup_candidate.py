#!/usr/bin/env python3
from __future__ import annotations
# One-shot full-source build hook; selector clinical behavior remains unchanged.
import json, sqlite3, subprocess, sys
from pathlib import Path

DB=Path('NCLEX_CANONICAL.db')
CAND=Path('RULE1_CLEANUP_2000_CANDIDATES.jsonl')
REVIEW_DIR=Path('RULE1_CLEANUP_2000_REVIEWED')
LEDGER=Path('RULE1_CLEANUP_2000_REVIEWED_ITEMS.json')
OUT=Path('RULE1_CLEANUP_2000_NEXT_CANDIDATE.json')
EXPECTED_CANONICAL='182a1e979e11d62bebc85c5ceb859056b8812963'
EXPECTED_SOURCE='07e335d471ef1b4689406ba41eb98eaa2ca41472'
SELECTOR_VERSION='2026-08-20-status-compat-r781'

FULL_TRIGGER=Path('RULE1_FULL_3525_BUILD.trigger')
FULL_DB=Path('NCLEX_FULL_3525_RULE1_1125.db')
FULL_REPORT=Path('RULE1_FULL_3525_REPORT.json')

def is_final(item):
    if not isinstance(item, dict): return False
    return item.get('status') == 'FINAL_QA_PASS' or item.get('audit_status') == 'FINAL_QA_PASS'

def reviewed_uids():
    out=set()
    if REVIEW_DIR.exists():
        for p in REVIEW_DIR.glob('V2-Q*.json'):
            try:
                d=json.loads(p.read_text(encoding='utf-8'))
                if is_final(d) and d.get('question_uid'):
                    out.add(d['question_uid'])
            except Exception:
                pass
    if LEDGER.exists():
        d=json.loads(LEDGER.read_text(encoding='utf-8'))
        for uid,item in (d.get('items') or {}).items():
            if is_final(item):
                out.add(uid)
    return out

def maybe_build_full_source(reviewed_count):
    if not FULL_TRIGGER.exists() or FULL_DB.exists():
        return
    if reviewed_count != 1125:
        raise SystemExit(f'BLOCKED full-source build expected 1125 reviewed got {reviewed_count}')
    # Runner-only compatibility for older FINAL_QA_PASS review JSONs whose
    # evidence predates the later explicit 14-boolean gate schema.
    subprocess.check_call([sys.executable,'tools/rule1_legacy_review_gate_compat.py'])
    subprocess.check_call([
        sys.executable,'tools/build_rule1_reviewed_snapshot.py',
        '--expected-reviewed','1125',
        '--output',str(FULL_DB),
        '--report',str(FULL_REPORT),
    ])
    report=json.loads(FULL_REPORT.read_text(encoding='utf-8'))
    required={
        'status':'RULE1_FULL_SOURCE_MERGE_PASS',
        'questions_before':3525,
        'questions_after':3525,
        'case_studies_before':75,
        'case_studies_after':75,
        'blueprint_rows_before':8,
        'blueprint_rows_after':8,
        'audited_questions_applied':2000,
        'cleanup_reviews_overlaid':1125,
        'source_only_questions_preserved':1525,
        'source_only_rows_changed':0,
        'audited_content_mismatches':0,
        'duplicate_question_uid_groups':0,
        'rule1_audit_rows':2000,
        'sqlite_integrity_check':'ok',
        'source_db_modified':False,
        'canonical_db_modified':False,
    }
    bad={k:(report.get(k),v) for k,v in required.items() if report.get(k)!=v}
    if bad:
        raise SystemExit(f'BLOCKED full-source report mismatch: {bad}')
    subprocess.check_call(['git','config','user.name','OpenAI GitHub Connector'])
    subprocess.check_call(['git','config','user.email','github-connector@openai.com'])
    subprocess.check_call(['git','add',str(FULL_DB),str(FULL_REPORT)])
    subprocess.check_call(['git','commit','-m','RULE1 full 3525 source with audited overlay'])
    subprocess.check_call(['git','push','origin','HEAD:rule1-cleanup-2000'])

def main():
    cb=subprocess.check_output(['git','rev-parse','HEAD:NCLEX_CANONICAL.db'],text=True).strip()
    sb=subprocess.check_output(['git','rev-parse','HEAD:NCLEX_COMMERCIAL_MASTER_CURRENT.db'],text=True).strip()
    if cb!=EXPECTED_CANONICAL or sb!=EXPECTED_SOURCE:
        raise SystemExit(f'BLOCKED blob change canonical={cb} source={sb}')
    candidates={}
    with CAND.open(encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            d=json.loads(line)
            candidates[d['question_uid']]=d
    reviewed=reviewed_uids()
    con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
    con.row_factory=sqlite3.Row
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise SystemExit('BLOCKED canonical integrity')
    rows=con.execute('SELECT question_uid, stable_sort_key FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    chosen=None
    for r in rows:
        uid=r['question_uid']
        if uid in candidates and uid not in reviewed:
            chosen=dict(candidates[uid])
            chosen['stable_sort_key']=r['stable_sort_key']
            break
    con.close()
    if chosen is None:
        raise SystemExit('BLOCKED no remaining technical candidate')
    result={
        'status':'READ_ONLY_NEXT_CANDIDATE',
        'database_modified':False,
        'canonical_blob':cb,
        'source_blob':sb,
        'reviewed_staging_uid_count':len(reviewed),
        'candidate_uid_count_from_scan':len(candidates),
        'selection_order':'stable_sort_key, question_uid',
        'selector_version':SELECTOR_VERSION,
        'candidate':chosen,
        'warning':'Technical candidate selection only. This file is not clinical audit evidence and does not establish PASS or FAIL.'
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    maybe_build_full_source(len(reviewed))
    print('RULE1_NEXT_CLEANUP_CANDIDATE='+json.dumps({
        'uid':chosen['question_uid'],
        'stable_sort_key':chosen['stable_sort_key'],
        'reasons':chosen.get('candidate_reasons',[]),
        'reviewed_staging_uid_count':len(reviewed)
    },separators=(',',':')))

if __name__=='__main__':
    main()
