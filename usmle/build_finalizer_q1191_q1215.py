#!/usr/bin/env python3
import ast
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
BASE = ROOT / 'step2_import_q1186_q1190.py'
OUT = ROOT / 'step2_import_q1191_q1215.py'
WF = REPO / '.github' / 'workflows' / 'usmle-step2-import-q1191-q1215.yml'
BASE_BLOB = '60c5063698fecd7b160304781953a3df3e1c9b9f'
PRE_DB = '987c82084e1906854c03fe21e7dfc4f9d46be923'

SPEC_ROWS = [
    ("batch_specs_1101_1200/12_q1191_q1195.json", "cbcec34a0d1791f344a9226305680bc2eec3debe", 1191, 1195),
    ("batch_specs_1101_1200/13_q1196_q1200.json", "854078c41087450d3d05729c4f2fa430f1b5573e", 1196, 1200),
    ("batch_specs_1201_1300/01_q1201_q1205.json", "1e350647b0f68ff2e7a20cbfc903949307306179", 1201, 1205),
    ("batch_specs_1201_1300/02_q1206_q1210.json", "6a6782a926c9b598539e3d9ef9ffc11cacc2916e", 1206, 1210),
    ("batch_specs_1201_1300/03_q1211_q1215.json", "fc6053ebafcf9751d2c00e5cb70264bbe9d7418a", 1211, 1215),
]

EXPECTED_BP = {
    "Human Development":33,
    "Respiratory and Renal/Urinary Systems":154,
    "Blood, Lymphoreticular and Immune Systems":127,
    "Behavioral Health, Nervous Systems and Special Senses":140,
    "Musculoskeletal, Skin and Subcutaneous Tissue":120,
    "Cardiovascular System":105,
    "Gastrointestinal System":99,
    "Reproductive and Endocrine Systems":161,
    "Multisystem Processes and Disorders":127,
    "Biostatistics, Epidemiology and Population Health":65,
    "Social Sciences: Communication and Interpersonal Skills":84,
}
EXPECTED_CP = {
    "Medical Knowledge: Applying Foundational Science Concepts":820,
    "Patient Care: Diagnosis, including history and physical examination":244,
    "Practice-Based Learning and Improvement":66,
    "Communication and Interpersonal Skills":85,
}
EXPECTED_DISC = {
    "Pathology":4,
    "Physiology":16,
    "Nutrition":0,
    "Gross Anatomy & Embryology":0,
    "Microbiology":0,
    "Pharmacology":0,
    "Behavioral Sciences":5,
    "Biochemistry":10,
    "Histology & Cell Biology":3,
    "Immunology":0,
    "Genetics":19,
}
KEY_SEQUENCE = 'CEBADDABECEACDBBDECAACBED'


def blob(path: pathlib.Path) -> str:
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(path.relative_to(REPO))], text=True).strip()


def replace_between(src: str, start: str, end: str, replacement: str) -> str:
    a = src.index(start)
    b = src.index(end, a)
    return src[:a] + replacement + src[b:]


def pyrepr(obj):
    return repr(obj)


