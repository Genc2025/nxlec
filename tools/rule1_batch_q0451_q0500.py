#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sqlite3, subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE=Path('NCLEX_COMMERCIAL_MASTER_CURRENT.db')
CANONICAL=Path('NCLEX_CANONICAL.db')
APPROVED=Path('approved_items')
STAGING=Path('staging_items')
REPORT=Path('RULE1_BATCH_Q0451_Q0500_REPORT.json')
EXPECTED_SOURCE_BLOB='07e335d471ef1b4689406ba41eb98eaa2ca41472'
EXPECTED_CANONICAL_BLOB='9884b027cc2db1f6ed6468eb42e7794b16aeb757'
GATES=['source_authority_verified','currentness_verified','exact_locator_verified','stem_verified','correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified','ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified','independent_qa_passed','no_unresolved_conflict']
REQUIRED_TOP=['question_uid','source_bank','source_table','source_id','mode','category_id','client_need','difficulty','item_type_raw','renderer_type','stem','item_data','correct_answer','rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_source_organization','blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','blueprint_topic','stable_sort_key','source_db_filename','source_db_blob_sha','source_original','correction_summary','audit_status','second_pass_status','audit_date_utc','audit_reviewer','gates','audit_findings']
OPTIONAL_NULL={'case_uid','original_sequence','official_case_slot','slot_variant','specialty','cjmm_skill','scoring_rule'}
JSON_COLS=['item_data_json','correct_answer_json','source_original_json','audit_findings_json']

