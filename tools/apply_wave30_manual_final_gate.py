#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'NCLEX_COMMERCIAL_MASTER_CURRENT.db'; MAN=ROOT/'data/manual_final_qa_wave30_0732_0781.json'; REP=ROOT/'FINAL_QA_WAVE30_Q0732_Q0781_MANUAL_10OF10.md'
EXPECTED=[f'V2-Q{i:04d}' for i in range(732,782)]
DIMS=['source_verified','blueprint_verified','question_quality_verified','correct_answer_verified','distractors_verified','explanation_verified','currentness_verified','independent_qa_passed','no_unresolved_conflict']
FLAGS={'MANUAL_ITEM_BY_ITEM_AUDIT','SOURCE_CURRENTNESS_CHECKED','KEY_VERIFIED','DISTRACTORS_REVIEWED','RATIONALE_VERIFIED','AMBIGUITY_REVIEWED','SECOND_PASS_MANUAL_QA'}
def fail(x): raise SystemExit(x)
def main():
 if not DB.exists() or not MAN.exists(): fail('Wave30 DB/manifest missing')
 m=json.loads(MAN.read_text(encoding='utf-8')); items=m.get('items',[])
 if [x.get('question_uid') for x in items]!=EXPECTED or len(items)!=50: fail('Wave30 manifest scope mismatch')
 for x in items:
  u=x['question_uid']
  if x.get('manual_disposition')!='PASS' or x.get('all_11_dimensions') is not True or x.get('second_pass_verified') is not True: fail(f'Manual PASS evidence missing for {u}')
  if not str(x.get('source_locator') or '').strip() or not str(x.get('source_url') or '').startswith('https://'): fail(f'Source evidence missing for {u}')
 con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; now=datetime.now(timezone.utc).isoformat(); ratios=[]; devs=[]
 for x in items:
  u=x['question_uid']; q=con.execute('SELECT * FROM questions WHERE question_uid=?',(u,)).fetchone()
  if not q or q['clinical_qa_status']!='SOURCE_VERIFIED_2026_WAVE30_ITEM_BY_ITEM': fail(f'Persisted Wave30 status missing for {u}')
  if not FLAGS.issubset(set(json.loads(q['editorial_flags_json'] or '[]'))): fail(f'Manual flags missing for {u}')
  if q['source_detail']!=x['source_locator'] or q['source_url']!=x['source_url']: fail(f'Source provenance mismatch for {u}')
  d=json.loads(q['item_data_json']); a=json.loads(q['correct_answer_json']); o=d.get('options',{}); k=a.get('correct_option')
  if set(o)!={'A','B','C','D'} or k not in o or len({str(o[z]).strip().casefold() for z in 'ABCD'})!=4: fail(f'Option/key structure invalid for {u}')
  lengths={z:len(str(o[z]).strip()) for z in 'ABCD'}; ratio=max(lengths.values())/max(min(lengths.values()),1); dm=sum(v for z,v in lengths.items() if z!=k)/3; dev=abs(lengths[k]-dm)/max(dm,1)
  ratios.append(ratio); devs.append(dev)
  if ratio>1.15+1e-9 or dev>.10+1e-9: fail(f'Option gate failed for {u}: ratio={ratio:.4f} dev={dev:.4f}')
  qc=con.execute('SELECT * FROM option_length_qc WHERE question_uid=?',(u,)).fetchone()
  if not qc or qc['qc_status']!='PASS': fail(f'Persisted option QC missing for {u}')
  cols=','.join(DIMS); ph=','.join('?' for _ in DIMS)
  metrics=json.dumps({'characters':lengths,'max_min_ratio':round(ratio,4),'correct_option':k,'correct_vs_distractor_mean_deviation':round(dev,4),'manual_cue_review':True,'second_pass_verified':True},sort_keys=True)
  con.execute(f'INSERT OR REPLACE INTO question_final_gate(question_uid,audit_date,auditor,source_locator,source_version,{cols},option_length_metrics_json,rejection_reason,final_status) VALUES(?,?,?,?,?,{ph},?,?,?)',(u,now,m['reviewer'],q['source_detail'],q['clinical_qa_status']+' | manually checked 2026-08-14',*([1]*len(DIMS)),metrics,None,'FINAL_QA_PASS'))
 passed=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0732' AND 'V2-Q0781' AND final_status='FINAL_QA_PASS'").fetchone()[0]
 if passed!=50: con.rollback(); fail(f'Wave30 final gate passed={passed}/50')
 con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",('wave30_q0732_q0781_manual_final_gate','PASS_50_OF_50_2026_08_14_ITEM_BY_ITEM_STRICT_OPTIONS')); con.commit(); con.close()
 REP.write_text('\n'.join(['# Manual Final QA Gate — Q0732–Q0781','','- Scope: **50/50** items','- Review method: **manual item-by-item clinical/source QA + separate second pass**','- Final-gate result: **PASS 50/50**','- All 11 required dimensions: **PASS 50/50**','- Source locator/version: **PASS 50/50**','- Option-length/cue QC: **PASS 50/50**',f'- Maximum option max/min character ratio: **{max(ratios):.4f}** (gate ≤ 1.15)',f'- Maximum correct-option deviation from distractor mean: **{max(devs):.4f}** (gate ≤ 0.10)','','The full-bank commercial release gate remains closed until the remaining bank completes the same process.','']),encoding='utf-8')
 print(f'Wave30 manual final gate: PASS 50/50; max_ratio={max(ratios):.4f}; max_key_dev={max(devs):.4f}')
if __name__=='__main__': main()