def build_finalizer():
    if blob(BASE) != BASE_BLOB:
        raise SystemExit(f'base finalizer blob drift: {blob(BASE)}')
    src = BASE.read_text()

    config = f'''SPEC_FILES = [\n'''
    for rel, sha, lo, hi in SPEC_ROWS:
        config += f"    (ROOT / '{rel}', '{sha}', {lo}, {hi}),\n"
    config += f''']
EXPECTED_SPEC_BLOBS = {{str(p.relative_to(ROOT)):h for p,h,_,_ in SPEC_FILES}}
AUDIT_DIR = ROOT / 'audit'
PREFLIGHT = AUDIT_DIR / 'PREFLIGHT_Q1191_Q1215.json'
FORWARD = AUDIT_DIR / 'FORWARD_EXACT_Q1191_Q1215.json'
FINAL_AUDIT = AUDIT_DIR / 'STEP2_FINAL_10_10_Q0001_Q1215.json'
FINAL_STATE = ROOT / 'state' / 'step2_final_q0001_q1215.json'
FINAL_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

EXPECTED_PRE_DB_BLOB = '{PRE_DB}'
AUDIT_ID = 'STEP2-FINAL-Q0001-Q1215-20260904'
NEW_RANGE = range(1191,1216)
KEY_SEQUENCE = '{KEY_SEQUENCE}'
KEY_SCHEDULE = {{n:k for n,k in zip(NEW_RANGE,KEY_SEQUENCE)}}

EXPECTED_BLUEPRINT = {pyrepr(EXPECTED_BP)}
EXPECTED_COMPETENCIES = {pyrepr(EXPECTED_CP)}
OFFICIAL_DISCIPLINES = (
    'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology',
    'Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'
)
EXPECTED_NEW_DISCIPLINES = {pyrepr(EXPECTED_DISC)}
'''
    src = replace_between(src, "SPEC = ROOT / 'batch_specs_1101_1200' / '11_q1186_q1190.json'", 'GOV_ROOTS =', config)

    load_specs = '''def spec_blob_for_num(n):
    for p,h,lo,hi in SPEC_FILES:
        if lo <= n <= hi:
            return h
    raise SystemExit(f'no spec blob mapping for Q{n:04d}')

def load_specs():
    out={}
    for p,h,lo,hi in SPEC_FILES:
        got=file_blob(p)
        if got!=h:
            raise SystemExit(f'spec blob mismatch {p}: expected {h}, got {got}')
        arr=json.loads(p.read_text())
        expected=list(range(lo,hi+1))
        if not isinstance(arr,list) or [int(x.get('num',-1)) for x in arr] != expected:
            raise SystemExit(f'spec coverage/order failure {p}')
        for x in arr:
            n=int(x['num'])
            if n in out:
                raise SystemExit(f'duplicate staged spec Q{n:04d}')
            out[n]=x
    if sorted(out)!=list(NEW_RANGE):
        raise SystemExit('aggregate spec coverage failure')
    return out

'''
    src = replace_between(src, 'def load_specs():', 'def load_preflight():', load_specs)

    load_preflight = '''def load_preflight():
    p=json.loads(PREFLIGHT.read_text())
    if p.get('overall_status')!='PASS':
        raise SystemExit('preflight overall status not PASS')
    if p.get('authoritative_db_blob')!=EXPECTED_PRE_DB_BLOB or int(p.get('authoritative_final_count',-1))!=1190:
        raise SystemExit('preflight bound to wrong DB state')
    if p.get('spec_blobs')!=EXPECTED_SPEC_BLOBS or int(p.get('spec_count',-1))!=25:
        raise SystemExit('preflight spec binding/coverage failure')
    rows=p.get('items',[])
    if {int(x.get('num',-1)) for x in rows}!=set(NEW_RANGE):
        raise SystemExit('preflight item coverage failure')
    for x in rows:
        if x.get('status')!='PASS' or x.get('exact_or_semantic_hits') or x.get('unique_term_hits'):
            raise SystemExit(f"Q{int(x.get('num',-1)):04d} preflight overlap failure")
    if p.get('within_batch_collisions'):
        raise SystemExit('preflight within-batch collision')
    f=json.loads(FORWARD.read_text())
    if f.get('overall_status')!='PASS' or int(f.get('checked_item_count',-1))!=25 or int(f.get('clear_count',-1))!=25:
        raise SystemExit('forward exact overall/count failure')
    if f.get('authoritative_db_blob')!=EXPECTED_PRE_DB_BLOB or int(f.get('authoritative_final_count',-1))!=1190:
        raise SystemExit('forward exact DB binding failure')
    if f.get('spec_blobs')!=EXPECTED_SPEC_BLOBS:
        raise SystemExit('forward exact spec binding failure')
    for x in f.get('items',[]):
        if x.get('status')!='PASS' or x.get('canonical_hits') or x.get('canonical_main_term_hits'):
            raise SystemExit(f"Q{int(x.get('num',-1)):04d} forward exact failure")
    return p

'''
    src = replace_between(src, 'def load_preflight():', 'def load_audits():', load_preflight)

    load_audits = '''def load_audits():
    out={}
    for n in NEW_RANGE:
        p=AUDIT_DIR/f'Q{n:04d}_FINAL_10_10_AUDIT.json'
        if not p.exists():
            raise SystemExit('missing audit '+str(p))
        a=json.loads(p.read_text())
        if a.get('item')!=f'Q{n:04d}' or a.get('status')!='FINAL_10_10_PASS':
            raise SystemExit(f'Q{n:04d} audit identity/status failure')
        if a.get('authoritative_db_blob')!=EXPECTED_PRE_DB_BLOB or int(a.get('authoritative_db_final_count',-1))!=1190:
            raise SystemExit(f'Q{n:04d} audit DB binding failure')
        if a.get('exact_spec_sha')!=spec_blob_for_num(n):
            raise SystemExit(f'Q{n:04d} audit spec binding failure')
        if a.get('db_write') is not False or int(a.get('unresolved_conflicts',-1))!=0:
            raise SystemExit(f'Q{n:04d} staged/write/conflict failure')
        required={
            'source_authority':'PASS','exact_locator':'PASS','stem':'PASS','lead_in':'PASS',
            'correct_answer':'PASS','rationale':'PASS','educational_objective':'PASS',
            'ambiguity':'PASS','second_possible_answer':'PASS_NONE','cueing':'PASS','overlap':'PASS',
            'zero_unsupported_precision':'PASS','forward_exact_duplicate_check':'PASS',
            'canonical_main_construct_overlap':'PASS_NONE'
        }
        for k,v in required.items():
            if a.get(k)!=v:
                raise SystemExit(f'Q{n:04d}: audit gate {k}={a.get(k)!r}, expected {v!r}')
        if a.get('source_currentness',{}).get('status')!='PASS':
            raise SystemExit(f'Q{n:04d} source currentness failure')
        if a.get('distractors')!=['PASS']*4:
            raise SystemExit(f'Q{n:04d} distractor audit failure')
        if a.get('adversarial_second_pass',{}).get('result')!='PASS':
            raise SystemExit(f'Q{n:04d} adversarial second pass failure')
        expert=a.get('expert_review_layer',{})
        expert_required=('answer_granularity','mechanism_direction','temporal_sequence','scope_match','negative_evidence',
                         'distractor_ontology','answer_key_inversion','minimal_information','clinical_base_rate',
                         'units_numbers_thresholds','terminology_drift','source_disagreement','educational_objective_leakage',
                         'cross_item_contamination','expert_reviewer_reversal')
        if expert.get('status')!='PASS' or any(expert.get(k)!='PASS' for k in expert_required):
            raise SystemExit(f'Q{n:04d} expert layer failure')
        kig=a.get('key_integrity_gate',{})
        key_required=('factually_correct','stem_supports_key','lead_in_matches_answer_granularity',
                      'no_second_defensible_answer','no_authoritative_source_conflict','no_required_hidden_assumption')
        if kig.get('status')!='PASS' or any(kig.get(k)!='PASS' for k in key_required):
            raise SystemExit(f'Q{n:04d} key-integrity failure')
        rg=a.get('realism_gate',{})
        realism_required=('clinically_contextualized','foundational_science_application','stem_signal_to_noise',
                          'distractor_plausibility','option_parallelism','nbme_style_single_best_answer',
                          'core_step1_relevance','mechanism_depth')
        if rg.get('status')!='PASS' or any(rg.get(k)!='PASS' for k in realism_required):
            raise SystemExit(f'Q{n:04d} realism failure')
        dg=a.get('official_discipline_gate',{})
        if dg.get('status')!='PASS' or dg.get('all_tags_in_usmle_table3') is not True:
            raise SystemExit(f'Q{n:04d} discipline gate failure')
        tags=dg.get('tags',[])
        if not tags or any(t not in OFFICIAL_DISCIPLINES for t in tags):
            raise SystemExit(f'Q{n:04d} invalid discipline tags')
        out[n]=(a,p)
    return out

'''
    src = replace_between(src, 'def load_audits():', 'def build_payload', load_audits)

    replacements = {
        "'preflight_spec_blob':EXPECTED_SPEC_BLOB": "'preflight_spec_blob':spec_blob_for_num(n)",
        "'step2_audit_id':'STEP2-FINAL-Q1186-Q1190-20260904'": "'step2_audit_id':'STEP2-FINAL-Q1191-Q1215-20260904'",
        "len(old_items)!=1185 or len(old_reviews)!=1185": "len(old_items)!=1190 or len(old_reviews)!=1190",
        "expected 1185 authoritative finals/reviews": "expected 1190 authoritative finals/reviews",
        "set(range(1,1186))": "set(range(1,1191))",
        "Counter(KEY_SCHEDULE.values())!=Counter({'A':1,'B':1,'C':1,'D':1,'E':1})": "Counter(KEY_SCHEDULE.values())!=Counter({'A':5,'B':5,'C':5,'D':5,'E':5})",
        "if seq in ('ABCDE','BCDEA','CDEAB','DEABC','EABCD','EDCBA'):\n        raise SystemExit('answer-key schedule too patterned')": "if len(seq)!=25 or len(set(seq[i:i+5] for i in range(0,25,5)))<5:\n        raise SystemExit('answer-key schedule too patterned')",
        "qnum(c['candidate_id'])<=1185": "qnum(c['candidate_id'])<=1190",
        "(AUDIT_ID,1190,key_hash,aggregate_review_hash,FINAL_AT)": "(AUDIT_ID,1215,key_hash,aggregate_review_hash,FINAL_AT)",
        "if len(items)!=1190 or len(revs)!=1190": "if len(items)!=1215 or len(revs)!=1215",
        "set(range(1,1191))": "set(range(1,1216))",
        "Q1186-Q1190 exact-once failure": "Q1191-Q1215 exact-once failure",
        "if reread!=1190 or new!=5": "if reread!=1215 or new!=25",
        "fin[1]!=1190": "fin[1]!=1215",
        "'item_count':1190": "'item_count':1215",
        "'step2_final_review_count':1190": "'step2_final_review_count':1215",
        "'range':'Q1186-Q1190'": "'range':'Q1191-Q1215'",
        "'item_count':5": "'item_count':25",
        "'clinical_audit_files_verified':5": "'clinical_audit_files_verified':25",
        "'preflight_spec_blob':EXPECTED_SPEC_BLOB": "'preflight_spec_blobs':EXPECTED_SPEC_BLOBS",
        "'reread_verified_count':1190": "'reread_verified_count':1215",
        "'new_block_reread_verified_count':5": "'new_block_reread_verified_count':25",
        "'q1186_q1190_present_exactly_once':True": "'q1191_q1215_present_exactly_once':True",
        "'contiguous_q0001_q1190':True": "'contiguous_q0001_q1215':True",
    }
    for old,new in replacements.items():
        if old not in src:
            raise SystemExit('missing transform marker: '+old)
        src=src.replace(old,new)

    # Repair the pre-contiguity replacement that is intentionally different from post-contiguity.
    src=src.replace("old_ids!=review_ids or {qnum(cid) for cid in old_ids}!=set(range(1,1216))", "old_ids!=review_ids or {qnum(cid) for cid in old_ids}!=set(range(1,1191))")

    ast.parse(src)
    OUT.write_text(src)
    subprocess.check_call(['python','-m','py_compile',str(OUT)])


