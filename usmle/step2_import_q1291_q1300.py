#!/usr/bin/env python3
from __future__ import annotations
import os,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
base=ROOT/'step2_import_q1261_q1270.py'
s=base.read_text()
manifest_blob=os.environ.get('Q1291_Q1300_MANIFEST_BLOB','').strip()
if not re.fullmatch(r'[0-9a-f]{40}',manifest_blob): raise SystemExit('Q1291_Q1300_MANIFEST_BLOB must be exact 40-char git blob')
repls=[
("STATE_PRE=ROOT/'state'/'step2_final_q0001_q1260.json'","STATE_PRE=ROOT/'state'/'step2_final_q0001_q1290.json'"),
("STATE_POST=ROOT/'state'/'step2_final_q0001_q1270.json'","STATE_POST=ROOT/'state'/'step2_final_q0001_q1300.json'"),
("MANIFEST=AUD/'Q1261_Q1270_FINAL_QA_PASS.json'","MANIFEST=AUD/'Q1291_Q1300_FINAL_QA_PASS.json'"),
("FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1270.json'","FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1300.json'"),
("BATCH=ROOT/'batch_specs_1201_1300'/'09_q1261_q1270_author_20260906.json'","BATCH=ROOT/'batch_specs_1201_1300'/'12_q1291_q1300_author_20260906.json'"),
("NEW_RANGE=range(1261,1271)","NEW_RANGE=range(1291,1301)"),
("EXPECTED_KEYS={1261:'B',1262:'E',1263:'C',1264:'A',1265:'D',1266:'C',1267:'A',1268:'D',1269:'E',1270:'B'}","EXPECTED_KEYS={1291:'C',1292:'A',1293:'D',1294:'B',1295:'E',1296:'B',1297:'D',1298:'A',1299:'C',1300:'E'}"),
("EXPECTED_PRE_COUNT=1260; EXPECTED_POST_COUNT=1270","EXPECTED_PRE_COUNT=1290; EXPECTED_POST_COUNT=1300"),
("EXPECTED_PRE_DB_BLOB='2afb11e1d3490cedc757ecfbe7e4515c6bbd527c'","EXPECTED_PRE_DB_BLOB='8e2f2badc5e1cac3c4dc438cd469c3a05cc7092e'"),
("EXPECTED_BATCH_BLOB='25d7f71b6aa7866e5c5a8f0da7c7c9bc28e309ef'","EXPECTED_BATCH_BLOB='a9ae65f1508891a804c500f26ce3a7ea4e767a16'"),
("EXPECTED_MANIFEST_BLOB='61e85d42cb173ee7ee5fc6f413161d7d1a3309e7'",f"EXPECTED_MANIFEST_BLOB='{manifest_blob}'"),
("AUDIT_ID='STEP2-FINAL-Q0001-Q1270-20260906'; CID_SUFFIX='20260906T101000Z'","AUDIT_ID='STEP2-FINAL-Q0001-Q1300-20260906'; CID_SUFFIX='20260906T185316Z'"),
("GI='Gastrointestinal System'; CV='Cardiovascular System'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'","SOC='Social Sciences: Communication and Interpersonal Skills'; MSK='Musculoskeletal, Skin & Subcutaneous Tissue'; COMM='Communication and Interpersonal Skills'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'"),
("'Behavioral Health, Nervous Systems and Special Senses'","'Behavioral Health, Nervous Systems and Special Senses','Behavioral Health & Nervous Systems/Special Senses'"),
("seq!='BECADCADEB'","seq!='CADBEBDACE'"),
("Counter({GI:5,CV:5})","Counter({SOC:3,MSK:7})"),
("Counter({DX:5,MK:5})","Counter({COMM:3,MK:5,DX:2})"),
("m.get('candidate_batch_blob')!=EXPECTED_BATCH_BLOB or m.get('candidate_batch_object_sha256')!=hobj(json.loads(BATCH.read_text()))","m.get('candidate_batch_blob')!=EXPECTED_BATCH_BLOB or m.get('candidate_batch_object_sha256')!=hashlib.sha256(BATCH.read_bytes()).hexdigest()"),
("if hobj(a)!=ref.get('audit_object_sha256')","if hashlib.sha256(ap.read_bytes()).hexdigest()!=ref.get('audit_object_sha256')"),
("m.get('item_range')!='Q1261-Q1270'","m.get('item_range')!='Q1291-Q1300'"),
("m.get('answer_key_sequence')!='BECADCADEB'","m.get('answer_key_sequence')!='CADBEBDACE'"),
("m.get('system_distribution')!={GI:5,CV:5}","m.get('system_distribution')!={SOC:3,MSK:7}"),
("m.get('competency_distribution')!={DX:5,MK:5}","m.get('competency_distribution')!={COMM:3,MK:5,DX:2}"),
("if bp.get('primary_system') not in {GI,CV}","if bp.get('primary_system') not in {SOC,MSK}"),
("bp.get('primary_competency') not in {DX,MK}","bp.get('primary_competency') not in {COMM,MK,DX}"),
("'Q1261-Q1270-FINAL-QA-PASS-Q1260-BOUND-20260906'","'Q1291-Q1300-FINAL-QA-PASS-Q1290-BOUND-20260906'"),
("pre.get('contiguous_q0001_q1260')","pre.get('contiguous_q0001_q1290')"),
("'pre-state Q1260 binding failure'","'pre-state Q1290 binding failure'"),
("p['blueprint']['primary_system'] not in {GI,CV}","p['blueprint']['primary_system'] not in {SOC,MSK}"),
("p['blueprint']['primary_competency'] not in {DX,MK}","p['blueprint']['primary_competency'] not in {COMM,MK,DX}"),
("!='BECADCADEB'","!='CADBEBDACE'"),
("'range':'Q1261-Q1270'","'range':'Q1291-Q1300'"),
("'sequence':'BECADCADEB'","'sequence':'CADBEBDACE'"),
("'q1261_q1270_present_exactly_once':True","'q1291_q1300_present_exactly_once':True"),
("'contiguous_q0001_q1270':True","'contiguous_q0001_q1300':True"),
("s['item_count']==1270 and s['step2_final_review_count']==1270 and s['contiguous_q0001_q1270'] is True and s['q1261_q1270_present_exactly_once'] is True","s['item_count']==1300 and s['step2_final_review_count']==1300 and s['contiguous_q0001_q1300'] is True and s['q1291_q1300_present_exactly_once'] is True"),
("'final_count':1270,'reviews':1270","'final_count':1300,'reviews':1300")]
for old,new in repls:
    if old not in s: raise SystemExit('importer transform source token missing: '+old)
    s=s.replace(old,new)
s,n=re.subn(r"\n\s*if n==1266 and \(a\.get\('second_answer_attack'.*?Q1266 repaired adversarial audit binding failure'\)\n","\n",s)
if n!=1: raise SystemExit(f'expected to remove exactly one Q1266 special gate, got {n}')
if re.search(r'\bGI\b|\bCV\b',s): raise SystemExit('stale GI/CV variable remains after importer transform')
for stale in ["Q1261-Q1270","q1261_q1270","BECADCADEB","range(1261,1271)","EXPECTED_PRE_COUNT=1260","{GI,CV}","{DX,MK}"]:
    if stale in s: raise SystemExit('stale importer token remains: '+stale)
compile(s,str(base)+'[Q1291-Q1300 transformed]','exec')
ns={'__name__':'__main__','__file__':str(Path(__file__).resolve())}
exec(compile(s,str(base)+'[Q1291-Q1300 transformed]','exec'),ns)
