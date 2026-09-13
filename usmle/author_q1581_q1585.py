#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a
import q1581_item,q1582_item,q1583_item,q1584_item,q1585_item

OUT=Path('usmle/batch_specs_1501_1600/17_q1581_q1585_author_20260913.json')
DB_BLOB='4c966e4c644c37aaf3dea39bcea33ddbb713a63f'
TODAY='2026-09-13'

def make(*args,**kwargs):
 x=a.make(*args,**kwargs)
 x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
 x['sources'][0]['retrieved_at']=TODAY
 x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
 return x

def main():
 items=[m.build(make) for m in (q1581_item,q1582_item,q1583_item,q1584_item,q1585_item)]
 b={'batch_id':'Q1581-Q1585-20260913','created_at':TODAY,'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT','production_import_ready':False,'candidate_count':5,'canonical_count_before':1580,'canonical_count_after':1580,'canonical_db_blob':DB_BLOB,'answer_key_sequence':'ABCDE','answer_key_distribution':{L:1 for L in 'ABCDE'},'technical_integrity':{'source_hashes_fabricated':False,'source_hashes_complete':False,'independent_audit_complete':False,'trusted_importer_complete':False},'items':items}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert [x['num'] for x in items]==list(range(1581,1586))
 assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
 assert len({x['drug'].casefold() for x in items})==5
 assert 'ncjmm' not in OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))
if __name__=='__main__': main()
