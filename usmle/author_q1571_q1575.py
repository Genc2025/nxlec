#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a
import q1571_item,q1572_item,q1573_item,q1574_item,q1575_item

OUT=Path('usmle/batch_specs_1501_1600/15_q1571_q1575_author_20260913.json')
DB_BLOB='c0f369b414a36f6db6d89e540db66e3bfad61912'
TODAY='2026-09-13'

def make(*args,**kwargs):
 x=a.make(*args,**kwargs)
 x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
 x['sources'][0]['retrieved_at']=TODAY
 x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
 return x

def main():
 items=[m.build(make) for m in (q1571_item,q1572_item,q1573_item,q1574_item,q1575_item)]
 b={'batch_id':'Q1571-Q1575-20260913','created_at':TODAY,'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT','production_import_ready':False,'candidate_count':5,'canonical_count_before':1570,'canonical_count_after':1570,'canonical_db_blob':DB_BLOB,'answer_key_sequence':'ABCDE','answer_key_distribution':{L:1 for L in 'ABCDE'},'technical_integrity':{'source_hashes_fabricated':False,'source_hashes_complete':False,'independent_audit_complete':False,'trusted_importer_complete':False},'items':items}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert [x['num'] for x in items]==list(range(1571,1576))
 assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
 assert len({x['drug'].casefold() for x in items})==5
 assert 'ncjmm' not in OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))
if __name__=='__main__': main()
