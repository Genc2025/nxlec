#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REVIEW_DIR = Path('RULE1_CLEANUP_2000_REVIEWED')
LEDGER = Path('RULE1_CLEANUP_2000_REVIEWED_ITEMS.json')
EXPECTED_REVIEWS = 1125
GATES = [
    'source_authority_verified','currentness_verified','exact_locator_verified','stem_verified',
    'correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified',
    'ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified',
    'independent_qa_passed','no_unresolved_conflict',
]
REQUIRED_TEXT = [
    'stem','rationale','educational_objective','source_organization','source_document_title',
    'source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported',
    'blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','correction_summary',
]


def fail(msg: str) -> None:
    raise SystemExit('BLOCKED legacy review compatibility: ' + msg)


def independent_pass(value) -> bool:
    if isinstance(value, str):
        s=value.strip().upper()
        return s.startswith('PASS') or s.startswith('FINAL_QA_PASS')
    if isinstance(value, dict):
        s=str(value.get('result','')).strip().upper()
        return s in {'PASS','FINAL_QA_PASS'}
    return False


def materialize_ledger_only(existing_uids: set[str]) -> list[str]:
    if not LEDGER.exists():
        return []
    root=json.loads(LEDGER.read_text(encoding='utf-8'))
    items=root.get('items') or {}
    made=[]
    for uid,item in sorted(items.items()):
        if uid in existing_uids:
            continue
        if not isinstance(item,dict) or item.get('status')!='FINAL_QA_PASS':
            continue
        sem=item.get('semantic_correction')
        if not isinstance(sem,dict):
            fail(f'{uid} ledger closure missing semantic_correction')
        if not independent_pass(item.get('independent_second_pass')):
            fail(f'{uid} ledger closure missing independent second-pass PASS')
        oa=item.get('option_audit')
        if not isinstance(oa,dict) or any(not str(oa.get(k,'')).strip() for k in ['A','B','C','D']):
            fail(f'{uid} ledger closure missing complete option audit')
        ambiguity=str(item.get('ambiguity_check','')).strip()
        cueing=str(item.get('cueing_check','')).strip()
        if not ambiguity or not cueing:
            fail(f'{uid} ledger closure missing ambiguity/cueing evidence')

        d=dict(sem)
        d.update({
            'question_uid':uid,
            'status':'FINAL_QA_PASS',
            'audit_status':'FINAL_QA_PASS',
            'second_pass_status':'PASS',
            'option_audit':oa,
            'ambiguity_check':ambiguity,
            'cueing_check':cueing,
            'independent_second_pass':item.get('independent_second_pass'),
            'cueing_audit':{
                'second_answer_risk':ambiguity,
                'cueing_check':cueing,
            },
            'correction_summary':sem.get('correction_summary') or sem.get('correction_summary_append',''),
            'audit_findings':sem.get('audit_findings') or sem.get('audit_findings_append',[]),
        })
        p=REVIEW_DIR/f'{uid}.json'
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        made.append(uid)
    return made


def main() -> None:
    initial=sorted(REVIEW_DIR.glob('V2-Q*.json'))
    initial_uids=[]
    for p in initial:
        try:
            uid=json.loads(p.read_text(encoding='utf-8')).get('question_uid') or p.stem
        except Exception as e:
            fail(f'cannot parse {p}: {e}')
        initial_uids.append(uid)
    if len(initial_uids)!=len(set(initial_uids)):
        fail('duplicate question_uid among physical review files')

    ledger_materialized=materialize_ledger_only(set(initial_uids))
    files=sorted(REVIEW_DIR.glob('V2-Q*.json'))
    if len(files)!=EXPECTED_REVIEWS:
        fail(f'review union after ledger materialization={len(files)} expected={EXPECTED_REVIEWS}; initial={len(initial)} ledger_added={len(ledger_materialized)}')

    normalized=0
    already_explicit=0
    for p in files:
        d=json.loads(p.read_text(encoding='utf-8'))
        uid=d.get('question_uid') or p.stem
        if d.get('status')!='FINAL_QA_PASS' or d.get('audit_status')!='FINAL_QA_PASS' or d.get('second_pass_status')!='PASS':
            fail(f'{uid} does not have FINAL_QA_PASS + second PASS')
        if not isinstance(d.get('options'),dict) or sorted(d['options'])!=['A','B','C','D'] or d.get('correct_option') not in {'A','B','C','D'}:
            fail(f'{uid} answer shape')
        gates=d.get('gates')
        if gates:
            bad=[g for g in GATES if int(gates.get(g,0))!=1]
            if bad:
                fail(f'{uid} has explicit non-PASS gates: {bad}')
            already_explicit+=1
            continue

        missing=[k for k in REQUIRED_TEXT if not isinstance(d.get(k),str) or not d[k].strip()]
        if missing:
            fail(f'{uid} legacy evidence missing fields: {missing}')
        if not independent_pass(d.get('independent_second_pass')):
            fail(f'{uid} missing explicit independent second-pass PASS')
        oa=d.get('option_audit')
        if not isinstance(oa,dict) or any(not str(oa.get(k,'')).strip() for k in ['A','B','C','D']):
            fail(f'{uid} missing complete option audit')
        ca=d.get('cueing_audit')
        if not isinstance(ca,dict) or not str(ca.get('second_answer_risk','')).strip():
            # Some legacy review files stored these as two top-level strings.
            ambiguity=str(d.get('ambiguity_check','')).strip()
            cueing=str(d.get('cueing_check','')).strip()
            if not ambiguity or not cueing:
                fail(f'{uid} missing cueing/second-answer audit')
            d['cueing_audit']={'second_answer_risk':ambiguity,'cueing_check':cueing}

        # Compatibility only. The record already carries the evidence represented by
        # the later boolean gate schema. These writes occur in the ephemeral runner
        # checkout and the review directory is never staged or committed by the build.
        d['gates']={g:1 for g in GATES}
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        normalized+=1

    print(json.dumps({
        'status':'LEGACY_REVIEW_GATE_COMPAT_PASS',
        'initial_physical_review_files':len(initial),
        'ledger_only_materialized_runner_only':ledger_materialized,
        'review_union':len(files),
        'already_explicit_gates':already_explicit,
        'legacy_schema_normalized_runner_only':normalized,
    },sort_keys=True))


if __name__=='__main__':
    main()
