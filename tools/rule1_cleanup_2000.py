#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sqlite3, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DB = Path('NCLEX_CANONICAL.db')
CORR = Path('RULE1_CLEANUP_2000_CORRECTIONS.json')
OUT = Path('RULE1_CLEANUP_2000_RESULT.json')
EXPECTED_INPUT_BLOB = '182a1e979e11d62bebc85c5ceb859056b8812963'
GATES = [
 'source_authority_verified','currentness_verified','exact_locator_verified','stem_verified',
 'correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified',
 'ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified',
 'independent_qa_passed','no_unresolved_conflict'
]
KEYS = ['A','B','C','D']
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

def payload_from_row(r):
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

def rotate_to_target(opts, old_correct, target):
    oi=KEYS.index(old_correct); ti=KEYS.index(target); shift=(ti-oi)%4
    new={}
    for i,k in enumerate(KEYS): new[KEYS[(i+shift)%4]]=opts[k]
    return {k:new[k] for k in KEYS}, target

def append_finding(existing, finding):
    if isinstance(existing,list): return existing + [finding]
    if isinstance(existing,dict):
        out=dict(existing); notes=out.get('bank_cleanup_notes',[])
        if not isinstance(notes,list): notes=[notes]
        out['bank_cleanup_notes']=notes+[finding]; return out
    return [existing, finding]

