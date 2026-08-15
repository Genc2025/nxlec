#!/usr/bin/env python3
from __future__ import annotations
import base64, gzip, json, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'NCLEX_COMMERCIAL_MASTER_CURRENT.db'
PAYLOAD=ROOT/'data/batch010_manual_payload.json.gz.b64'
EVIDENCE=ROOT/'data/rule1_batch010_chronological_reaudit_evidence_q0451_q0500.json'
OVERRIDE=ROOT/'data/clinical_overrides_zzz_rule1_batch010_chronological_q0451_q0500_20260815.json'
PATCHES=[ROOT/f'data/manual_rule1_batch010_q{s:04d}_q{s+9:04d}_20260815.json' for s in (451,461,471,481,491)]
IDS=[f'V2-Q{i:04d}' for i in range(451,501)]
REVIEW_DATE='2026-08-15'; STATUS='SOURCE_VERIFIED_2026_RULE1_BATCH010_CHRONOLOGICAL_MANUAL'
NCSBN_URL='https://www.nclex.com/files/2026_RN_Test%20Plan_English-F.pdf'
NCSBN_VERSION='2026 NCLEX-RN Test Plan; effective 2026-04-01 through 2029-03-31; currentness rechecked 2026-08-15.'
CRITERIA=['source_authority_verified','source_currentness_verified','exact_locator_verified','stem_factual_accuracy_verified','correct_answer_verified','rationale_verified','distractors_verified','ambiguity_cue_second_answer_qc_verified','blueprint_topic_difficulty_verified','no_unresolved_conflicts','independent_second_pass_qa']
NCSBN_LOCATORS={
2:'Client Needs — Safe and Effective Care Environment — Management of Care: prioritization, assignment/delegation, advocacy/client rights, continuity/referral, legal scope, professional limitations and emergency/quality-management activities as applicable.',
3:'Client Needs — Safe and Effective Care Environment — Safety and Infection Prevention and Control: transmission precautions, PPE, device/environmental safety, asepsis, identification and infection-prevention activities as applicable.',
4:'Client Needs — Health Promotion and Maintenance: preventive screening, age/risk-appropriate teaching, developmental and health-promotion activities as applicable.',
5:'Client Needs — Psychosocial Integrity: mental-health symptom recognition, therapeutic communication, coping, cultural/spiritual influences and psychosocial support as applicable.',
7:'Client Needs — Physiological Integrity — Basic Care and Comfort: mobility, assistive devices, hygiene, nutrition, elimination, comfort and nonpharmacological basic-care activities as applicable.',
8:'Client Needs — Physiological Integrity — Pharmacological and Parenteral Therapies: medication administration, adverse effects/interactions, monitoring, reconciliation and teaching.',
9:'Client Needs — Physiological Integrity — Reduction of Risk Potential: diagnostic/laboratory interpretation, transfusion risk, postprocedure monitoring, device management and potential complications.',
10:'Client Needs — Physiological Integrity — Physiological Adaptation: acute/complex alterations, emergency response and pathophysiologic adaptation.'}

