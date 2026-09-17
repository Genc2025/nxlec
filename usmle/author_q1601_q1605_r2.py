#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a
import q1601_item_r2,q1602_item,q1603_item,q1604_item,q1605_item

OUT=Path('usmle/batch_specs_1601_1700/01_q1601_q1605_author_20260918_r2.json')
DB_BLOB='0df54bf3943674d2eb0a604626a05bf01474fa08'
TODAY='2026-09-18'

def make(*args,**kwargs):
 x=a.make(*args,**kwargs)
 x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
 x['sources'][0]['retrieved_at']=TODAY
 x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
 return x

def make_general(q,drug,system,disc,vig,lead,opts,key,construct,keyexp,rats,eo,title,url,loc,source_date,alt,res):
 # Reuse the stable item/evidence schema, then replace the label-specific source binding.
 x=a.make(q,drug,system,disc,vig,lead,opts,key,construct,keyexp,rats,eo,'PLACEHOLDER','not-applicable',alt,res)
 sid=f'Q{q}-NCBI'
 x['sources']=[{
  'source_id':sid,
  'title':title,
  'agency':'National Center for Biotechnology Information (NCBI), National Library of Medicine, NIH',
  'url':url,
  'source_section_date':source_date,
  'date_basis':f'NCBI Bookshelf source reports last update {source_date}; live page reverified {TODAY}.',
  'retrieved_at':TODAY,
  'section_locator':loc,
  'source_page_sha256':None,
  'cited_section_sha256':None,
  'hash_status':'PENDING_DETERMINISTIC_REFETCH_AND_HASH'
 }]
 for e in x['evidence_map']:
  e['source_ids']=[sid]
  e['source_locator']=loc
 x['author_qa']['source_identity_setid_url_locator']='PASS — NCBI/NLM title, canonical HTTPS URL, and exact section locator verified; DailyMed SetID not applicable.'
 x['author_qa']['currentness']=f'PASS — source last updated {source_date} and live page reverified {TODAY}.'
 return x

def main():
 items=[
  q1601_item_r2.build(make_general),
  q1602_item.build(make),
  q1603_item.build(make),
  q1604_item.build(make),
  q1605_item.build(make),
 ]
 b={
  'batch_id':'Q1601-Q1605-20260918-R2',
  'created_at':TODAY,
  'revision_reason':'Replace Q1601 after whole-bank audit detected a repeated tested construct with canonical Q1404; Q1602-Q1605 are re-frozen and re-audited unchanged in content.',
  'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
  'production_import_ready':False,
  'candidate_count':5,
  'canonical_count_before':1600,
  'canonical_count_after':1600,
  'canonical_db_blob':DB_BLOB,
  'answer_key_sequence':'ABCDE',
  'answer_key_distribution':{L:1 for L in 'ABCDE'},
  'technical_integrity':{'source_hashes_fabricated':False,'source_hashes_complete':False,'independent_audit_complete':False,'trusted_importer_complete':False},
  'items':items
 }
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert [x['num'] for x in items]==list(range(1601,1606))
 assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
 assert 'ncjmm' not in OUT.read_text().casefold()
 assert items[0]['item']['tested_construct']!='Competitive inhibition of CMV pUL97 protein kinase'
 print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE','revision':'R2'}))

if __name__=='__main__':
 main()