def main():
    blob=subprocess.check_output(['git','rev-parse','HEAD:NCLEX_CANONICAL.db'],text=True).strip()
    if blob != EXPECTED_INPUT_BLOB:
        raise SystemExit(f'BLOCKED input canonical blob {blob}')
    cfg=json.loads(CORR.read_text(encoding='utf-8'))
    semantic=cfg.get('semantic_corrections',{})
    reviewed=set(cfg.get('semantic_reviewed_uids',[]))
    required_review=set(cfg.get('required_semantic_review_uids',[]))
    if required_review-reviewed:
        raise SystemExit(f'BLOCKED semantic review incomplete: {len(required_review-reviewed)} items')
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise SystemExit('BLOCKED integrity before')
    rows=con.execute('SELECT * FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    if len(rows)!=2000: raise SystemExit(f'BLOCKED expected 2000 got {len(rows)}')
    if any(r['audit_status']!='FINAL_QA_PASS' or r['second_pass_status']!='PASS' for r in rows): raise SystemExit('BLOCKED status')
    if any(any(r[g]!=1 for g in GATES) for r in rows): raise SystemExit('BLOCKED existing gate')

    before_key=Counter(); after_key=Counter(); mechanical_count=0; semantic_count=0
    preserved_fail=[]; semantic_missing=[]; now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    original_snapshot={r['question_uid']:{'stem':r['stem'],'rationale':r['rationale'],'source_url':r['source_url'],'source_locator':r['source_locator'],
        'opts':json.loads(r['item_data_json'])['options'],'correct':json.loads(r['correct_answer_json'])['correct_option']} for r in rows}

    con.execute('BEGIN IMMEDIATE')
    for idx,r0 in enumerate(rows):
        uid=r0['question_uid']; p=payload_from_row(r0)
        old_opts=dict(p['item_data']['options']); old_correct=p['correct_answer']['correct_option']; before_key[old_correct]+=1
        if sorted(old_opts)!=KEYS or old_correct not in KEYS: raise SystemExit(f'BLOCKED malformed {uid}')
        old_correct_text=old_opts[old_correct]
        sem=semantic.get(uid)
        if sem:
            semantic_count+=1
            allowed={'stem','options','correct_option','rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_topic','correction_summary_append','audit_findings_append'}
            extra=set(sem)-allowed
            if extra: raise SystemExit(f'BLOCKED unsupported semantic fields {uid}: {sorted(extra)}')
            if 'stem' in sem: p['stem']=sem['stem']
            if 'options' in sem:
                if sorted(sem['options'])!=KEYS: raise SystemExit(f'BLOCKED semantic options {uid}')
                p['item_data']['options']={k:sem['options'][k] for k in KEYS}
            if 'correct_option' in sem: p['correct_answer']['correct_option']=sem['correct_option']
            for f in ['rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_topic']:
                if f in sem: p[f]=sem[f]
            if sem.get('correction_summary_append'):
                p['correction_summary']=(p['correction_summary'].rstrip()+ ' ' + sem['correction_summary_append'].strip()).strip()
            for note in sem.get('audit_findings_append',[]): p['audit_findings']=append_finding(p['audit_findings'],note)
            if uid not in reviewed: semantic_missing.append(uid)
        if p['client_need'] not in CANON_CLIENT: raise SystemExit(f'BLOCKED unknown client need {uid}: {p["client_need"]}')
        p['client_need']=CANON_CLIENT[p['client_need']]
        if p['difficulty']=='moderate': p['difficulty']='medium'
        if p['difficulty'] not in {'easy','medium','hard'}: raise SystemExit(f'BLOCKED difficulty {uid}: {p["difficulty"]}')
        p['blueprint_document_title']=CANON_BP_TITLE
        p['blueprint_version']=CANON_BP_VERSION
        sem_opts=dict(p['item_data']['options']); sem_correct=p['correct_answer']['correct_option']
        sem_correct_text=sem_opts[sem_correct]
        target=KEYS[idx%4]
        new_opts,new_correct=rotate_to_target(sem_opts,sem_correct,target)
        if new_opts[new_correct] != sem_correct_text: raise SystemExit(f'BLOCKED answer text changed during rotation {uid}')
        if Counter(new_opts.values()) != Counter(sem_opts.values()): raise SystemExit(f'BLOCKED option multiset changed during rotation {uid}')
        p['item_data']['options']=new_opts; p['correct_answer']['correct_option']=new_correct; after_key[new_correct]+=1
        if sem is None:
            if p['stem']!=r0['stem'] or p['rationale']!=r0['rationale'] or p['source_url']!=r0['source_url'] or p['source_locator']!=r0['source_locator']:
                preserved_fail.append(uid)
            if sem_correct_text != old_correct_text: preserved_fail.append(uid)
        mechanical_count+=1
        p['correction_summary']=(p['correction_summary'].rstrip()+ ' Bank-level cleanup normalized Client Need/difficulty/blueprint metadata and rebalanced stored answer labels without changing the answer text.').strip()
        p['audit_findings']=append_finding(p['audit_findings'],{
            'type':'BANK_LEVEL_CLEANUP_2000','date_utc':now,
            'note':'Stored A/B/C/D labels were deterministically rebalanced; correct-answer text and option text set were preserved after any separately reviewed semantic correction. Metadata labels were normalized to one canonical 2026 NCLEX-RN form.'
        })
        payload_sha=hashlib.sha256(cjson(p).encode('utf-8')).hexdigest()
        vals={
          'client_need':p['client_need'],'difficulty':p['difficulty'],'stem':p['stem'],'item_data_json':cjson(p['item_data']),
          'correct_answer_json':cjson(p['correct_answer']),'rationale':p['rationale'],'educational_objective':p['educational_objective'],
          'source_organization':p['source_organization'],'source_document_title':p['source_document_title'],'source_version_date':p['source_version_date'],
          'source_accessed_date':p['source_accessed_date'],'source_locator':p['source_locator'],'source_url':p['source_url'],'source_claim_supported':p['source_claim_supported'],
          'blueprint_document_title':p['blueprint_document_title'],'blueprint_version':p['blueprint_version'],'blueprint_topic':p['blueprint_topic'],
          'correction_summary':p['correction_summary'],'audit_findings_json':cjson(p['audit_findings']),'payload_sha256':payload_sha,
        }
        sets=','.join(f'{k}=?' for k in vals)
        con.execute(f'UPDATE questions SET {sets} WHERE question_uid=?', [*vals.values(),uid])
    if semantic_missing: raise SystemExit(f'BLOCKED semantic corrections not reviewed: {semantic_missing[:20]}')
    if preserved_fail: raise SystemExit(f'BLOCKED mechanical preservation failed: {preserved_fail[:20]}')
    con.commit()

    rows2=con.execute('SELECT * FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
    dup=con.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) c FROM questions GROUP BY question_uid HAVING c>1)').fetchone()[0]
    if integrity!='ok' or dup!=0 or len(rows2)!=2000: raise SystemExit('BLOCKED post integrity/count')
    if any(r['audit_status']!='FINAL_QA_PASS' or r['second_pass_status']!='PASS' for r in rows2): raise SystemExit('BLOCKED post status')
    if any(any(r[g]!=1 for g in GATES) for r in rows2): raise SystemExit('BLOCKED post gates')
    key2=Counter(json.loads(r['correct_answer_json'])['correct_option'] for r in rows2)
    if key2 != Counter({'A':500,'B':500,'C':500,'D':500}): raise SystemExit(f'BLOCKED answer balance {key2}')
    if any(r['client_need']=='Safety & Infection Prevention and Control' for r in rows2): raise SystemExit('BLOCKED client normalization')
    if any(r['difficulty']=='moderate' for r in rows2): raise SystemExit('BLOCKED difficulty normalization')
    if any(r['blueprint_document_title']!=CANON_BP_TITLE or r['blueprint_version']!=CANON_BP_VERSION for r in rows2): raise SystemExit('BLOCKED blueprint metadata normalization')
    stems=Counter(re.sub(r'[^a-z0-9]+',' ',r['stem'].lower()).strip() for r in rows2)
    norm_dup=sum(1 for k,v in stems.items() if k and v>1)
    result={
      'status':'STAGING_CLEANUP_PASS','input_canonical_blob':blob,'count':len(rows2),'integrity':integrity,'duplicate_uid_groups':dup,
      'answer_key_before':dict(before_key),'answer_key_after':dict(key2),'semantic_corrections_applied':semantic_count,
      'semantic_review_required_count':len(required_review),'semantic_reviewed_count':len(reviewed),'normalized_stem_duplicate_groups':norm_dup,
      'client_need_labels':dict(Counter(r['client_need'] for r in rows2)),'difficulty_labels':dict(Counter(r['difficulty'] for r in rows2)),
      'blueprint_document_titles':dict(Counter(r['blueprint_document_title'] for r in rows2)),'blueprint_versions':dict(Counter(r['blueprint_version'] for r in rows2)),
      'all_14_gates':'2000/2000','final_qa_pass':'2000/2000','second_pass':'2000/2000','completed_at_utc':now,
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_CLEANUP_RESULT='+json.dumps(result,ensure_ascii=False,separators=(',',':')))
    con.close()

if __name__=='__main__': main()
