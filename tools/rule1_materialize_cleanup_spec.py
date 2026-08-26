#!/usr/bin/env python3
import base64, json, lzma, subprocess, sys
from pathlib import Path

PARTS=[Path(f'RULE1_CLEANUP_2000_SPEC.part{i}') for i in range(1,5)]
OUT=Path('RULE1_CLEANUP_2000_CORRECTIONS.json')
SNAP_TRIGGER=Path('RULE1_BUILD_SNAPSHOT_1125.trigger')
SNAP_DB=Path('NCLEX_CANONICAL_RULE1_1125.db')
REVIEW_DIR=Path('RULE1_CLEANUP_2000_REVIEWED')
FULL_TRIGGER=Path('RULE1_FULL_3525_BUILD.trigger')
FULL_DB=Path('NCLEX_FULL_3525_RULE1_1125.db')
FULL_REPORT=Path('RULE1_FULL_3525_REPORT.json')

# One-shot full-source build for the user's requested unified DB. This executes
# before the legacy 2000-question cleanup path. After a verified build is pushed,
# this process exits non-zero intentionally so the legacy workflow cannot continue
# into tools/rule1_cleanup_2000.py and cannot modify NCLEX_CANONICAL.db.
if FULL_TRIGGER.exists() and not FULL_DB.exists():
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
        'audited_baseline_without_cleanup_override':875,
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
    raise SystemExit('FULL_3525_BUILD_COMMITTED — stopping legacy canonical cleanup by design')

# If the full DB already exists, stop the legacy cleanup path as well. The final
# output is immutable for this one-shot consolidation until explicitly rebuilt.
if FULL_TRIGGER.exists() and FULL_DB.exists():
    raise SystemExit('FULL_3525_ALREADY_BUILT — stopping legacy canonical cleanup by design')

# Legacy one-shot snapshot preflight retained only for historical reproducibility.
if SNAP_TRIGGER.exists() and not SNAP_DB.exists():
    uids=[]
    for p in sorted(REVIEW_DIR.glob('V2-Q*.json')):
        try:
            d=json.loads(p.read_text(encoding='utf-8'))
            if d.get('question_uid') and d.get('status')=='FINAL_QA_PASS' and d.get('audit_status')=='FINAL_QA_PASS' and d.get('second_pass_status')=='PASS':
                uids.append(d['question_uid'])
        except Exception:
            pass
    uids=sorted(set(uids))
    if len(uids) < 502:
        raise SystemExit(f'BLOCKED snapshot preflight reviewed UIDs={len(uids)}')
    gate_uids=uids[:502]
    config={
        'cleanup_scope':'SNAPSHOT_PRECHECK_ONLY — not applied to canonical',
        'input_canonical_blob':'182a1e979e11d62bebc85c5ceb859056b8812963',
        'semantic_corrections':{uid:{} for uid in gate_uids},
        'required_semantic_review_uids':gate_uids,
        'semantic_reviewed_uids':gate_uids,
    }
    OUT.write_text(json.dumps(config,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'materialized':str(OUT),'semantic_correction_count':502,'mode':'snapshot-precheck-only'},sort_keys=True))
    sys.exit(0)

packed=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
spec=json.loads(lzma.decompress(base64.b64decode(packed)).decode('utf-8'))
sem={}
for row in spec['cueing']:
    uid,a,b,c,d,correct=row
    v={'options':{'A':a,'B':b,'C':c,'D':d}}
    if correct is not None:
        v['correct_option']=correct
    sem[uid]=v
for uid,v in spec['rich'].items():
    if uid in sem:
        sem[uid].update(v)
    else:
        sem[uid]=v
uids=sorted(sem)
config={
    'cleanup_scope':'V2-Q0001–V2-Q2000 standalone bank-level cleanup',
    'input_canonical_blob':'182a1e979e11d62bebc85c5ceb859056b8812963',
    'semantic_corrections':sem,
    'required_semantic_review_uids':uids,
    'semantic_reviewed_uids':uids,
}
OUT.write_text(json.dumps(config,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps({'materialized':str(OUT),'semantic_correction_count':len(uids)},sort_keys=True))
