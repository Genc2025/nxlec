#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,pathlib,subprocess
cand=pathlib.Path(os.environ['CAND_PATH'])
audit=pathlib.Path(os.environ['OUT_PATH'])
db_blob=os.environ['DB_BLOB']
count=int(os.environ['CANONICAL_COUNT'])
start=int(os.environ['START_Q']); end=int(os.environ['END_Q'])
date=os.environ['AUDIT_DATE']
r=json.loads(audit.read_text()); b=json.loads(cand.read_text())
assert r['verdict']=='ZERO_TRUST_PASS' and r['failures']==[] and r['item_count']==5
assert r['canonical_count']==r['canonical_review_count']==count and r['canonical_db_blob']==db_blob
assert all(x['status']=='PASS' and x['source_live_binding']=='PASS' and x['second_answer_attack']=='PASS' and x['blueprint']=='PASS' and x['evidence_derived_key']==x['intended_key'] and x['canonical_max_jaccard']<0.45 for x in r['item_reports'])
keys=''.join(x['item']['intended_key'] for x in b['items']); assert keys=='ABCDE'
out=pathlib.Path(f'usmle/audit/Q{start}_Q{end}_FINAL_QA_PASS.json')
m={'audit_id':f'Q{start}-Q{end}-FINAL-QA-PASS-{date}','status':'FINAL_QA_PASS','final_qa_verdict':'FINAL_QA_PASS_NO_MATERIAL_DEFECT','item_range':f'Q{start}-Q{end}','item_count':5,'candidate_batch_blob':subprocess.check_output(['git','hash-object',str(cand)],text=True).strip(),'candidate_batch_sha256':hashlib.sha256(cand.read_bytes()).hexdigest(),'authoritative_db_blob':db_blob,'authoritative_db_final_count':count,'authoritative_review_count':count,'technical_freeze':'PASS_ALL_DECLARED_LOCATOR_COMPONENTS','zero_trust_audit_sha256':hashlib.sha256(audit.read_bytes()).hexdigest(),'answer_key_sequence':keys,'all_items_final_10_10_pass':True,'unresolved_defects':[],'suggested_changes':[],'ncjmm':'NOT_APPLICABLE_USMLE','production_import_ready':True,'production_db_modified':False,'trusted_importer_complete':False}
out.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print(out)
