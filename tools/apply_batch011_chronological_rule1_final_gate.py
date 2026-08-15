#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'NCLEX_COMMERCIAL_MASTER_CURRENT.db'
EVIDENCE=ROOT/'data/rule1_batch011_chronological_reaudit_evidence_q0501_q0550.json'
OVERRIDE=ROOT/'data/clinical_overrides_zzz_rule1_batch011_chronological_q0501_q0550_20260815.json'
REPORT=ROOT/'FINAL_QA_BATCH011_Q0501_Q0550_RULE1_11OF11.md'
IDS=[f'V2-Q{i:04d}' for i in range(501,551)]
STATUS='SOURCE_VERIFIED_2026_RULE1_BATCH011_CHRONOLOGICAL_MANUAL'
GATE='CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA'
CRITERIA=['source_authority_verified','source_currentness_verified','exact_locator_verified','stem_factual_accuracy_verified','correct_answer_verified','rationale_verified','distractors_verified','ambiguity_cue_second_answer_qc_verified','blueprint_topic_difficulty_verified','no_unresolved_conflicts','independent_second_pass_qa']
FLAGS={'RULE1_BATCH011_MANUAL_ITEM_BY_ITEM_REAUDIT','LEGACY_STATUS_NOT_USED_AS_EVIDENCE','SEMANTIC_DECISIONS_NOT_BY_SCRIPT','STATIC_MANUAL_AUTHORED_FINAL_OPTIONS','SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED','MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS','INDEPENDENT_SECOND_PASS_QA_PASS','OPTION_LENGTH_METRICS_MEASUREMENT_ONLY'}
def measure(options,key):
    ls={k:len(str(options[k]).strip()) for k in 'ABCD'}
    dm=sum(ls[k] for k in 'ABCD' if k!=key)/3
    return {'characters':ls,'max_min_ratio':round(max(ls.values())/max(min(ls.values()),1),4),'correct_option':key,'correct_deviation_from_distractor_mean':round(abs(ls[key]-dm)/max(dm,1),4),'use':'MEASUREMENT_ONLY_NOT_SEMANTIC_GATE'}
