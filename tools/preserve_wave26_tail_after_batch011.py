#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'NCLEX_COMMERCIAL_MASTER_CURRENT.db'
PATCHES=[ROOT/'data/manual_option_balance_wave26a_0532_0556.json',ROOT/'data/manual_option_balance_wave26b_0557_0581.json']
MANIFEST=ROOT/'data/manual_final_qa_wave26_0532_0581.json'
IDS=[f'V2-Q{i:04d}' for i in range(551,582)]
MAX_RATIO=1.15
MAX_DEV=0.10
DIMS=['source_verified','blueprint_verified','question_quality_verified','correct_answer_verified','distractors_verified','explanation_verified','currentness_verified','independent_qa_passed','no_unresolved_conflict']
def metrics(options,key):
    lengths={k:len(str(options[k]).strip()) for k in 'ABCD'}
    mn=min(lengths.values()); mx=max(lengths.values()); ratio=mx/max(mn,1)
    dm=sum(lengths[k] for k in 'ABCD' if k!=key)/3
    dev=abs(lengths[key]-dm)/max(dm,1)
    order=sorted('ABCD',key=lambda k:(lengths[k],k))
    return {'lengths':lengths,'min_chars':mn,'max_chars':mx,'max_min_ratio':round(ratio,4),'correct_option':key,'correct_length_rank':order.index(key)+1,'correct_is_extreme':int(lengths[key] in (mn,mx)),'correct_vs_distractor_mean_deviation':round(dev,4),'strict_pass':ratio<=MAX_RATIO and dev<=MAX_DEV}
def main():
    patch=[]
    for p in PATCHES:
        doc=json.loads(p.read_text(encoding='utf-8')); patch.extend(doc.get('items',[]))
    patch={x['question_uid']:x for x in patch if x.get('question_uid') in IDS}
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    mitems={x['question_uid']:x for x in manifest.get('items',[]) if x.get('question_uid') in IDS}
    if set(patch)!=set(IDS) or set(mitems)!=set(IDS): raise SystemExit('Wave26 tail preservation scope mismatch')
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; now=datetime.now(timezone.utc).isoformat(); failures=[]
    for uid in IDS:
        mi=mitems[uid]
        if mi.get('manual_disposition')!='PASS' or mi.get('all_11_dimensions') is not True:
            failures.append(f'{uid}: prior Wave26 manual semantic evidence not PASS'); continue
        q=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if not q or not str(q['clinical_qa_status']).startswith('SOURCE_VERIFIED_2026_WAVE26'):
            failures.append(f'{uid}: current row is not preserved Wave26 source-verified tail'); continue
        data=json.loads(q['item_data_json']); ans=json.loads(q['correct_answer_json']); key=ans['correct_option']; options=patch[uid].get('options')
        if not isinstance(options,dict) or set(options)!=set('ABCD') or key not in options or len({str(options[k]).strip().casefold() for k in 'ABCD'})!=4:
            failures.append(f'{uid}: invalid tail option patch'); continue
        mt=metrics(options,key)
        if not mt['strict_pass']:
            failures.append(f"{uid}: tail option QC failed ratio={mt['max_min_ratio']} dev={mt['correct_vs_distractor_mean_deviation']}"); continue
        data['options']=options
        flags=json.loads(q['editorial_flags_json'] or '[]')
        for f in ('MANUAL_OPTION_CUE_REVIEW','STRICT_OPTION_LENGTH_QC_PASS'):
            if f not in flags: flags.append(f)
        con.execute('UPDATE questions SET item_data_json=?,editorial_flags_json=? WHERE question_uid=?',(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')),json.dumps(flags,ensure_ascii=False,sort_keys=True,separators=(',',':')),uid))
        con.execute('INSERT OR REPLACE INTO option_length_qc(question_uid,lengths_json,min_chars,max_chars,max_min_ratio,correct_option,correct_length_rank,correct_is_extreme,qc_status,qc_note) VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,json.dumps(mt['lengths'],sort_keys=True),mt['min_chars'],mt['max_chars'],mt['max_min_ratio'],key,mt['correct_length_rank'],mt['correct_is_extreme'],'PASS','Preserved prior Wave26 manual option/cue review for non-overlapping Q0551-Q0581 tail after Batch011; quantitative metrics are enforcement only.'))
        con.execute('INSERT OR REPLACE INTO question_final_gate(question_uid,audit_date,auditor,source_locator,source_version,source_verified,blueprint_verified,question_quality_verified,correct_answer_verified,distractors_verified,explanation_verified,currentness_verified,independent_qa_passed,no_unresolved_conflict,option_length_metrics_json,rejection_reason,final_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid,now,manifest.get('reviewer','OpenAI Wave26 manual review'),q['source_detail'],f"{q['clinical_qa_status']} | prior Wave26 manual source/currentness QA preserved after Batch011",1,1,1,1,1,1,1,1,1,json.dumps(mt,sort_keys=True),None,'FINAL_QA_PASS'))
    if failures:
        con.rollback(); raise SystemExit('\n'.join(failures))
    count=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0551' AND 'V2-Q0581' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    qc=con.execute("SELECT COUNT(*) FROM option_length_qc WHERE question_uid BETWEEN 'V2-Q0551' AND 'V2-Q0581' AND qc_status='PASS'").fetchone()[0]
    if (count,qc)!=(31,31): con.rollback(); raise SystemExit(f'Wave26 tail preservation count mismatch final={count} qc={qc}')
    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES('wave26_tail_q0551_q0581_preserved_after_batch011','PASS_31_OF_31_PRIOR_MANUAL_EVIDENCE_REAPPLIED_TECHNICALLY')")
    con.commit(); con.close(); print('WAVE26_TAIL_PRESERVED_AFTER_BATCH011 final=31/31 qc=31/31 semantic_decisions=prior_manual_not_script')
if __name__=='__main__': main()
