#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
SRC=ROOT/'step2_import_q1231_q1240.py'
OUT=ROOT/'step2_import_q1241_q1250.py'
EXPECTED_SRC_BLOB='a0b8c5ac4c5768f27f85a15c2f9e374bc0a89ef3'
MANIFEST=ROOT/'audit'/'Q1241_Q1250_FINAL_QA_PASS.json'
EXPECTED_MANIFEST_BLOB='3cdb253ed2e825593c3aba5b44bec7ea940a6a35'

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()

def replace_one(s,old,new):
    c=s.count(old)
    if c!=1: raise SystemExit(f'expected exactly one occurrence ({c}) of: {old[:120]}')
    return s.replace(old,new,1)

def main():
    if gitblob(SRC)!=EXPECTED_SRC_BLOB: raise SystemExit('baseline importer changed')
    if gitblob(MANIFEST)!=EXPECTED_MANIFEST_BLOB: raise SystemExit('FINAL QA manifest changed')
    s=SRC.read_text()
    pairs=[
      ("STATE_PRE=ROOT/'state'/'step2_final_q0001_q1230.json'","STATE_PRE=ROOT/'state'/'step2_final_q0001_q1240.json'"),
      ("STATE_POST=ROOT/'state'/'step2_final_q0001_q1240.json'","STATE_POST=ROOT/'state'/'step2_final_q0001_q1250.json'"),
      ("MANIFEST=AUD/'Q1231_Q1240_FINAL_QA_PASS.json'","MANIFEST=AUD/'Q1241_Q1250_FINAL_QA_PASS.json'"),
      ("FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1240.json'","FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1250.json'"),
      ("BATCH=ROOT/'batch_specs_1201_1300'/'06_q1231_q1240_author_20260906.json'","BATCH=ROOT/'batch_specs_1201_1300'/'07_q1241_q1250_author_20260906.json'"),
      ("NEW_RANGE=range(1231,1241)","NEW_RANGE=range(1241,1251)"),
      ("EXPECTED_KEYS={1231:'C',1232:'A',1233:'E',1234:'B',1235:'D',1236:'B',1237:'D',1238:'A',1239:'C',1240:'E'}","EXPECTED_KEYS={1241:'B',1242:'D',1243:'A',1244:'E',1245:'C',1246:'A',1247:'E',1248:'C',1249:'D',1250:'B'}"),
      ("EXPECTED_PRE_COUNT=1230","EXPECTED_PRE_COUNT=1240"),
      ("EXPECTED_POST_COUNT=1240","EXPECTED_POST_COUNT=1250"),
      ("EXPECTED_PRE_DB_BLOB='bbfff305e86386f8788e67ea60827416bfb9b3d6'","EXPECTED_PRE_DB_BLOB='ec4393c3699a68616ea2877b464916b0db680328'"),
      ("EXPECTED_BATCH_BLOB='05020adefda182f213d45b92ef2d49803b77abdc'","EXPECTED_BATCH_BLOB='74a9f64982189d58f0bff5e5204ff39cff931fdb'"),
      ("EXPECTED_MANIFEST_BLOB='8b2bcb4af61a5d0eeb60d743982e03ff0e48200e'",f"EXPECTED_MANIFEST_BLOB='{EXPECTED_MANIFEST_BLOB}'"),
      ("AUDIT_ID='STEP2-FINAL-Q0001-Q1240-20260906'","AUDIT_ID='STEP2-FINAL-Q0001-Q1250-20260906'"),
      ("CID_SUFFIX='20260905T223800Z'","CID_SUFFIX='20260906T074000Z'"),
      ("OFFICIAL_SYSTEMS={'Human Development','Respiratory and Renal/Urinary Systems','Blood, Lymphoreticular and Immune Systems','Behavioral Health, Nervous Systems and Special Senses','Musculoskeletal, Skin and Subcutaneous Tissue','Cardiovascular System','Gastrointestinal System','Reproductive and Endocrine Systems','Multisystem Processes and Disorders','Biostatistics, Epidemiology and Population Health','Social Sciences: Communication and Interpersonal Skills'}",
       "OFFICIAL_SYSTEMS={'Human Development','Respiratory and Renal/Urinary Systems','Blood, Lymphoreticular and Immune Systems','Blood & Lymphoreticular/Immune Systems','Behavioral Health, Nervous Systems and Special Senses','Musculoskeletal, Skin and Subcutaneous Tissue','Musculoskeletal, Skin & Subcutaneous Tissue','Cardiovascular System','Gastrointestinal System','Reproductive and Endocrine Systems','Multisystem Processes and Disorders','Biostatistics, Epidemiology and Population Health','Social Sciences: Communication and Interpersonal Skills'}"),
      ("OFFICIAL_COMPETENCIES={'Medical Knowledge: Applying Foundational Science Concepts','Patient Care: Diagnosis, including history and physical examination','Practice-Based Learning and Improvement','Communication and Interpersonal Skills'}",
       "OFFICIAL_COMPETENCIES={'Medical Knowledge: Applying Foundational Science Concepts','Patient Care: Diagnosis, including history and physical examination','Patient Care: Diagnosis','Practice-Based Learning and Improvement','Communication and Interpersonal Skills'}"),
      ("if ''.join(docs[n]['item']['intended_key'] for n in NEW_RANGE)!='CAEBDBDACE': raise SystemExit('candidate key sequence failure')","if ''.join(docs[n]['item']['intended_key'] for n in NEW_RANGE)!='BDAECAECDB': raise SystemExit('candidate key sequence failure')"),
      ("if Counter(d['blueprint']['primary_competency'] for d in docs.values())!=Counter({'Patient Care: Diagnosis, including history and physical examination':6,'Medical Knowledge: Applying Foundational Science Concepts':4}):",
       "if Counter(d['blueprint']['primary_competency'] for d in docs.values())!=Counter({'Patient Care: Diagnosis':5,'Medical Knowledge: Applying Foundational Science Concepts':5}):"),
      ("if m.get('answer_key_distribution')!={'A':2,'B':2,'C':2,'D':2,'E':2} or m.get('answer_key_sequence')!='CAEBDBDACE':",
       "if m.get('answer_key_distribution')!={'A':2,'B':2,'C':2,'D':2,'E':2} or m.get('answer_key_sequence')!='BDAECAECDB':"),
      ("if m.get('competency_distribution')!={'Patient Care: Diagnosis, including history and physical examination':6,'Medical Knowledge: Applying Foundational Science Concepts':4}:",
       "if m.get('competency_distribution')!={'Patient Care: Diagnosis':5,'Medical Knowledge: Applying Foundational Science Concepts':5}:"),
      ("'step2_audit_id':'Q1231-Q1240-FINAL-QA-PASS-Q1230-BOUND-20260906'","'step2_audit_id':'Q1241-Q1250-FINAL-QA-PASS-Q1240-BOUND-20260906-R2'"),
      ("pre.get('contiguous_q0001_q1230') is not True: raise SystemExit('pre-state Q1230 binding failure')","pre.get('contiguous_q0001_q1240') is not True: raise SystemExit('pre-state Q1240 binding failure')"),
      ("if increment_bp!=Counter({'Cardiovascular System':5,'Gastrointestinal System':5}): raise SystemExit('new-block system distribution failure')",
       "if increment_bp!=Counter({'Blood & Lymphoreticular/Immune Systems':5,'Musculoskeletal, Skin & Subcutaneous Tissue':5}): raise SystemExit('new-block system distribution failure')"),
      ("if increment_cp!=Counter({'Patient Care: Diagnosis, including history and physical examination':6,'Medical Knowledge: Applying Foundational Science Concepts':4}): raise SystemExit('new-block competency distribution failure')",
       "if increment_cp!=Counter({'Patient Care: Diagnosis':5,'Medical Knowledge: Applying Foundational Science Concepts':5}): raise SystemExit('new-block competency distribution failure')"),
      ("'range':'Q1231-Q1240'","'range':'Q1241-Q1250'"),
      ("'q1231_q1240_present_exactly_once':True","'q1241_q1250_present_exactly_once':True"),
      ("'contiguous_q0001_q1240':True","'contiguous_q0001_q1250':True"),
      ("assert s['item_count']==1240 and s['step2_final_review_count']==1240 and s['contiguous_q0001_q1240'] is True and s['q1231_q1240_present_exactly_once'] is True",
       "assert s['item_count']==1250 and s['step2_final_review_count']==1250 and s['contiguous_q0001_q1250'] is True and s['q1241_q1250_present_exactly_once'] is True"),
      ("print(json.dumps({'status':'SUCCESS','final_count':1240,'reviews':1240,'integrity':'ok','post_db_blob':post_blob,'state':str(STATE_POST.relative_to(REPO)),'final_audit':str(FINAL_AUDIT.relative_to(REPO))},sort_keys=True))",
       "print(json.dumps({'status':'SUCCESS','final_count':1250,'reviews':1250,'integrity':'ok','post_db_blob':post_blob,'state':str(STATE_POST.relative_to(REPO)),'final_audit':str(FINAL_AUDIT.relative_to(REPO))},sort_keys=True))")
    ]
    for old,new in pairs: s=replace_one(s,old,new)

    # New-block labels must be current exact USMLE labels even though the global reread set
    # intentionally accepts legacy labels already persisted in Q0001-Q1240.
    anchor="    bp=copy.deepcopy(d['blueprint'])\n    if bp.get('primary_system') not in OFFICIAL_SYSTEMS or bp.get('primary_competency') not in OFFICIAL_COMPETENCIES: raise SystemExit(f'Q{n}: canonical blueprint label failure')"
    strict="    bp=copy.deepcopy(d['blueprint'])\n    if bp.get('primary_system') not in {'Blood & Lymphoreticular/Immune Systems','Musculoskeletal, Skin & Subcutaneous Tissue'}: raise SystemExit(f'Q{n}: current system label failure')\n    if bp.get('primary_competency') not in {'Patient Care: Diagnosis','Medical Knowledge: Applying Foundational Science Concepts'}: raise SystemExit(f'Q{n}: current competency label failure')\n    if bp.get('official_outline_path') != [bp.get('primary_system')] or not bp.get('internal_content_path'): raise SystemExit(f'Q{n}: official/internal outline path failure')"
    s=replace_one(s,anchor,strict)

    # Require the repaired evidence-map contract at import time.
    anchor2="    exp=copy.deepcopy(d['explanation']); de=exp.get('distractor_explanations',{})\n    if set(de)!=set('ABCDE') or 'correct' not in str(de[key]).lower() or not str(exp.get('key_explanation','')).strip() or not str(exp.get('educational_objective','')).strip(): raise SystemExit(f'Q{n}: rationale/objective gate failure')"
    strict2=anchor2+"\n    if any(L!=key and ('It is not selected because it does not account for' not in str(de[L]) or not str(de[L]).startswith(f\"Option {L} proposes '\")) for L in 'ABCDE'): raise SystemExit(f'Q{n}: grounded distractor rationale failure')"
    s=replace_one(s,anchor2,strict2)

    # Evidence claims must be identical to the final rationale and non-key claims must remain inference-only.
    anchor3="        base['rationale']=exp['key_explanation'] if L==key else de[L]\n        base['fresh_item_audit_verified']=True"
    strict3="        expected_claim=de[L]\n        if str(base.get('claim',''))!=str(expected_claim): raise SystemExit(f'Q{n}: evidence claim/rationale binding failure {L}')\n        if str(base.get('direct_or_inference',''))!=('direct' if L==key else 'inference'): raise SystemExit(f'Q{n}: evidence inference classification failure {L}')\n        base['rationale']=exp['key_explanation'] if L==key else de[L]\n        base['fresh_item_audit_verified']=True"
    s=replace_one(s,anchor3,strict3)

    OUT.write_text(s)
    print('GENERATED',OUT.relative_to(REPO),'BLOB',gitblob(OUT),'MANIFEST_BLOB',EXPECTED_MANIFEST_BLOB)

if __name__=='__main__': main()