def sh(*args): return subprocess.check_output(args,text=True).strip()
def cjson(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def psha(p): return hashlib.sha256(cjson(p).encode()).hexdigest()
def fail(m): raise SystemExit(m)

def fingerprint(con):
    rows=con.execute("SELECT * FROM questions WHERE question_uid BETWEEN 'V2-Q0001' AND 'V2-Q0450' ORDER BY question_uid").fetchall()
    packed=[list(r) for r in rows]
    return hashlib.sha256(json.dumps(packed,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),len(rows)

def db_values(p,created):
    return {
      'question_uid':p['question_uid'],'source_bank':p['source_bank'],'source_table':p['source_table'],'source_id':p['source_id'],'mode':p['mode'],'case_uid':p.get('case_uid'),'original_sequence':p.get('original_sequence'),'official_case_slot':p.get('official_case_slot'),'slot_variant':p.get('slot_variant'),'category_id':p['category_id'],'client_need':p['client_need'],'specialty':p.get('specialty'),'difficulty':p['difficulty'],'cjmm_skill':p.get('cjmm_skill'),'item_type_raw':p['item_type_raw'],'renderer_type':p['renderer_type'],'stem':p['stem'],'item_data_json':cjson(p['item_data']),'correct_answer_json':cjson(p['correct_answer']),'rationale':p['rationale'],'scoring_rule':p.get('scoring_rule'),'educational_objective':p['educational_objective'],'source_organization':p['source_organization'],'source_document_title':p['source_document_title'],'source_version_date':p['source_version_date'],'source_accessed_date':p['source_accessed_date'],'source_locator':p['source_locator'],'source_url':p['source_url'],'source_claim_supported':p['source_claim_supported'],'blueprint_source_organization':p['blueprint_source_organization'],'blueprint_document_title':p['blueprint_document_title'],'blueprint_version':p['blueprint_version'],'blueprint_locator':p['blueprint_locator'],'blueprint_url':p['blueprint_url'],'blueprint_topic':p['blueprint_topic'],'stable_sort_key':p['stable_sort_key'],'source_db_filename':p['source_db_filename'],'source_db_blob_sha':p['source_db_blob_sha'],'source_original_json':cjson(p['source_original']),'correction_summary':p['correction_summary'],'audit_status':p['audit_status'],'second_pass_status':p['second_pass_status'],'audit_date_utc':p['audit_date_utc'],'audit_reviewer':p['audit_reviewer'],**{g:int(p['gates'][g]) for g in GATES},'audit_findings_json':cjson(p['audit_findings']),'payload_sha256':psha(p),'created_at_utc':created}

def main():
    uids=[f'V2-Q{i:04d}' for i in range(451,501)]
    expected={f'{u}.json' for u in uids}
    actual={p.name for p in APPROVED.glob('*.json')}
    if actual!=expected: fail(f'approved_items mismatch count={len(actual)} missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
    now=datetime.now(timezone.utc)
    payloads=[]
    for uid in uids:
        try: p=json.loads((APPROVED/f'{uid}.json').read_text())
        except Exception as e: fail(f'Bad JSON {uid}: {e}')
        missing=[k for k in REQUIRED_TOP if k not in p or (p[k] in ('',None) and k not in OPTIONAL_NULL)]
        if missing: fail(f'{uid} missing fields {missing}')
        if p['question_uid']!=uid or p['source_bank']!='v2' or p['source_table']!='questions' or p['source_id']!=int(uid[-4:]): fail(f'{uid} source identity mismatch')
        if p['audit_status']!='FINAL_QA_PASS' or p['second_pass_status']!='PASS': fail(f'{uid} final status invalid')
        bad=[g for g in GATES if p['gates'].get(g)!=1]
        if bad: fail(f'{uid} failed gates {bad}')
        if p['source_db_filename']!=SOURCE.name or p['source_db_blob_sha']!=EXPECTED_SOURCE_BLOB: fail(f'{uid} source metadata mismatch')
        try: t=datetime.fromisoformat(p['audit_date_utc'].replace('Z','+00:00'))
        except Exception as e: fail(f'{uid} bad audit timestamp {e}')
        if t.tzinfo is None or t>now: fail(f'{uid} future/naive audit timestamp {p["audit_date_utc"]}')
        if p['source_accessed_date']!='2026-08-16': fail(f'{uid} source_accessed_date mismatch')
        if set(p['item_data'].get('options',{}))!={'A','B','C','D'}: fail(f'{uid} options not A-D')
        if p['correct_answer'].get('correct_option') not in {'A','B','C','D'}: fail(f'{uid} invalid key')
        payloads.append(p)
    if len(payloads)!=50 or len({p['question_uid'] for p in payloads})!=50: fail('payload count/uniqueness failure')

    head_source=sh('git','rev-parse',f'HEAD:{SOURCE}')
    head_can=sh('git','rev-parse',f'HEAD:{CANONICAL}')
    if head_source!=EXPECTED_SOURCE_BLOB or sh('git','hash-object',str(SOURCE))!=EXPECTED_SOURCE_BLOB: fail('source blob moved')
    if head_can!=EXPECTED_CANONICAL_BLOB or sh('git','hash-object',str(CANONICAL))!=EXPECTED_CANONICAL_BLOB: fail(f'canonical base moved HEAD={head_can}')

    src=sqlite3.connect(SOURCE); src.row_factory=sqlite3.Row
    con=sqlite3.connect(CANONICAL); con.row_factory=sqlite3.Row; con.execute('PRAGMA foreign_keys=ON')
    if src.execute('PRAGMA integrity_check').fetchone()[0]!='ok': fail('source integrity failed')
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok': fail('canonical pre integrity failed')
    pre=con.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    dup=con.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)').fetchone()[0]
    if pre!=450 or dup: fail(f'canonical precondition count={pre} dup={dup}')
    if con.execute("SELECT COUNT(*) FROM questions WHERE question_uid BETWEEN 'V2-Q0451' AND 'V2-Q0500'").fetchone()[0]: fail('batch UIDs already present')
    fp_before,fp_count=fingerprint(con)
    if fp_count!=450: fail(f'protected count {fp_count}')

    snapshot_exact=0
    for p in payloads:
        uid=p['question_uid']; row=src.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if row is None: fail(f'source missing {uid}')
        if row['source_bank']!=p['source_bank'] or row['source_id']!=p['source_id'] or row['source_table']!=p['source_table'] or row['stable_sort_key']!=p['stable_sort_key']: fail(f'source identity moved {uid}')
        o=p['source_original']
        exact={'stem':row['stem']==o['stem'],'options':json.loads(row['item_data_json'])['options']==o['options'],'correct_option':json.loads(row['correct_answer_json'])['correct_option']==o['correct_option'],'rationale':row['rationale']==o['rationale'],'source_url':row['source_url']==o['source_url'],'source_detail':row['source_detail']==o['source_detail'],'difficulty':row['difficulty']==o['difficulty']}
        if not all(exact.values()): fail(f'source_original mismatch {uid}: {exact}')
        if p['source_id']>=452:
            sp=STAGING/f'{uid}.json'
            if not sp.exists(): fail(f'missing staging snapshot {uid}')
            snap=json.loads(sp.read_text())
            if snap.get('source_blob_expected')!=EXPECTED_SOURCE_BLOB or snap.get('canonical_blob_expected')!=EXPECTED_CANONICAL_BLOB: fail(f'snapshot blob metadata mismatch {uid}')
            if snap.get('source_row')!=dict(row): fail(f'staging source row mismatch {uid}')
        snapshot_exact+=1
    if snapshot_exact!=50: fail('source snapshot/source_original validation count failure')

    created=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        con.execute('BEGIN IMMEDIATE')
        for p in payloads:
            vals=db_values(p,created); cols=list(vals)
            con.execute(f"INSERT INTO questions ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",[vals[c] for c in cols])
        con.commit()
    except Exception:
        con.rollback(); raise

    integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
    post=con.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    dup2=con.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)').fetchone()[0]
    if integrity!='ok' or post!=500 or dup2: fail(f'post core failure integrity={integrity} count={post} dup={dup2}')

    schema=list(con.execute('PRAGMA table_info(questions)'))
    req={r[1] for r in schema if r[3]==1}; req.add('question_uid')
    missing_required=0
    for row in con.execute('SELECT * FROM questions'):
        for col in req:
            v=row[col]
            if v is None or (isinstance(v,str) and not v.strip()): missing_required+=1
    if missing_required: fail(f'missing_required={missing_required}')
    bad_json=0
    for row in con.execute('SELECT * FROM questions'):
        for col in JSON_COLS:
            try: json.loads(row[col])
            except Exception: bad_json+=1
    if bad_json: fail(f'bad_json={bad_json}')
    pred=' OR '.join(f'{g}<>1' for g in GATES)
    failed=con.execute(f"SELECT COUNT(*) FROM questions WHERE audit_status<>'FINAL_QA_PASS' OR second_pass_status<>'PASS' OR {pred}").fetchone()[0]
    if failed: fail(f'rows failing gates/status={failed}')

    reread=0; mismatches={}
    for p in payloads:
        saved=con.execute('SELECT * FROM questions WHERE question_uid=?',(p['question_uid'],)).fetchone(); exp=db_values(p,created)
        diff=[c for c,v in exp.items() if saved[c]!=v]
        if diff: mismatches[p['question_uid']]=diff
        else: reread+=1
    if reread!=50: fail(f'reread_exact={reread}/50 {mismatches}')
    fp_after,fp_count_after=fingerprint(con)
    protected=fp_before==fp_after and fp_count==fp_count_after==450
    if not protected: fail('Q0001-Q0450 changed')

    completed={r[0] for r in con.execute('SELECT question_uid FROM questions')}
    next_uid=None
    for r in src.execute("SELECT question_uid FROM questions WHERE source_bank='v2' ORDER BY source_id ASC"):
        if r['question_uid'] not in completed: next_uid=r['question_uid']; break
    if next_uid!='V2-Q0501': fail(f'next expected Q0501 got {next_uid}')
    con.close(); src.close()
    source_after=sh('git','hash-object',str(SOURCE)); source_diff=sh('git','diff','--name-only','--',str(SOURCE))
    if source_after!=EXPECTED_SOURCE_BLOB or source_diff: fail(f'source changed {source_after} {source_diff!r}')
    new_blob=sh('git','hash-object',str(CANONICAL))
    report={'status':'PASS','batch':'V2-Q0451-V2-Q0500','approved_items_count':50,'approved_json_valid':50,'source_rows_verified_exact':'50/50','canonical_base_blob':EXPECTED_CANONICAL_BLOB,'canonical_new_blob':new_blob,'canonical_integrity':integrity,'canonical_question_count_before':pre,'canonical_question_count_after':post,'duplicate_uid_count':dup2,'missing_required_count':missing_required,'bad_json_count':bad_json,'reread_exact':f'{reread}/50','all_14_gates_pass_rows':'500/500','protected_q0001_q0450_unchanged':protected,'protected_q0001_q0450_fingerprint_before':fp_before,'protected_q0001_q0450_fingerprint_after':fp_after,'source_blob_before':EXPECTED_SOURCE_BLOB,'source_blob_after':source_after,'source_db_unchanged':True,'next_uid':next_uid,'single_sqlite_transaction':True,'generated_at_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat()}
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__': main()
