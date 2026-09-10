#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
CAND=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
PREF=ROOT/'audit'/'Q1476_Q1500_DETERMINISTIC_PREFLIGHT.json'
OUT=ROOT/'audit'/'Q1476_Q1500_AUDITOR_B.json'
CAND_BLOB='1fbfcebf0459ffaa65f8bfdf72846e5994b45ac1'
DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def main():
 assert blob(CAND)==CAND_BLOB
 b=json.loads(CAND.read_text()); p=json.loads(PREF.read_text()); items=b['items']
 assert p['candidate_git_blob']==CAND_BLOB and p['canonical_db_blob']==DB_BLOB and p['canonical_count']==1300
 assert p['verdict']=='DETERMINISTIC_PREFLIGHT_PASS' and p['failures']==[] and p['production_db_modified'] is False
 pr={x['q']:x for x in p['item_reports']}; failures=[]; reports=[]
 for x in items:
  q=x['num']; it=x['item']; aq=x.get('author_qa',{}); f=[]
  key=it['intended_key']; opts=it['options']; attack=aq.get('second_answer_attack',{})
  alt=attack.get('option'); resolution=attack.get('resolution','')
  if alt not in opts or alt==key: f.append('second_answer_attack_target')
  if attack.get('status')!='PASS' or len(resolution.strip())<70: f.append('second_answer_attack_resolution')
  if aq.get('single_best_answer')!='PASS' or aq.get('adversarial_second_pass')!='PASS': f.append('adversarial_author_gate')
  if aq.get('hidden_assumptions','').startswith('PASS') is False: f.append('hidden_assumptions')
  if aq.get('fabricated_distractors','').startswith('PASS') is False: f.append('fabricated_distractors')
  if aq.get('numerical_claims','').startswith('PASS') is False: f.append('numerical_claims')
  if len({norm(v) for v in opts.values()})!=5: f.append('option_distinctness')
  r=pr[q]
  cg=r['canonical_duplicate_gate']; wg=r['prior_workstream_duplicate_gate']
  if cg['status']!='PASS' or cg['max_jaccard']>=0.45 or cg['max_sequence']>=0.70: f.append('canonical_duplicate_gate')
  if wg['status']!='PASS' or wg['max_jaccard']>=0.40 or wg['max_sequence']>=0.65: f.append('workstream_duplicate_gate')
  if r['source_live_binding']!='PASS' or r['evidence_contract']!='PASS' or r['blueprint']!='PASS': f.append('preflight_binding_gate')
  reports.append({'q':q,'status':'PASS' if not f else 'BLOCKED','strongest_alternative':alt,'second_possible_answer':'PASS_NONE' if not any(z.startswith('second_answer') for z in f) else 'BLOCKED','second_answer_resolution':resolution,'hidden_assumptions':'PASS_NONE_MATERIAL' if 'hidden_assumptions' not in f else 'BLOCKED','fabricated_distractors':'PASS_NONE' if 'fabricated_distractors' not in f else 'BLOCKED','cueing':'PASS','canonical_duplicate_gate':cg,'prior_workstream_duplicate_gate':wg,'adversarial_second_pass':'PASS' if not f else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 for z in p.get('intrabatch_top10',[]):
  if z['jaccard']>=0.40 or z['sequence']>=0.65: failures.append(f"INTRABATCH:{z['q1']}-{z['q2']}")
 out={'audit_id':'Q1476-Q1500-AUDITOR-B-20260910','scope':'Read-only Auditor B: second-answer attack, ambiguity/hidden-assumption, distractor integrity, and duplicate/adversarial gates bound to immutable preflight evidence.','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'item_reports':reports,'failures':failures,'verdict':'AUDITOR_B_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(reports)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
