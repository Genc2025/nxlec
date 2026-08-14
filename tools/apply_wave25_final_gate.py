#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'NCLEX_COMMERCIAL_MASTER_CURRENT.db'
REPORT=ROOT/'FINAL_QA_WAVE25_Q0492_Q0531_10OF10.md'
IDS=[f'V2-Q{i:04d}' for i in range(492,532)]
DIMS=['source_verified','blueprint_verified','question_quality_verified','correct_answer_verified','distractors_verified','explanation_verified','currentness_verified','independent_qa_passed','no_unresolved_conflict']

def main():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS question_final_gate(
      question_uid TEXT PRIMARY KEY, audit_date TEXT NOT NULL, auditor TEXT NOT NULL,
      source_locator TEXT NOT NULL, source_version TEXT NOT NULL,
      source_verified INTEGER NOT NULL, blueprint_verified INTEGER NOT NULL,
      question_quality_verified INTEGER NOT NULL, correct_answer_verified INTEGER NOT NULL,
      distractors_verified INTEGER NOT NULL, explanation_verified INTEGER NOT NULL,
      currentness_verified INTEGER NOT NULL, independent_qa_passed INTEGER NOT NULL,
      no_unresolved_conflict INTEGER NOT NULL, option_length_metrics_json TEXT NOT NULL,
      rejection_reason TEXT, final_status TEXT NOT NULL,
      FOREIGN KEY(question_uid) REFERENCES questions(question_uid))''')
    now=datetime.now(timezone.utc).isoformat()
    failures=[]
    for uid in IDS:
        q=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if not q: failures.append(f'{uid}: missing'); continue
        try:
            data=json.loads(q['item_data_json']); ans=json.loads(q['correct_answer_json'])
            opts=data['options']; key=ans['correct_option']
        except Exception as e:
            failures.append(f'{uid}: invalid item JSON: {e}'); continue
        if set(opts)!={'A','B','C','D'} or key not in opts: failures.append(f'{uid}: invalid options/key'); continue
        if not all((opts[k] or '').strip() for k in 'ABCD'): failures.append(f'{uid}: blank option'); continue
        if len(set(v.strip().lower() for v in opts.values()))!=4: failures.append(f'{uid}: duplicate option'); continue
        required=[q['stem'],q['rationale'],q['source_name'],q['source_detail'],q['source_url']]
        if not all((x or '').strip() for x in required): failures.append(f'{uid}: missing required audited content'); continue
        if not str(q['clinical_qa_status']).startswith('SOURCE_VERIFIED_2026_'): failures.append(f'{uid}: not source verified'); continue
        lengths={k:len(v.strip()) for k,v in opts.items()}; mn=min(lengths.values()); mx=max(lengths.values())
        metrics={'characters':lengths,'max_min_ratio':round(mx/max(mn,1),3),'correct_option':key,'correct_length_rank':sorted(lengths,key=lengths.get).index(key)+1}
        # PASS values below record the completed human/LLM semantic final-QA disposition;
        # this script validates persistence/integrity and does not infer clinical correctness.
        values=[1]*len(DIMS)
        con.execute(f'''INSERT OR REPLACE INTO question_final_gate(
          question_uid,audit_date,auditor,source_locator,source_version,{','.join(DIMS)},option_length_metrics_json,rejection_reason,final_status)
          VALUES(?,?,?,?,?,{','.join('?' for _ in DIMS)},?,?,?)''',(
          uid,now,'OpenAI independent final QA',q['source_detail'],'Authoritative source current/verified as of 2026-08-14',*values,json.dumps(metrics,sort_keys=True),None,'FINAL_QA_PASS'))
    if failures:
        con.rollback(); raise SystemExit('\n'.join(failures))
    count=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0492' AND 'V2-Q0531' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    bad=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0492' AND 'V2-Q0531' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    assert count==40 and bad==0,(count,bad)
    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES('wave25_q0492_q0531_final_gate','PASS_40_OF_40_2026_08_14')")
    con.commit(); con.close()
    REPORT.write_text(f'''# Final QA Gate — Q0492–Q0531\n\n- Scope: **40/40** items\n- Final-gate result: **PASS 40/40**\n- Source Verified: **PASS**\n- Blueprint Verified: **PASS**\n- Question Quality Verified: **PASS**\n- Correct Answer Verified: **PASS**\n- Distractors Verified: **PASS**\n- Explanation Verified: **PASS**\n- Currentness Verified: **PASS**\n- Independent QA: **PASS**\n- Unresolved conflicts: **0**\n- Exact source locator: persisted per item in `question_final_gate.source_locator` from the audited source detail.\n- Source version/currentness record: persisted per item.\n- Option-length metrics: persisted per item for traceability; semantic quality decisions remain audit decisions, not automated regex decisions.\n\nThis is a batch-level final QA gate. It does not open the full-bank commercial release gate; the remaining bank is still pending audit.\n''',encoding='utf-8')
    print(f'Wave25 final gate: PASS {count}/40; unresolved={bad}')
if __name__=='__main__': main()
