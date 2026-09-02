#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path

BASE_DB = Path('NCLEX_CANONICAL.db')
SOURCE_DB = Path('NCLEX_COMMERCIAL_MASTER_CURRENT.db')
REVIEW_DIR = Path('RULE1_CLEANUP_2000_REVIEWED')
SELECTOR = Path('RULE1_CLEANUP_2000_NEXT_CANDIDATE.json')
EXPECTED_CANONICAL_BLOB = '182a1e979e11d62bebc85c5ceb859056b8812963'
EXPECTED_SOURCE_BLOB = '07e335d471ef1b4689406ba41eb98eaa2ca41472'
EXPECTED_CANONICAL_QUESTIONS = 2000
EXPECTED_SOURCE_QUESTIONS = 3525
EXPECTED_SOURCE_CASES = 75
EXPECTED_BLUEPRINT_ROWS = 8
EXPECTED_CANDIDATES = 1322
KEYS = ['A','B','C','D']
GATES = [
    'source_authority_verified','currentness_verified','exact_locator_verified','stem_verified',
    'correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified',
    'ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified',
    'independent_qa_passed','no_unresolved_conflict',
]
CANON_CLIENT = {
    'Management of Care':'Management of Care',
    'Safety & Infection Prevention and Control':'Safety and Infection Prevention and Control',
    'Safety and Infection Prevention and Control':'Safety and Infection Prevention and Control',
    'Health Promotion and Maintenance':'Health Promotion and Maintenance',
    'Psychosocial Integrity':'Psychosocial Integrity',
    'Basic Care and Comfort':'Basic Care and Comfort',
    'Pharmacological and Parenteral Therapies':'Pharmacological and Parenteral Therapies',
    'Reduction of Risk Potential':'Reduction of Risk Potential',
    'Physiological Adaptation':'Physiological Adaptation',
}
CANON_BP_TITLE = '2026 NCLEX-RN Test Plan'
CANON_BP_VERSION = 'Effective April 1, 2026 through March 31, 2029'


def cjson(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',',':'))


def git_blob(path: str) -> str:
    return subprocess.check_output(['git','rev-parse',f'HEAD:{path}'], text=True).strip()


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def payload_from_row(r: sqlite3.Row) -> dict:
    return {
      'question_uid':r['question_uid'],'source_bank':r['source_bank'],'source_table':r['source_table'],'source_id':r['source_id'],
      'mode':r['mode'],'case_uid':r['case_uid'],'original_sequence':r['original_sequence'],'official_case_slot':r['official_case_slot'],
      'slot_variant':r['slot_variant'],'category_id':r['category_id'],'client_need':r['client_need'],'specialty':r['specialty'],
      'difficulty':r['difficulty'],'cjmm_skill':r['cjmm_skill'],'item_type_raw':r['item_type_raw'],'renderer_type':r['renderer_type'],
      'stem':r['stem'],'item_data':json.loads(r['item_data_json']),'correct_answer':json.loads(r['correct_answer_json']),
      'rationale':r['rationale'],'scoring_rule':r['scoring_rule'],'educational_objective':r['educational_objective'],
      'source_organization':r['source_organization'],'source_document_title':r['source_document_title'],
      'source_version_date':r['source_version_date'],'source_accessed_date':r['source_accessed_date'],
      'source_locator':r['source_locator'],'source_url':r['source_url'],'source_claim_supported':r['source_claim_supported'],
      'blueprint_source_organization':r['blueprint_source_organization'],'blueprint_document_title':r['blueprint_document_title'],
      'blueprint_version':r['blueprint_version'],'blueprint_locator':r['blueprint_locator'],'blueprint_url':r['blueprint_url'],
      'blueprint_topic':r['blueprint_topic'],'stable_sort_key':r['stable_sort_key'],'source_db_filename':r['source_db_filename'],
      'source_db_blob_sha':r['source_db_blob_sha'],'source_original':json.loads(r['source_original_json']),
      'correction_summary':r['correction_summary'],'audit_status':r['audit_status'],'second_pass_status':r['second_pass_status'],
      'audit_date_utc':r['audit_date_utc'],'audit_reviewer':r['audit_reviewer'],
      'gates':{g:int(r[g]) for g in GATES},'audit_findings':json.loads(r['audit_findings_json']),
    }


