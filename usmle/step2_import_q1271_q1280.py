#!/usr/bin/env python3
from __future__ import annotations
import os,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
base=ROOT/'step2_import_q1261_q1270.py'
s=base.read_text()
manifest_blob=os.environ.get('Q1271_Q1280_MANIFEST_BLOB','').strip()
if not re.fullmatch(r'[0-9a-f]{40}',manifest_blob): raise SystemExit('Q1271_Q1280_MANIFEST_BLOB must be exact 40-char git blob')
repls=[
("STATE_PRE=ROOT/'state'/'step2_final_q0001_q1260.json'","STATE_PRE=ROOT/'state'/'step2_final_q0001_q1270.json'"),
("STATE_POST=ROOT/'state'/'step2_final_q0001_q1270.json'","STATE_POST=ROOT/'state'/'step2_final_q0001_q1280.json'"),
("MANIFEST=AUD/'Q1261_Q1270_FINAL_QA_PASS.json'","MANIFEST=AUD/'Q1271_Q1280_FINAL_QA_PASS.json'"),
("FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1270.json'","FINAL_AUDIT=AUD/'STEP2_FINAL_10_10_Q0001_Q1280.json'"),
("BATCH=ROOT/'batch_specs_1201_1300'/'09_q1261_q1270_author_20260906.json'","BATCH=ROOT/'batch_specs_1201_1300'/'10_q1271_q1280_author_20260906.json'"),
("NEW_RANGE=range(1261,1271)","NEW_RANGE=range(1271,1281)"),
("EXPECTED_KEYS={1261:'B',1262:'E',1263:'C',1264:'A',1265:'D',1266:'C',1267:'A',1268:'D',1269:'E',1270:'B'}","EXPECTED_KEYS={1271:'C',1272:'E',1273:'A',1274:'D',1275:'B',1276:'A',1277:'D',1278:'C',1279:'B',1280:'E'}"),
("EXPECTED_PRE_COUNT=1260; EXPECTED_POST_COUNT=1270","EXPECTED_PRE_COUNT=1270; EXPECTED_POST_COUNT=1280"),
("EXPECTED_PRE_DB_BLOB='2afb11e1d3490cedc757ecfbe7e4515c6bbd527c'","EXPECTED_PRE_DB_BLOB='cbfe7c4b469fa49555813cffcc6604d2003dcdac'"),
("EXPECTED_BATCH_BLOB='25d7f71b6aa7866e5c5a8f0da7c7c9bc28e309ef'","EXPECTED_BATCH_BLOB='8d4dbeff50a3ec7301a3d915a694645bb007514a'"),
("EXPECTED_MANIFEST_BLOB='61e85d42cb173ee7ee5fc6f413161d7d1a3309e7'",f"EXPECTED_MANIFEST_BLOB='{manifest_blob}'"),
("AUDIT_ID='STEP2-FINAL-Q0001-Q1270-20260906'; CID_SUFFIX='20260906T101000Z'","AUDIT_ID='STEP2-FINAL-Q0001-Q1280-20260906'; CID_SUFFIX='20260906T112500Z'"),
("GI='Gastrointestinal System'; CV='Cardiovascular System'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'","NEURO='Behavioral Health & Nervous Systems/Special Senses'; BLOOD='Blood & Lymphoreticular/Immune Systems'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'"),
("'Behavioral Health, Nervous Systems and Special Senses'","'Behavioral Health, Nervous Systems and Special Senses','Behavioral Health & Nervous Systems/Special Senses'"),
("seq!='BECADCADEB'","seq!='CEADBADCBE'"),
("Counter({GI:5,CV:5})","Counter({NEURO:5,BLOOD:5})"),
("m.get('item_range')!='Q1261-Q1270'","m.get('item_range')!='Q1271-Q1280'"),
("m.get('answer_key_sequence')!='BECADCADEB'","m.get('answer_key_sequence')!='CEADBADCBE'"),
("m.get('system_distribution')!={GI:5,CV:5}","m.get('system_distribution')!={NEURO:5,BLOOD:5}"),
("if bp.get('primary_system') not in {GI,CV}","if bp.get('primary_system') not in {NEURO,BLOOD}"),
("'Q1261-Q1270-FINAL-QA-PASS-Q1260-BOUND-20260906'","'Q1271-Q1280-FINAL-QA-PASS-Q1270-BOUND-20260906'"),
("pre.get('contiguous_q0001_q1260')","pre.get('contiguous_q0001_q1270')"),
("'pre-state Q1260 binding failure'","'pre-state Q1270 binding failure'"),
("inc_bp!=Counter({GI:5,CV:5})","inc_bp!=Counter({NEURO:5,BLOOD:5})"),
("p['blueprint']['primary_system'] not in {GI,CV}","p['blueprint']['primary_system'] not in {NEURO,BLOOD}"),
("!='BECADCADEB'", "!='CEADBADCBE'"),
("'range':'Q1261-Q1270'","'range':'Q1271-Q1280'"),
("'sequence':'BECADCADEB'","'sequence':'CEADBADCBE'"),
("'q1261_q1270_present_exactly_once':True","'q1271_q1280_present_exactly_once':True"),
("'contiguous_q0001_q1270':True","'contiguous_q0001_q1280':True"),
("s['item_count']==1270 and s['step2_final_review_count']==1270 and s['contiguous_q0001_q1270'] is True and s['q1261_q1270_present_exactly_once'] is True","s['item_count']==1280 and s['step2_final_review_count']==1280 and s['contiguous_q0001_q1280'] is True and s['q1271_q1280_present_exactly_once'] is True"),
("'final_count':1270,'reviews':1270","'final_count':1280,'reviews':1280")]
for old,new in repls:
    if old not in s: raise SystemExit('importer transform source token missing: '+old)
    s=s.replace(old,new)
s,n=re.subn(r"\n\s*if n==1266 and \(a\.get\('second_answer_attack'.*?Q1266 repaired adversarial audit binding failure'\)\n","\n",s)
if n!=1: raise SystemExit(f'expected to remove exactly one Q1266 special gate, got {n}')
# Global variable references left from the old GI/CV pair must be gone.
if re.search(r'\bGI\b|\bCV\b',s): raise SystemExit('stale GI/CV variable remains after importer transform')
# Old batch/range/status markers must not survive in executable logic.
for stale in ["Q1261-Q1270","q1261_q1270","BECADCADEB","range(1261,1271)","EXPECTED_PRE_COUNT=1260"]:
    if stale in s: raise SystemExit('stale importer token remains: '+stale)
compile(s,str(base)+'[Q1271-Q1280 transformed]','exec')
ns={'__name__':'__main__','__file__':str(Path(__file__).resolve())}
exec(compile(s,str(base)+'[Q1271-Q1280 transformed]','exec'),ns)