def main():
    doc=json.loads(EVIDENCE.read_text(encoding='utf-8')); odoc=json.loads(OVERRIDE.read_text(encoding='utf-8'))
    if doc.get('standard')!='RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT' or doc.get('batch')!='Q0501-Q0550' or doc.get('legacy_status_evidence') is not False or doc.get('semantic_decisions_by_script') is not False or doc.get('criteria_names')!=CRITERIA:
        raise SystemExit('Invalid Batch 011 manual Rule 1 evidence header')
    if odoc.get('semantic_decisions_by_script') is not False:
        raise SystemExit('Batch 011 override semantic decision provenance invalid')
    ev={x['id']:x for x in doc.get('items',[])}; ov={x['question_uid']:x for x in odoc.get('questions',[])}
    if len(ev)!=50 or set(ev)!=set(IDS) or len(ov)!=50 or set(ov)!=set(IDS):
        raise SystemExit('Batch 011 evidence/override scope mismatch')
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; now=datetime.now(timezone.utc).isoformat()
    con.execute("CREATE TABLE IF NOT EXISTS question_final_gate(question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,auditor TEXT NOT NULL,source_locator TEXT NOT NULL,source_version TEXT NOT NULL,source_verified INTEGER NOT NULL,blueprint_verified INTEGER NOT NULL,question_quality_verified INTEGER NOT NULL,correct_answer_verified INTEGER NOT NULL,distractors_verified INTEGER NOT NULL,explanation_verified INTEGER NOT NULL,currentness_verified INTEGER NOT NULL,independent_qa_passed INTEGER NOT NULL,no_unresolved_conflict INTEGER NOT NULL,option_length_metrics_json TEXT NOT NULL,rejection_reason TEXT,final_status TEXT NOT NULL,FOREIGN KEY(question_uid) REFERENCES questions(question_uid))")
    con.execute("CREATE TABLE IF NOT EXISTS rule1_manual_audit(question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator_version TEXT NOT NULL,finding TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,FOREIGN KEY(question_uid) REFERENCES questions(question_uid))")
    con.execute('DROP TABLE IF EXISTS rule1_batch011_chronological_reaudit_evidence')
    con.execute("CREATE TABLE rule1_batch011_chronological_reaudit_evidence(question_uid TEXT PRIMARY KEY,audit_date TEXT NOT NULL,correct_option TEXT NOT NULL,category_id INTEGER NOT NULL,client_need TEXT NOT NULL,difficulty TEXT NOT NULL,source_authority TEXT NOT NULL,source_url TEXT NOT NULL,source_locator TEXT NOT NULL,source_version TEXT NOT NULL,finding TEXT NOT NULL,ncsbn_first_check_json TEXT NOT NULL,criteria_passed_count INTEGER NOT NULL,second_pass TEXT NOT NULL,final_disposition TEXT NOT NULL,option_metrics_json TEXT NOT NULL,FOREIGN KEY(question_uid) REFERENCES questions(question_uid))")
    failures=[]
    for uid in IDS:
        e=ev[uid]; o=ov[uid]
        if e.get('criteria')!=11 or e.get('criteria_names')!=CRITERIA or e.get('second_pass')!='PASS' or e.get('final')!='FINAL_QA_PASS' or e.get('semantic_decision_origin')!='MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT':
            failures.append(f'{uid}: incomplete manual 11/11/second-pass evidence'); continue
        n=e.get('ncsbn_first_check',{})
        if n.get('required_currentness_and_blueprint_check') is not True or n.get('result')!='PASS' or '2026-04-01' not in n.get('version','') or '2029-03-31' not in n.get('version',''):
            failures.append(f'{uid}: NCSBN currentness/blueprint evidence incomplete'); continue
        if not e.get('source_url','').startswith('https://') or not e.get('source_locator','').strip() or not e.get('source_version','').strip() or not e.get('source_authority','').strip():
            failures.append(f'{uid}: source authority/URL/locator/version incomplete'); continue
        con.execute('UPDATE questions SET category_id=?,client_need=?,difficulty=? WHERE question_uid=?',(e['category_id'],e['client_need'],e['difficulty'],uid))
        q=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if not q: failures.append(f'{uid}: DB row missing'); continue
        try:
            opts=json.loads(q['item_data_json'])['options']; key=json.loads(q['correct_answer_json'])['correct_option']
            eopts=json.loads(o['item_data_json'])['options']; ekey=json.loads(o['correct_answer_json'])['correct_option']
        except Exception as exc:
            failures.append(f'{uid}: invalid JSON {exc}'); continue
        if set(opts)!=set('ABCD') or len({str(v).strip().casefold() for v in opts.values()})!=4:
            failures.append(f'{uid}: invalid/duplicate options'); continue
        if opts!=eopts or key!=ekey or key!=e['key'] or q['stem']!=o['stem'] or q['rationale']!=o['rationale']:
            failures.append(f'{uid}: DB final content does not match manual authored override'); continue
        if (q['category_id'],q['client_need'],q['difficulty'])!=(e['category_id'],e['client_need'],e['difficulty']):
            failures.append(f'{uid}: blueprint/topic/difficulty mismatch'); continue
        if (q['source_name'],q['source_url'])!=(e['source_name'],e['source_url']):
            failures.append(f'{uid}: source name/URL mismatch'); continue
        detail=q['source_detail'] or ''
        if e['source_locator'] not in detail or e['source_version'] not in detail or 'NCSBN first-check' not in detail or '2026-08-15' not in detail:
            failures.append(f'{uid}: locator/version/currentness/NCSBN check not integrated'); continue
        if q['clinical_qa_status']!=STATUS:
            failures.append(f'{uid}: final Batch 011 status not integrated'); continue
        flags=set(json.loads(q['editorial_flags_json'] or '[]'))
        if not FLAGS.issubset(flags):
            failures.append(f'{uid}: final manual Rule 1 flags incomplete'); continue
        m=measure(opts,key); lv=f"{e['source_locator']} {e['source_version']}"
        con.execute('INSERT OR REPLACE INTO rule1_batch011_chronological_reaudit_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid,now,key,e['category_id'],e['client_need'],e['difficulty'],e['source_authority'],e['source_url'],e['source_locator'],e['source_version'],e['finding'],json.dumps(n,sort_keys=True),11,'PASS','FINAL_QA_PASS',json.dumps(m,sort_keys=True)))
        con.execute('INSERT OR REPLACE INTO rule1_manual_audit(question_uid,audit_date,correct_option,source_authority,source_url,source_locator_version,finding,criteria_passed_count,second_pass,final_disposition) VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,now,key,e['source_authority'],e['source_url'],lv,e['finding'],11,'PASS','FINAL_QA_PASS'))
        con.execute('INSERT OR REPLACE INTO question_final_gate(question_uid,audit_date,auditor,source_locator,source_version,source_verified,blueprint_verified,question_quality_verified,correct_answer_verified,distractors_verified,explanation_verified,currentness_verified,independent_qa_passed,no_unresolved_conflict,option_length_metrics_json,rejection_reason,final_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid,now,'OpenAI Rule 1 Batch 011 manual item-by-item audit; independent second pass',e['source_locator'],e['source_version'],1,1,1,1,1,1,1,1,1,json.dumps(m,sort_keys=True),None,'FINAL_QA_PASS'))
    if failures:
        con.rollback(); raise SystemExit('\n'.join(failures))
    con.execute("INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",('batch011_chronological_q0501_q0550_rule1_final_gate','PASS_50_OF_50_MANUAL_ITEM_BY_ITEM_SECOND_PASS_11_OF_11_NCSBN_2026_08_15'))
    integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
    total=con.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    ready=con.execute('SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1').fetchone()[0]
    gate=con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()
    final=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0501' AND 'V2-Q0550' AND final_status='FINAL_QA_PASS'").fetchone()[0]
    manual=con.execute("SELECT COUNT(*) FROM rule1_manual_audit WHERE question_uid BETWEEN 'V2-Q0501' AND 'V2-Q0550' AND criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    evidence=con.execute("SELECT COUNT(*) FROM rule1_batch011_chronological_reaudit_evidence WHERE criteria_passed_count=11 AND second_pass='PASS' AND final_disposition='FINAL_QA_PASS'").fetchone()[0]
    status=con.execute("SELECT COUNT(*) FROM questions WHERE question_uid BETWEEN 'V2-Q0501' AND 'V2-Q0550' AND clinical_qa_status=?",(STATUS,)).fetchone()[0]
    bad=con.execute("SELECT COUNT(*) FROM question_final_gate WHERE question_uid BETWEEN 'V2-Q0501' AND 'V2-Q0550' AND (source_verified<>1 OR blueprint_verified<>1 OR question_quality_verified<>1 OR correct_answer_verified<>1 OR distractors_verified<>1 OR explanation_verified<>1 OR currentness_verified<>1 OR independent_qa_passed<>1 OR no_unresolved_conflict<>1)").fetchone()[0]
    if integrity!='ok' or total!=3525 or ready!=0 or not gate or gate[0]!=GATE or (final,manual,evidence,status,bad)!=(50,50,50,50,0):
        con.rollback(); raise SystemExit(f'Batch011 integrated gate failed integrity={integrity} total={total} ready={ready} final={final} manual={manual} evidence={evidence} status={status} bad={bad} gate={gate}')
    con.commit(); con.close()
    REPORT.write_text('\n'.join([
        '# Rule 1 Chronological Batch 011 — Q0501-Q0550','',
        '- Scope: **50/50**','- Legacy PASS/status used as clinical quality evidence: **NO**','- Semantic/clinical decisions made by scripts: **NO**',
        '- Fresh item-by-item review of stem + all four options + key + rationale: **50/50**','- Rule 1 criteria: **11/11 for 50/50**',
        '- Correct answers directly source-verified: **50/50**','- Source authority + URL + exact locator + version/currentness: **50/50**',
        '- NCSBN 2026 NCLEX-RN Test Plan currentness/blueprint check: **50/50**','- Distractor plausibility / ambiguity / cueing / second-answer QC: **50/50**',
        '- Real clinical/editorial/source/blueprint corrections integrated where required: **YES**','- Independent second pass on final corrected state: **50/50**',
        '- Unresolved conflicts: **0**','- Option-length metrics: **measurement only; not a semantic PASS rule**','- SQLite integrity: **ok**',
        '- commercial_release_ready: **0**','- Commercial release gate: **CLOSED** pending full-bank clinical/currentness/source-licensing/release QA','',
        '## Material corrections',
        '- Q0503: blueprint corrected to Safety & Infection Prevention and Control and current CDC tetanus wound prophylaxis retained.',
        '- Q0514: blueprint corrected to Pharmacological and Parenteral Therapies and DEA storage wording narrowed to the exact federal security requirement.',
        '- Q0521: blueprint corrected to Psychosocial Integrity for individualized cultural assessment/culturally responsive care.',
        '- Q0533: blueprint corrected to Pharmacological and Parenteral Therapies; colchicine wording preserves both acute-flare treatment and prophylaxis roles.',
        '- Q0538: prior second-correct-answer defect removed; only one option now integrates phenobarbital level with clinical seizure/adverse-effect assessment.',
        '- Q0539: blueprint corrected to Pharmacological and Parenteral Therapies and source upgraded to current DailyMed version 12 published 2026-02-20.',
        '- Q0542: blueprint corrected to Pharmacological and Parenteral Therapies for prescribed eye-drop administration.',
        '', '## Final disposition','**FINAL_QA_PASS — 50/50 for Batch 011 Q0501-Q0550.**'])+'\n',encoding='utf-8')
    print('BATCH011_MANUAL_FINAL_GATE PASS=50/50 criteria11=50/50 sources=50/50 second_pass=50/50 unresolved=0 bad=0 integrity=ok')
if __name__=='__main__': main()
