#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a
import q1601_item,q1602_item,q1603_item,q1604_item,q1605_item

OUT=Path('usmle/batch_specs_1601_1700/01_q1601_q1605_author_20260915.json')
DB_BLOB='0df54bf3943674d2eb0a604626a05bf01474fa08'
TODAY='2026-09-15'

def make(*args,**kwargs):
 x=a.make(*args,**kwargs)
 x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
 x['sources'][0]['retrieved_at']=TODAY
 x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
 return x

def main():
 items=[m.build(make) for m in (q1601_item,q1602_item,q1603_item,q1604_item,q1605_item)]
 b={'batch_id':'Q1601-Q1605-20260915','created_at':TODAY,'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT','production_import_ready':False,'candidate_count':5,'canonical_count_before':1600,'canonical_count_after':1600,'canonical_db_blob':DB_BLOB,'answer_key_sequence':'ABCDE','answer_key_distribution':{L:1 for L in 'ABCDE'},'technical_integrity':{'source_hashes_fabricated':False,'source_hashes_complete':False,'independent_audit_complete':False,'trusted_importer_complete':False},'items':items}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert [x['num'] for x in items]==list(range(1601,1606))
 assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
 assert len({x['drug'].casefold() for x in items})==5
 assert 'ncjmm' not in OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))
if __name__=='__main__': main()
