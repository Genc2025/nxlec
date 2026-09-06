#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'finalize_q1271_q1280_qa.py'
s=base.read_text()
repls=[
("10_q1271_q1280_author_20260906.json","11_q1281_q1290_author_20260906.json"),
("Q1271_Q1280_READONLY_AUDIT.json","Q1281_Q1290_READONLY_AUDIT.json"),
("Q1271_Q1280_FINAL_QA_PASS.json","Q1281_Q1290_FINAL_QA_PASS.json"),
("cbfe7c4b469fa49555813cffcc6604d2003dcdac","c6d3a9df9c8887b6ff3f3dbac6c710ed564bb4ed"),
("8d4dbeff50a3ec7301a3d915a694645bb007514a","fdda09072509425b0321aafbe921aa95fed53aee"),
("ro['canonical_count']==ro['canonical_review_count']==1270","ro['canonical_count']==ro['canonical_review_count']==1280"),
("set(range(1271,1281))","set(range(1281,1291))"),
("for n in range(1271,1281):","for n in range(1281,1291):"),
("'authoritative_db_final_count':1270","'authoritative_db_final_count':1280"),
("Q1271-Q1280-FINAL-QA-PASS-Q1270-BOUND-20260906","Q1281-Q1290-FINAL-QA-PASS-Q1280-BOUND-20260906"),
("Q1271-Q1280","Q1281-Q1290"),
("CEADBADCBE","BDACECAEDB"),
("'Behavioral Health & Nervous Systems/Special Senses':5,'Blood & Lymphoreticular/Immune Systems':5","'Reproductive & Endocrine Systems':5,'Respiratory & Renal/Urinary Systems':5")]
for old,new in repls:
    if old not in s:raise SystemExit('FINAL transform source token missing: '+old)
    s=s.replace(old,new)
for stale in ['Q1271_Q1280','10_q1271_q1280','CEADBADCBE','set(range(1271,1281))']:
    if stale in s:raise SystemExit('stale FINAL token remains: '+stale)
compile(s,str(base)+'[Q1281-Q1290 transformed]','exec')
exec(compile(s,str(base)+'[Q1281-Q1290 transformed]','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
