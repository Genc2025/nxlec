#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3
from collections import Counter
from pathlib import Path

DB=Path('NCLEX_CANONICAL.db')
CORR=Path('RULE1_CLEANUP_2000_CORRECTIONS.json')
RESULT=Path('RULE1_CLEANUP_2000_RESULT.json')
OUT=Path('RULE1_CLEANUP_2000_REGRESSION.json')
KEYS=['A','B','C','D']
GATES=['source_authority_verified','currentness_verified','exact_locator_verified','stem_verified','correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified','ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified','independent_qa_passed','no_unresolved_conflict']
ABS_RE=re.compile(r'\b(always|never|only|completely|entirely|all|none|guarantee(?:d|s)?|must|every|exactly|immediately|solely|regardless|automatically)\b',re.I)
REQUIRED=['question_uid','client_need','difficulty','stem','item_data_json','correct_answer_json','rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_source_organization','blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','blueprint_topic','audit_status','second_pass_status','audit_reviewer','payload_sha256']
EXACT_FIELDS=['stem','rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_topic']

def norm(s): return re.sub(r'[^a-z0-9]+',' ',(s or '').lower()).strip()

def flags_for(row):
    opts=json.loads(row['item_data_json'])['options']; ck=json.loads(row['correct_answer_json'])['correct_option']
    lens={k:len(str(opts[k]).strip()) for k in KEYS}; cl=lens[ck]; ds=[lens[k] for k in KEYS if k!=ck]; mean=sum(ds)/3
    absn={k:bool(ABS_RE.search(str(opts[k]))) for k in KEYS}; distractor_abs=sum(absn[k] for k in KEYS if k!=ck)
    strong=(cl>=1.8*mean and cl-mean>=70) or (not absn[ck] and distractor_abs>=2 and cl>=1.5*mean and cl-mean>=45)
    tier2=(cl>=1.6*mean and cl-mean>=55) or (not absn[ck] and distractor_abs>=2 and cl>=1.35*mean and cl-mean>=30)
    return strong,tier2

def main():
    cfg=json.loads(CORR.read_text(encoding='utf-8')); result=json.loads(RESULT.read_text(encoding='utf-8'))
    sem=cfg['semantic_corrections']; required=set(cfg['required_semantic_review_uids']); reviewed=set(cfg['semantic_reviewed_uids'])
    if len(sem)!=502 or required!=reviewed or required!=set(sem): raise SystemExit(f'BLOCKED semantic spec counts sem={len(sem)} required={len(required)} reviewed={len(reviewed)}')
    if result.get('status')!='STAGING_CLEANUP_PASS' or result.get('semantic_corrections_applied')!=502: raise SystemExit(f'BLOCKED cleanup result {result}')
    con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True); con.row_factory=sqlite3.Row
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise SystemExit('BLOCKED integrity')
    rows=con.execute('SELECT * FROM questions ORDER BY stable_sort_key,question_uid').fetchall(); by={r['question_uid']:r for r in rows}
    if len(rows)!=2000: raise SystemExit(f'BLOCKED count {len(rows)}')
    if len(by)!=2000: raise SystemExit('BLOCKED duplicate UID')
    missing=[]; malformed=[]; strong=[]; tier2=[]
    for r in rows:
        for f in REQUIRED:
            v=r[f]
            if v is None or (isinstance(v,str) and not v.strip()): missing.append((r['question_uid'],f))
        if r['audit_status']!='FINAL_QA_PASS' or r['second_pass_status']!='PASS' or any(r[g]!=1 for g in GATES): raise SystemExit(f'BLOCKED status/gate {r["question_uid"]}')
        try:
            opts=json.loads(r['item_data_json'])['options']; ans=json.loads(r['correct_answer_json'])['correct_option']
            if sorted(opts)!=KEYS or ans not in KEYS or not str(opts[ans]).strip(): malformed.append(r['question_uid'])
        except Exception: malformed.append(r['question_uid']); continue
        a,b=flags_for(r)
        if a: strong.append(r['question_uid'])
        if b: tier2.append(r['question_uid'])
    if missing: raise SystemExit(f'BLOCKED missing fields {missing[:20]} total={len(missing)}')
    if malformed: raise SystemExit(f'BLOCKED malformed items {malformed[:20]} total={len(malformed)}')
    if strong or tier2: raise SystemExit(f'BLOCKED cueing regression strong={strong[:20]}({len(strong)}) tier2={tier2[:20]}({len(tier2)})')
    keys=Counter(json.loads(r['correct_answer_json'])['correct_option'] for r in rows)
    if keys!=Counter({'A':500,'B':500,'C':500,'D':500}): raise SystemExit(f'BLOCKED key balance {keys}')
    if any(r['client_need']=='Safety & Infection Prevention and Control' for r in rows): raise SystemExit('BLOCKED client-name normalization')
    if any(r['difficulty'] not in {'easy','medium','hard'} for r in rows): raise SystemExit('BLOCKED difficulty normalization')
    if any(r['blueprint_document_title']!='2026 NCLEX-RN Test Plan' or r['blueprint_version']!='Effective April 1, 2026 through March 31, 2029' for r in rows): raise SystemExit('BLOCKED blueprint normalization')
    stems=Counter(norm(r['stem']) for r in rows)
    dup_stems=[k for k,v in stems.items() if k and v>1]
    if dup_stems: raise SystemExit(f'BLOCKED normalized duplicate stems {len(dup_stems)}')
    exact_fail=[]
    for uid,s in sem.items():
        r=by.get(uid)
        if r is None: exact_fail.append((uid,'missing')); continue
        for f in EXACT_FIELDS:
            if f in s and r[f]!=s[f]: exact_fail.append((uid,f))
        if 'options' in s:
            actual=json.loads(r['item_data_json'])['options']
            if Counter(actual.values())!=Counter(s['options'].values()): exact_fail.append((uid,'option_multiset'))
            if 'correct_option' in s:
                want=s['options'][s['correct_option']]
                actual_key=json.loads(r['correct_answer_json'])['correct_option']
                if actual[actual_key]!=want: exact_fail.append((uid,'correct_answer_text'))
        if s.get('correction_summary_append') and s['correction_summary_append'].strip() not in r['correction_summary']:
            exact_fail.append((uid,'correction_summary_append'))
    if exact_fail: raise SystemExit(f'BLOCKED semantic exact verification {exact_fail[:25]} total={len(exact_fail)}')
    out={
      'status':'POST_WRITE_REGRESSION_PASS','count':2000,'integrity':'ok','semantic_corrections_verified':'502/502',
      'strong_cueing_flags':0,'tier2_cueing_flags':0,'normalized_duplicate_stem_groups':0,'malformed_items':0,
      'required_fields_complete':'2000/2000','final_qa_pass':'2000/2000','independent_second_pass':'2000/2000','all_14_gates':'2000/2000',
      'answer_key_distribution':dict(keys),'client_need_labels':dict(Counter(r['client_need'] for r in rows)),
      'difficulty_labels':dict(Counter(r['difficulty'] for r in rows))
    }
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_CLEANUP_REGRESSION='+json.dumps(out,ensure_ascii=False,separators=(',',':')))
    con.close()

if __name__=='__main__': main()
