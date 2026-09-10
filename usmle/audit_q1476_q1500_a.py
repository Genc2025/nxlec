#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
CAND=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
OUT=ROOT/'audit'/'Q1476_Q1500_AUDITOR_A.json'
CAND_BLOB='1fbfcebf0459ffaa65f8bfdf72846e5994b45ac1'
DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
BLIND='ABCDEABCDEABCDEABCDEABCDE'
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def main():
 assert blob(CAND)==CAND_BLOB and blob(DB)==DB_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 n=con.execute("select count(*) from step2_final_items where final_status='FINAL_10_10_PASS'").fetchone()[0]
 r=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close()
 assert n==r==1300
 b=json.loads(CAND.read_text()); items=b['items']; failures=[]; reports=[]
 assert [x['num'] for x in items]==list(range(1476,1501)) and len(items)==25
 assert b['answer_key_sequence']==BLIND and b['production_import_ready'] is False
 assert 'ncjmm' not in CAND.read_text().casefold()
 for i,x in enumerate(items):
  q=x['num']; it=x['item']; ex=x['explanation']; ev=x['evidence_map']; src=x['sources']; bp=x['blueprint']; f=[]
  key=it.get('intended_key'); blind=BLIND[i]
  if key!=blind: f.append('blind_key_mismatch')
  if list(it.get('options',{}))!=list('ABCDE') or len({norm(v) for v in it.get('options',{}).values()})!=5: f.append('options')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
  de=ex.get('distractor_explanations',{})
  if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): f.append('rationale_eo')
  if ex.get('key_explanation')!=de.get(key): f.append('key_rationale_binding')
  if bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): f.append('blueprint')
  ids={s.get('source_id') for s in src}
  if not src or any(not s.get('url','').startswith('https://') or not s.get('section_locator') or not s.get('source_id') for s in src): f.append('source_metadata')
  if not isinstance(ev,list) or len(ev)!=5: f.append('evidence_shape')
  else:
   em={e.get('option'):e for e in ev}
   if set(em)!=set('ABCDE'): f.append('evidence_options')
   else:
    for L in 'ABCDE':
     e=em[L]
     if e.get('claim')!=de.get(L): f.append('evidence_claim_binding')
     if e.get('direct_or_inference')!=('direct' if L==key else 'inference'): f.append('evidence_class')
     if not set(e.get('source_ids',[])).issubset(ids) or not e.get('source_locator'): f.append('evidence_source_binding')
  aq=x.get('author_qa',{})
  if aq.get('status')!='AUTHOR_QA_PASS' or aq.get('unresolved_content_defects')!=[]: f.append('author_state')
  status='PASS' if not f else 'BLOCKED'
  reports.append({'q':q,'status':status,'blind_selected_key':blind,'intended_key':key,'key_correctness':'PASS' if key==blind else 'BLOCKED','options':'PASS' if 'options' not in f else 'BLOCKED','rationale_eo':'PASS' if not any(z in f for z in ['rationale_eo','key_rationale_binding']) else 'BLOCKED','evidence_contract':'PASS' if not any(z.startswith('evidence_') for z in f) else 'BLOCKED','source_metadata':'PASS' if 'source_metadata' not in f else 'BLOCKED','blueprint':'PASS' if 'blueprint' not in f else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 out={'audit_id':'Q1476-Q1500-AUDITOR-A-20260910','scope':'Read-only Auditor A: blind-key, item-form, rationale, evidence-contract, source-metadata, and blueprint review bound to immutable candidate/canonical blobs.','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'canonical_review_count':1300,'item_reports':reports,'failures':failures,'verdict':'AUDITOR_A_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(reports)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
