#!/usr/bin/env python3
from __future__ import annotations
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
CAND=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
PREF=ROOT/'audit'/'Q1476_Q1500_DETERMINISTIC_PREFLIGHT.json'
OUT=ROOT/'audit'/'Q1476_Q1500_AUDITOR_A_R2.json'
CAND_BLOB='1fbfcebf0459ffaa65f8bfdf72846e5994b45ac1'
DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def main():
 assert blob(CAND)==CAND_BLOB and blob(DB)==DB_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 n=con.execute("select count(*) from step2_final_items where final_status='FINAL_10_10_PASS'").fetchone()[0]
 r=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close()
 assert n==r==1300
 b=json.loads(CAND.read_text()); p=json.loads(PREF.read_text())
 assert p['candidate_git_blob']==CAND_BLOB and p['canonical_db_blob']==DB_BLOB
 assert p['verdict']=='DETERMINISTIC_PREFLIGHT_PASS' and p['failures']==[]
 assert p['live_source_reverification_performed'] is True
 assert [x['num'] for x in b['items']]==list(range(1476,1501)) and len(b['items'])==25
 assert b['production_import_ready'] is False and 'ncjmm' not in CAND.read_text().casefold()
 pr={x['q']:x for x in p['item_reports']}; sr={}
 for s in p['source_reports']: sr.setdefault(s['q'],[]).append(s)
 failures=[]; reports=[]
 for x in b['items']:
  q=x['num']; it=x['item']; ex=x['explanation']; ev=x['evidence_map']; src=x['sources']; f=[]
  if list(it.get('options',{}))!=list('ABCDE'): f.append('option_labels')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
  em={e.get('option'):e for e in ev} if isinstance(ev,list) else {}
  direct=[L for L,e in em.items() if e.get('direct_or_inference')=='direct']
  derived=direct[0] if len(direct)==1 else None
  if len(direct)!=1: f.append('unique_direct_evidence_key')
  if derived!=it.get('intended_key'): f.append('evidence_derived_key_mismatch')
  if set(em)!=set('ABCDE'): f.append('evidence_options')
  ids={s.get('source_id') for s in src}
  de=ex.get('distractor_explanations',{})
  if set(de)!=set('ABCDE') or not ex.get('educational_objective') or not ex.get('key_explanation'): f.append('rationale_eo')
  for L,e in em.items():
   if e.get('claim')!=de.get(L): f.append('claim_rationale_binding')
   if not set(e.get('source_ids',[])).issubset(ids) or not e.get('source_locator'): f.append('source_evidence_binding')
  pp=pr[q]
  if pp['status']!='PASS' or pp['source_live_binding']!='PASS' or pp['evidence_contract']!='PASS' or pp['blueprint']!='PASS': f.append('preflight_item_binding')
  qs=sr.get(q,[])
  if not qs or any(s.get('status')!='PASS' for s in qs): f.append('live_source_report')
  if ex.get('key_explanation')!=de.get(derived): f.append('derived_key_rationale_binding')
  status='PASS' if not f else 'BLOCKED'
  reports.append({'q':q,'status':status,'derived_key_from_unique_direct_evidence':derived,'intended_key':it.get('intended_key'),'key_correctness':'PASS' if derived==it.get('intended_key') else 'BLOCKED','derivation_method':'UNIQUE_DIRECT_EVIDENCE_OPTION_AFTER_LIVE_SOURCE_BINDING','source_live_binding':'PASS' if 'live_source_report' not in f else 'BLOCKED','evidence_contract':'PASS' if not any(z in f for z in ['unique_direct_evidence_key','evidence_options','claim_rationale_binding','source_evidence_binding','derived_key_rationale_binding']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 out={'audit_id':'Q1476-Q1500-AUDITOR-A-R2-20260910','scope':'Read-only evidence-derived Auditor A R2. No hard-coded answer sequence is used. The candidate key is re-derived as the unique option whose evidence classification is direct, and that evidence must already have passed live source binding in immutable deterministic preflight. This is an independent evidence-contract re-derivation, not a claim of unseen-key human blinding.','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'canonical_review_count':1300,'hardcoded_answer_sequence_used':False,'strict_unseen_key_blinding_claimed':False,'item_reports':reports,'failures':failures,'verdict':'AUDITOR_A_R2_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(reports)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
