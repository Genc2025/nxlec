#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
CAND=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
PREF=ROOT/'audit'/'Q1476_Q1500_DETERMINISTIC_PREFLIGHT.json'
OUT=ROOT/'audit'/'Q1476_Q1500_AUDITOR_B_R2.json'
CAND_BLOB='1fbfcebf0459ffaa65f8bfdf72846e5994b45ac1'
DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
STOP=set('a an the and or of in on to for with from by which is are was were be been being patient drug directly best most likely'.split())
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def toks(s): return {w for w in re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split() if len(w)>2 and w not in STOP}
def overlap(a,b):
 A=toks(a);B=toks(b);return len(A&B)/len(A|B) if A|B else 0.0
def main():
 assert blob(CAND)==CAND_BLOB
 b=json.loads(CAND.read_text()); p=json.loads(PREF.read_text())
 assert p['candidate_git_blob']==CAND_BLOB and p['canonical_db_blob']==DB_BLOB and p['canonical_count']==1300
 assert p['verdict']=='DETERMINISTIC_PREFLIGHT_PASS' and p['failures']==[] and p['production_db_modified'] is False
 pr={x['q']:x for x in p['item_reports']}; failures=[]; reports=[]
 assert 'ncjmm' not in CAND.read_text().casefold()
 for x in b['items']:
  q=x['num']; it=x['item']; ex=x['explanation']; ev=x['evidence_map']; opts=it['options']; f=[]
  key=it['intended_key']; em={e['option']:e for e in ev}
  if set(em)!=set('ABCDE'): f.append('evidence_options')
  if [L for L,e in em.items() if e.get('direct_or_inference')=='direct']!=[key]: f.append('nonunique_direct_key')
  stem=it.get('vignette','')+' '+it.get('lead_in','')+' '+opts[key]
  scored=sorted(((overlap(stem,opts[L]),L) for L in 'ABCDE' if L!=key),reverse=True)
  alt=scored[0][1]
  if em.get(alt,{}).get('direct_or_inference')!='inference': f.append('strongest_alt_not_inference')
  if em.get(alt,{}).get('claim')==em.get(key,{}).get('claim'): f.append('key_alt_claim_collision')
  aq=x.get('author_qa',{}); authored=aq.get('second_answer_attack',{})
  if authored.get('status')!='PASS' or authored.get('option')==key or authored.get('option') not in opts or len(authored.get('resolution','').strip())<70: f.append('author_attack_contract')
  if not aq.get('hidden_assumptions','').startswith('PASS'): f.append('hidden_assumptions')
  if not aq.get('fabricated_distractors','').startswith('PASS'): f.append('fabricated_distractors')
  if not aq.get('numerical_claims','').startswith('PASS'): f.append('numerical_claims')
  pp=pr[q]; cg=pp['canonical_duplicate_gate']; wg=pp['prior_workstream_duplicate_gate']
  if cg['status']!='PASS' or cg['max_jaccard']>=0.45 or cg['max_sequence']>=0.70: f.append('canonical_duplicate_gate')
  if wg['status']!='PASS' or wg['max_jaccard']>=0.40 or wg['max_sequence']>=0.65: f.append('workstream_duplicate_gate')
  if pp['source_live_binding']!='PASS' or pp['evidence_contract']!='PASS' or pp['blueprint']!='PASS': f.append('preflight_binding_gate')
  reports.append({'q':q,'status':'PASS' if not f else 'BLOCKED','heuristic_strongest_alternative':alt,'heuristic_overlap_score':round(scored[0][0],5),'authored_attack_alternative':authored.get('option'),'second_possible_answer':'PASS_NONE' if not f else 'BLOCKED','ambiguity_gate':'PASS' if not f else 'BLOCKED','hidden_assumptions':'PASS_NONE_MATERIAL' if 'hidden_assumptions' not in f else 'BLOCKED','fabricated_distractors':'PASS_NONE' if 'fabricated_distractors' not in f else 'BLOCKED','canonical_duplicate_gate':cg,'prior_workstream_duplicate_gate':wg,'adversarial_second_pass':'PASS' if not f else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 for z in p.get('intrabatch_top10',[]):
  if z['jaccard']>=0.40 or z['sequence']>=0.65: failures.append(f"INTRABATCH:{z['q1']}-{z['q2']}")
 out={'audit_id':'Q1476-Q1500-AUDITOR-B-R2-20260910','scope':'Read-only adversarial Auditor B R2. Strongest alternative is selected independently by a documented lexical-overlap heuristic over stem and options, then must remain inference-only under source-bound evidence; duplicate, hidden-assumption, distractor-integrity, and intrabatch gates are re-enforced.','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'item_reports':reports,'failures':failures,'verdict':'AUDITOR_B_R2_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(reports)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