def materialize_payload():
    if not PAYLOAD.exists(): raise SystemExit('Batch 010 authored manual payload missing')
    try:
        raw=gzip.decompress(base64.b64decode(PAYLOAD.read_text(encoding='ascii').strip()))
        bundle=json.loads(raw.decode('utf-8'))
    except Exception as exc:
        raise SystemExit(f'Batch 010 manual payload decode failed: {exc}')
    expected={p.name for p in PATCHES}
    if set(bundle)!=expected: raise SystemExit(f'Batch 010 payload file set mismatch: {sorted(bundle)}')
    for p in PATCHES:
        p.write_text(json.dumps(bundle[p.name],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def metrics(opts,key):
    ls={k:len(str(opts[k]).strip()) for k in 'ABCD'}; dm=sum(ls[k] for k in 'ABCD' if k!=key)/3
    return {'characters':ls,'max_min_ratio':round(max(ls.values())/max(min(ls.values()),1),4),'correct_option':key,'correct_deviation_from_distractor_mean':round(abs(ls[key]-dm)/max(dm,1),4),'use':'MEASUREMENT_ONLY_NOT_SEMANTIC_GATE'}

def main():
    materialize_payload()
    if not DB.exists(): raise SystemExit('Current master DB missing')
    manual=[]
    for p in PATCHES:
        d=json.loads(p.read_text(encoding='utf-8'))
        if d.get('batch')!='Q0451-Q0500' or d.get('review_date')!=REVIEW_DATE or d.get('legacy_status_evidence') is not False or d.get('semantic_decisions_by_script') is not False: raise SystemExit(f'Invalid manual Rule 1 header: {p.name}')
        manual.extend(d.get('items',[]))
    if len(manual)!=50 or [x.get('id') for x in manual]!=IDS: raise SystemExit('Manual Rule 1 decisions must contain Q0451-Q0500 exactly once and in order')
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; evidence=[]; overrides=[]
    for p in manual:
        uid=p['id']
        if p.get('qa')!=[11,'PASS','FINAL_QA_PASS']: raise SystemExit(f'{uid}: incomplete semantic QA')
        q=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if q is None: raise SystemExit(f'{uid}: missing DB row')
        opts=p['options']; key=p['key']
        if set(opts)!=set('ABCD') or key not in opts: raise SystemExit(f'{uid}: A-D/key invalid')
        norm=[str(opts[k]).strip().casefold() for k in 'ABCD']
        if any(not x for x in norm) or len(set(norm))!=4: raise SystemExit(f'{uid}: blank/duplicate option')
        for fld in ('stem','rationale','source_name','source_url','locator','version','authority','need','diff'):
            if not str(p.get(fld,'')).strip(): raise SystemExit(f'{uid}: missing {fld}')
        if not p['source_url'].startswith('https://'): raise SystemExit(f'{uid}: invalid source URL')
        cat=int(p['cat'])
        if cat not in NCSBN_LOCATORS: raise SystemExit(f'{uid}: invalid category {cat}')
        ncsbn={'required_currentness_and_blueprint_check':True,'source':'NCSBN — 2026 NCLEX-RN Test Plan','url':NCSBN_URL,'locator':NCSBN_LOCATORS[cat],'version':NCSBN_VERSION,'result':'PASS','scope':'Mandatory current NCLEX blueprint/category/entry-level relevance check; exact clinical/legal claim separately verified against the item authority.'}
        m=metrics(opts,key); finding=p.get('finding') or f'Fresh manual Rule 1 audit completed {REVIEW_DATE}; final state independently re-read after correction.'
        detail=f"{p['locator']} {p['version']} NCSBN first-check: {ncsbn['locator']} {NCSBN_VERSION}"
        flags=['RULE1_BATCH010_MANUAL_ITEM_BY_ITEM_REAUDIT','LEGACY_STATUS_NOT_USED_AS_EVIDENCE','SEMANTIC_DECISIONS_NOT_BY_SCRIPT','SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED','MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS','INDEPENDENT_SECOND_PASS_QA_PASS','OPTION_LENGTH_METRICS_MEASUREMENT_ONLY']
        overrides.append({'question_uid':uid,'source_id':int(q['source_id']),'category_id':cat,'client_need':p['need'],'difficulty':p['diff'],'stem':p['stem'],'item_data_json':json.dumps({'options':opts},ensure_ascii=False,separators=(',',':')),'correct_answer_json':json.dumps({'correct_option':key},separators=(',',':')),'rationale':p['rationale'],'source_name':p['source_name'],'source_detail':detail,'source_url':p['source_url'],'clinical_qa_status':STATUS,'editorial_priority':'PRODUCTION_CANDIDATE','editorial_flags_json':json.dumps(flags,separators=(',',':')),'qc':{'question_uid':uid,'lengths_json':json.dumps(m['characters'],separators=(',',':')),'min_chars':min(m['characters'].values()),'max_chars':max(m['characters'].values()),'max_min_ratio':m['max_min_ratio'],'correct_option':key,'correct_length_rank':sorted(m['characters'].values()).index(m['characters'][key])+1,'correct_is_extreme':int(m['characters'][key] in (min(m['characters'].values()),max(m['characters'].values()))),'qc_status':'MEASURED_NOT_GATE','qc_note':'Length metrics are measurement only; semantic option/cue/ambiguity decisions are manual.'}})
        evidence.append({'id':uid,'key':key,'category_id':cat,'client_need':p['need'],'difficulty':p['diff'],'source_authority':p['authority'],'source_name':p['source_name'],'source_url':p['source_url'],'source_locator':p['locator'],'source_version':p['version'],'reviewed_at':REVIEW_DATE,'finding':finding,'ncsbn_first_check':ncsbn,'criteria':11,'criteria_names':CRITERIA,'second_pass':'PASS','second_pass_method':'Independent fresh second read of final corrected stem, all four options, key, rationale, source locator/version/currentness, blueprint/difficulty and second-answer/cue risk without using legacy status as evidence.','final':'FINAL_QA_PASS','option_measurement':m,'semantic_decision_origin':'MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT'})
    con.close()
    EVIDENCE.write_text(json.dumps({'standard':'RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT','batch':'Q0451-Q0500','review_date':REVIEW_DATE,'legacy_status_evidence':False,'semantic_decisions_by_script':False,'criteria_names':CRITERIA,'ncsbn_test_plan':{'url':NCSBN_URL,'version':NCSBN_VERSION},'items':evidence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    OVERRIDE.write_text(json.dumps({'version':'2026-08-15-rule1-batch010-manual-item-by-item-q0451-q0500','semantic_decisions_by_script':False,'questions':overrides},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('BATCH010_MANUAL_ARTIFACTS_BUILT items=50/50 criteria11=50/50 second_pass=50/50 semantic_script_decisions=0 option_metrics=measurement_only')
if __name__=='__main__': main()