def load_reviews(expected_reviewed: int) -> list[dict]:
    selector=json.loads(SELECTOR.read_text(encoding='utf-8'))
    if int(selector['reviewed_staging_uid_count']) != expected_reviewed:
        raise SystemExit(f"BLOCKED selector reviewed={selector['reviewed_staging_uid_count']} expected={expected_reviewed}")
    if int(selector['candidate_uid_count_from_scan']) != EXPECTED_CANDIDATES:
        raise SystemExit('BLOCKED candidate total')
    reviews=[]
    for p in sorted(REVIEW_DIR.glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        uid=d.get('question_uid')
        if not uid:
            raise SystemExit(f'BLOCKED missing UID {p}')
        if d.get('status')!='FINAL_QA_PASS' or d.get('audit_status')!='FINAL_QA_PASS' or d.get('second_pass_status')!='PASS':
            raise SystemExit(f'BLOCKED non-final review {uid}')
        gates=d.get('gates') or {}
        bad=[g for g in GATES if int(gates.get(g,0))!=1]
        if bad:
            raise SystemExit(f'BLOCKED gates {uid}: {bad}')
        if not isinstance(d.get('options'),dict) or sorted(d['options'])!=KEYS or d.get('correct_option') not in KEYS:
            raise SystemExit(f'BLOCKED answer shape {uid}')
        reviews.append(d)
    uids=[d['question_uid'] for d in reviews]
    dup=[u for u,n in Counter(uids).items() if n!=1]
    if dup:
        raise SystemExit(f'BLOCKED duplicate review UIDs {dup[:20]}')
    if len(reviews)!=expected_reviewed:
        raise SystemExit(f'BLOCKED review files={len(reviews)} expected={expected_reviewed}')
    return reviews


def build_cleaned_canonical(path: Path, reviews: list[dict]) -> None:
    shutil.copyfile(BASE_DB,path)
    con=sqlite3.connect(path); con.row_factory=sqlite3.Row
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise SystemExit('BLOCKED canonical temp integrity before')
        rows=con.execute('SELECT * FROM questions').fetchall()
        if len(rows)!=EXPECTED_CANONICAL_QUESTIONS:
            raise SystemExit(f'BLOCKED canonical count {len(rows)}')
        if any(r['audit_status']!='FINAL_QA_PASS' or r['second_pass_status']!='PASS' for r in rows):
            raise SystemExit('BLOCKED canonical final status')
        if any(any(int(r[g])!=1 for g in GATES) for r in rows):
            raise SystemExit('BLOCKED canonical gates')
        db_uids={r['question_uid'] for r in rows}
        missing=sorted({d['question_uid'] for d in reviews}-db_uids)
        if missing:
            raise SystemExit(f'BLOCKED review missing from canonical {missing[:20]}')
        con.execute('BEGIN IMMEDIATE')
        for d in reviews:
            uid=d['question_uid']; r=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
            item_data=json.loads(r['item_data_json']); correct=json.loads(r['correct_answer_json'])
            item_data['options']={k:d['options'][k] for k in KEYS}; correct['correct_option']=d['correct_option']
            client=d.get('client_need',r['client_need'])
            if client not in CANON_CLIENT:
                raise SystemExit(f'BLOCKED client need {uid}: {client}')
            difficulty=d.get('difficulty',r['difficulty'])
            if difficulty=='moderate': difficulty='medium'
            if difficulty not in {'easy','medium','hard'}:
                raise SystemExit(f'BLOCKED difficulty {uid}: {difficulty}')
            vals={
              'category_id':d.get('category_id',r['category_id']),'client_need':CANON_CLIENT[client],'difficulty':difficulty,
              'stem':d['stem'],'item_data_json':cjson(item_data),'correct_answer_json':cjson(correct),'rationale':d['rationale'],
              'educational_objective':d['educational_objective'],'source_organization':d['source_organization'],
              'source_document_title':d['source_document_title'],'source_version_date':d['source_version_date'],
              'source_accessed_date':d['source_accessed_date'],'source_locator':d['source_locator'],'source_url':d['source_url'],
              'source_claim_supported':d['source_claim_supported'],'blueprint_document_title':CANON_BP_TITLE,
              'blueprint_version':CANON_BP_VERSION,'blueprint_locator':d.get('blueprint_locator',r['blueprint_locator']),
              'blueprint_url':d.get('blueprint_url',r['blueprint_url']),'blueprint_topic':d.get('blueprint_topic',r['blueprint_topic']),
              'correction_summary':d.get('correction_summary',r['correction_summary']),'audit_status':'FINAL_QA_PASS',
              'second_pass_status':'PASS','audit_findings_json':cjson(d.get('audit_findings',{})),
            }
            for g in GATES: vals[g]=1
            sets=','.join(f'{k}=?' for k in vals)
            con.execute(f'UPDATE questions SET {sets} WHERE question_uid=?',[*vals.values(),uid])
            updated=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
            digest=hashlib.sha256(cjson(payload_from_row(updated)).encode('utf-8')).hexdigest()
            con.execute('UPDATE questions SET payload_sha256=? WHERE question_uid=?',(digest,uid))
        con.commit()
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise SystemExit('BLOCKED canonical temp integrity after')
        if con.execute('SELECT COUNT(*) FROM questions').fetchone()[0]!=EXPECTED_CANONICAL_QUESTIONS:
            raise SystemExit('BLOCKED canonical temp count after')
    finally:
        con.close()


def merge_into_full_source(output: Path, cleaned: Path, expected_reviewed: int) -> dict:
    shutil.copyfile(SOURCE_DB,output)
    out=sqlite3.connect(output); out.row_factory=sqlite3.Row
    can=sqlite3.connect(cleaned); can.row_factory=sqlite3.Row
    try:
        if out.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise SystemExit('BLOCKED source copy integrity before')
        q_before=out.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
        cases_before=out.execute('SELECT COUNT(*) FROM case_studies').fetchone()[0]
        bp_before=out.execute('SELECT COUNT(*) FROM nclex_2026_blueprint').fetchone()[0]
        if (q_before,cases_before,bp_before)!=(EXPECTED_SOURCE_QUESTIONS,EXPECTED_SOURCE_CASES,EXPECTED_BLUEPRINT_ROWS):
            raise SystemExit(f'BLOCKED source counts {(q_before,cases_before,bp_before)}')
        source_cols=[r['name'] for r in out.execute('PRAGMA table_info(questions)')]
        canonical_rows=can.execute('SELECT * FROM questions ORDER BY stable_sort_key,question_uid').fetchall()
        if len(canonical_rows)!=EXPECTED_CANONICAL_QUESTIONS: raise SystemExit('BLOCKED cleaned canonical count')
        canonical_uids={r['question_uid'] for r in canonical_rows}
        source_uids={r['question_uid'] for r in out.execute('SELECT question_uid FROM questions')}
        missing=sorted(canonical_uids-source_uids)
        if missing: raise SystemExit(f'BLOCKED audited UIDs missing from source {missing[:20]}')

        out.execute('BEGIN IMMEDIATE')
        applied=0
        for c in canonical_rows:
            uid=c['question_uid']; s=out.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
            if (s['source_bank'],s['source_table'],s['source_id'])!=(c['source_bank'],c['source_table'],c['source_id']):
                raise SystemExit(f'BLOCKED source identity mismatch {uid}')
            source_name=' — '.join(x for x in [c['source_organization'],c['source_document_title']] if x)
            source_detail=' | '.join(x for x in [c['source_locator'],c['source_claim_supported']] if x)
            vals={
              'mode':c['mode'],'case_uid':c['case_uid'],'original_sequence':c['original_sequence'],
              'official_case_slot':c['official_case_slot'],'slot_variant':c['slot_variant'],'category_id':c['category_id'],
              'client_need':c['client_need'],'specialty':c['specialty'],'difficulty':c['difficulty'],'cjmm_skill':c['cjmm_skill'],
              'item_type_raw':c['item_type_raw'],'renderer_type':c['renderer_type'],'stem':c['stem'],
              'item_data_json':c['item_data_json'],'correct_answer_json':c['correct_answer_json'],'rationale':c['rationale'],
              'scoring_rule':c['scoring_rule'],'source_name':source_name,'source_detail':source_detail,
              'source_url':c['source_url'],'stable_sort_key':c['stable_sort_key'],
            }
            sets=','.join(f'{k}=?' for k in vals)
            out.execute(f'UPDATE questions SET {sets} WHERE question_uid=?',[*vals.values(),uid]); applied+=1

        out.execute('DROP TABLE IF EXISTS rule1_audited_questions')
        audit_cols=[r['name'] for r in can.execute('PRAGMA table_info(questions)')]
        col_defs=[]
        for r in can.execute('PRAGMA table_info(questions)'):
            typ=r['type'] or 'TEXT'; col_defs.append(f'"{r["name"]}" {typ}')
        out.execute('CREATE TABLE rule1_audited_questions('+','.join(col_defs)+')')
        placeholders=','.join('?' for _ in audit_cols)
        out.executemany(
            'INSERT INTO rule1_audited_questions('+','.join(f'"{c}"' for c in audit_cols)+') VALUES ('+placeholders+')',
            ([r[c] for c in audit_cols] for r in canonical_rows)
        )
        out.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_rule1_audited_uid ON rule1_audited_questions(question_uid)')
        out.execute('DROP TABLE IF EXISTS rule1_merge_metadata')
        out.execute('CREATE TABLE rule1_merge_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
        meta={
          'role':'FULL_SOURCE_WITH_RULE1_AUDITED_OVERLAY','source_blob':EXPECTED_SOURCE_BLOB,
          'canonical_blob':EXPECTED_CANONICAL_BLOB,'source_questions':str(EXPECTED_SOURCE_QUESTIONS),
          'audited_questions_applied':str(EXPECTED_CANONICAL_QUESTIONS),'cleanup_reviews_overlaid':str(expected_reviewed),
          'source_only_questions_preserved':str(EXPECTED_SOURCE_QUESTIONS-EXPECTED_CANONICAL_QUESTIONS),
        }
        out.executemany('INSERT INTO rule1_merge_metadata(key,value) VALUES(?,?)',meta.items())
        out.commit()

        integrity=out.execute('PRAGMA integrity_check').fetchone()[0]
        q_after=out.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
        cases_after=out.execute('SELECT COUNT(*) FROM case_studies').fetchone()[0]
        bp_after=out.execute('SELECT COUNT(*) FROM nclex_2026_blueprint').fetchone()[0]
        audit_count=out.execute('SELECT COUNT(*) FROM rule1_audited_questions').fetchone()[0]
        dup=out.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)').fetchone()[0]
        mismatches=0
        for c in canonical_rows:
            s=out.execute('SELECT stem,item_data_json,correct_answer_json,rationale,source_url FROM questions WHERE question_uid=?',(c['question_uid'],)).fetchone()
            if tuple(s)!=(c['stem'],c['item_data_json'],c['correct_answer_json'],c['rationale'],c['source_url']): mismatches+=1
        if integrity!='ok' or (q_after,cases_after,bp_after)!=(q_before,cases_before,bp_before) or audit_count!=EXPECTED_CANONICAL_QUESTIONS or dup or mismatches:
            raise SystemExit(f'BLOCKED final check integrity={integrity} counts={(q_after,cases_after,bp_after)} audit={audit_count} dup={dup} mismatches={mismatches}')

        out.execute("ATTACH DATABASE ? AS original",(str(SOURCE_DB),))
        outside_changed_terms=[]
        for col in source_cols:
            outside_changed_terms.append(f'NOT (q."{col}" IS o."{col}")')
        outside_changed=out.execute(
            'SELECT COUNT(*) FROM questions q JOIN original.questions o ON o.question_uid=q.question_uid '
            'WHERE q.question_uid NOT IN (SELECT question_uid FROM rule1_audited_questions) AND ('+' OR '.join(outside_changed_terms)+')'
        ).fetchone()[0]
        out.execute('DETACH DATABASE original')
        if outside_changed!=0: raise SystemExit(f'BLOCKED source-only rows changed={outside_changed}')
        return {
          'questions_before':q_before,'questions_after':q_after,'case_studies_before':cases_before,'case_studies_after':cases_after,
          'blueprint_rows_before':bp_before,'blueprint_rows_after':bp_after,'audited_questions_applied':applied,
          'cleanup_reviews_overlaid':expected_reviewed,'audited_baseline_without_cleanup_override':applied-expected_reviewed,
          'source_only_questions_preserved':q_after-applied,'source_only_rows_changed':outside_changed,
          'audited_content_mismatches':mismatches,'duplicate_question_uid_groups':dup,'rule1_audit_rows':audit_count,
          'sqlite_integrity_check':integrity,
        }
    finally:
        can.close(); out.close()


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--expected-reviewed',type=int,required=True); ap.add_argument('--output',required=True); ap.add_argument('--report',required=True); args=ap.parse_args()
    output=Path(args.output); report_path=Path(args.report); temp=Path(str(output)+'.canonical.tmp')
    canonical_blob=git_blob(str(BASE_DB)); source_blob=git_blob(str(SOURCE_DB))
    if canonical_blob!=EXPECTED_CANONICAL_BLOB: raise SystemExit(f'BLOCKED canonical blob {canonical_blob}')
    if source_blob!=EXPECTED_SOURCE_BLOB: raise SystemExit(f'BLOCKED source blob {source_blob}')
    reviews=load_reviews(args.expected_reviewed)
    if output.exists(): output.unlink()
    if temp.exists(): temp.unlink()
    try:
        build_cleaned_canonical(temp,reviews)
        merge=merge_into_full_source(output,temp,args.expected_reviewed)
    finally:
        if temp.exists(): temp.unlink()
    src=sqlite3.connect(SOURCE_DB); can=sqlite3.connect(BASE_DB)
    try:
        source_integrity=src.execute('PRAGMA integrity_check').fetchone()[0]; source_count=src.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
        canonical_integrity=can.execute('PRAGMA integrity_check').fetchone()[0]; canonical_count=can.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    finally:
        src.close(); can.close()
    if source_integrity!='ok' or source_count!=EXPECTED_SOURCE_QUESTIONS or canonical_integrity!='ok' or canonical_count!=EXPECTED_CANONICAL_QUESTIONS:
        raise SystemExit('BLOCKED input DB changed during build')
    selector=json.loads(SELECTOR.read_text(encoding='utf-8'))
    report={
      'status':'RULE1_FULL_SOURCE_MERGE_PASS','output_db_file':str(output),'output_db_sha256':sha256_file(output),
      'input_source_file':str(SOURCE_DB),'input_source_blob':source_blob,'input_source_integrity':source_integrity,
      'input_source_question_count':source_count,'input_canonical_file':str(BASE_DB),'input_canonical_blob':canonical_blob,
      'input_canonical_integrity':canonical_integrity,'input_canonical_question_count':canonical_count,
      'candidate_uid_count_from_scan':int(selector['candidate_uid_count_from_scan']),'reviewed_staging_uid_count':int(selector['reviewed_staging_uid_count']),
      'review_files_validated':len(reviews),'next_selector_uid':(selector.get('candidate') or {}).get('question_uid'),
      'source_db_modified':False,'canonical_db_modified':False,**merge,
    }
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_FULL_SOURCE_MERGE='+cjson(report))

if __name__=='__main__': main()