def build_workflow():
    wf = f'''name: USMLE Step2 Import Approved Q1191-Q1215

on:
  push:
    branches: [main]
    paths:
      - 'usmle/audit/STEP2_FINALIZE_TRIGGER_Q1191_Q1215'

permissions:
  contents: write

concurrency:
  group: usmle-step2-import-q1191-q1215
  cancel-in-progress: false

jobs:
  finalize:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v6
        with:
          ref: main
          fetch-depth: 0
      - uses: actions/setup-python@v6
        with:
          python-version: '3.12'
      - name: Compile finalizer
        run: python -m py_compile usmle/step2_import_q1191_q1215.py
      - name: Finalize twenty-five individually approved items
        run: python usmle/step2_import_q1191_q1215.py
      - name: Independently verify authoritative SQLite before persist
        run: |
          python - <<'PY'
          import hashlib,json,pathlib,re,sqlite3,subprocess
          from collections import Counter
          def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
          def h(o): return hashlib.sha256(canon(o).encode()).hexdigest()
          def qnum(cid):
              m=re.search(r'DIRECT-(\\d{{4}})',cid or '')
              assert m,cid
              return int(m.group(1))
          db='usmle/data/usmle-step1.db'
          con=sqlite3.connect(db)
          assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
          items=con.execute("SELECT candidate_id,payload_json,payload_sha256,audit_sha256 FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
          reviews=con.execute("SELECT candidate_id,review_json,review_sha256,final_status FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
          assert len(items)==1215 and len(reviews)==1215
          assert con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]==0
          assert con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_reviews GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]==0
          ids={{r[0] for r in items}}; rids={{r[0] for r in reviews}}
          assert ids==rids and {{qnum(x) for x in ids}}==set(range(1,1216))
          for n in range(1191,1216): assert sum(1 for cid in ids if qnum(cid)==n)==1
          payloads=[]; reread=0; new=0
          for cid,pj,ps,ash in items:
              obj=json.loads(pj); payloads.append(obj)
              assert h(obj)==ps,cid
              rr=con.execute('SELECT review_json,review_sha256,final_status FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone()
              assert rr and rr[1]==ash and rr[2]=='FINAL_10_10_PASS',cid
              rev=json.loads(rr[0])
              assert rev.get('review_sha256')==rr[1],cid
              assert obj.get('step2_final_audit',{{}}).get('review_sha256')==rr[1],cid
              assert len(obj['item']['options'])==5 and len(set(obj['item']['options'].values()))==5,cid
              assert len(obj.get('sources',[]))>=2 and all(s.get('section_locator') for s in obj['sources']),cid
              n=qnum(cid)
              if 1191<=n<=1215:
                  ca=rev.get('clinical_audit',{{}})
                  assert rev.get('verdict')=='FINAL_10_10_PASS',cid
                  assert ca.get('status')=='FINAL_10_10_PASS' and ca.get('unresolved_conflicts')==0,cid
                  assert ca.get('second_possible_answer')=='PASS_NONE',cid
                  assert ca.get('canonical_main_construct_overlap')=='PASS_NONE',cid
                  assert ca.get('forward_exact_duplicate_check')=='PASS',cid
                  assert ca.get('adversarial_second_pass',{{}}).get('result')=='PASS',cid
                  assert ca.get('expert_review_layer',{{}}).get('status')=='PASS',cid
                  assert ca.get('key_integrity_gate',{{}}).get('status')=='PASS',cid
                  assert ca.get('realism_gate',{{}}).get('status')=='PASS',cid
                  new+=1
              reread+=1
          assert reread==1215 and new==25
          expected_bp={pyrepr(EXPECTED_BP)}
          expected_cp={pyrepr(EXPECTED_CP)}
          expected_disc={pyrepr(EXPECTED_DISC)}
          assert dict(Counter(p['blueprint']['primary_system'] for p in payloads))==expected_bp
          assert dict(Counter(p['blueprint']['primary_competency'] for p in payloads))==expected_cp
          official=['Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology','Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics']
          nd=Counter()
          for p in payloads:
              if 1191<=qnum(p['candidate_id'])<=1215: nd.update(p['blueprint']['disciplines'])
          assert {{d:nd.get(d,0) for d in official}}==expected_disc
          state=json.load(open('usmle/state/step2_final_q0001_q1215.json'))
          audit=json.load(open('usmle/audit/STEP2_FINAL_10_10_Q0001_Q1215.json'))
          assert state==audit
          assert state['audit_id']=='STEP2-FINAL-Q0001-Q1215-20260904'
          assert state['item_count']==1215 and state['step2_final_review_count']==1215
          assert state['new_block']['range']=='Q1191-Q1215' and state['new_block']['item_count']==25
          assert state['new_block']['clinical_audit_files_verified']==25 and state['new_block']['preflight_verified'] is True
          assert state['pre_authoritative_db_blob']=='{PRE_DB}'
          blob=subprocess.check_output(['git','hash-object',db],text=True).strip()
          assert state['post_authoritative_db_blob']==blob and blob!=state['pre_authoritative_db_blob']
          assert state['sqlite_integrity_check']=='ok' and state['duplicate_candidate_id_count']==0
          assert state['reread_verified_count']==1215 and state['new_block_reread_verified_count']==25
          assert state['q1191_q1215_present_exactly_once'] is True and state['contiguous_q0001_q1215'] is True
          assert state['blueprint_counts']==expected_bp and state['competency_counts']==expected_cp
          assert state['official_discipline_new_block_counts']==expected_disc
          assert state['answer_position_new_block']['balanced']=={{'A':5,'B':5,'C':5,'D':5,'E':5}}
          assert state['answer_position_new_block']['sequence']=='{KEY_SEQUENCE}'
          fin=con.execute('SELECT audit_id,item_count FROM step2_finalization WHERE id=1').fetchone()
          assert fin==('STEP2-FINAL-Q0001-Q1215-20260904',1215),fin
          con.close()
          assert not pathlib.Path(db+'-wal').exists() and not pathlib.Path(db+'-shm').exists()
          print(json.dumps({{'integrity_check':'ok','items':1215,'reviews':1215,'duplicates':0,'reread':1215,'new_block':25,'post_db_blob':blob}},sort_keys=True))
          PY
      - name: Persist authoritative USMLE state
        run: |
          git config user.name 'USMLE Step2 Finalizer'
          git config user.email 'actions@users.noreply.github.com'
          git add -f usmle/data/usmle-step1.db usmle/audit/STEP2_FINAL_10_10_Q0001_Q1215.json usmle/state/step2_final_q0001_q1215.json
          git commit -m 'Finalize USMLE Step 1 Q1191-Q1215 at Step2 10/10'
          git pull --rebase origin main
          git push origin HEAD:main
      - name: Verify persisted main commit and SQLite blob
        run: |
          git fetch origin main
          test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
          python - <<'PY'
          import json,pathlib,sqlite3,subprocess
          db='usmle/data/usmle-step1.db'
          state=json.load(open('usmle/state/step2_final_q0001_q1215.json'))
          head_blob=subprocess.check_output(['git','rev-parse','HEAD:'+db],text=True).strip()
          assert head_blob==state['post_authoritative_db_blob']
          con=sqlite3.connect(db)
          assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
          assert con.execute("SELECT COUNT(*) FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]==1215
          assert con.execute("SELECT COUNT(*) FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]==1215
          assert con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]==0
          assert con.execute('SELECT audit_id,item_count FROM step2_finalization WHERE id=1').fetchone()==('STEP2-FINAL-Q0001-Q1215-20260904',1215)
          con.close()
          assert not pathlib.Path(db+'-wal').exists() and not pathlib.Path(db+'-shm').exists()
          print(json.dumps({{'origin_main_matches_head':True,'persisted_db_blob':head_blob,'integrity_check':'ok','items':1215,'reviews':1215,'duplicates':0,'wal_sidecar':False,'shm_sidecar':False}},sort_keys=True))
          PY
'''
    WF.write_text(wf)


def main():
    build_finalizer()
    build_workflow()
    print(f'generated {OUT.relative_to(REPO)} and {WF.relative_to(REPO)}')

if __name__=='__main__':
    main()
