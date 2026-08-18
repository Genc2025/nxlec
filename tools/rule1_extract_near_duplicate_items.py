#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3, subprocess
from pathlib import Path

DB=Path('NCLEX_CANONICAL.db')
EXPECTED='182a1e979e11d62bebc85c5ceb859056b8812963'
OUT=Path('RULE1_CLEANUP_2000_NEAR_DUPLICATE_ITEMS.json')
UIDS=['V2-Q0239','V2-Q1468','V2-Q0679','V2-Q1934','V2-Q1174','V2-Q1176','V2-Q0886','V2-Q1038','V2-Q0653','V2-Q1387']

def main():
    blob=subprocess.check_output(['git','rev-parse','HEAD:NCLEX_CANONICAL.db'],text=True).strip()
    if blob!=EXPECTED: raise SystemExit(f'BLOCKED canonical blob {blob}')
    con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True); con.row_factory=sqlite3.Row
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise SystemExit('BLOCKED integrity')
    items={}
    for uid in UIDS:
        r=con.execute('SELECT * FROM questions WHERE question_uid=?',(uid,)).fetchone()
        if not r: raise SystemExit(f'BLOCKED missing {uid}')
        item=json.loads(r['item_data_json']); ans=json.loads(r['correct_answer_json'])
        items[uid]={
          'question_uid':uid,'stable_sort_key':r['stable_sort_key'],'category_id':r['category_id'],'client_need':r['client_need'],'difficulty':r['difficulty'],'blueprint_topic':r['blueprint_topic'],
          'stem':r['stem'],'options':item.get('options',{}),'correct_option':ans.get('correct_option'),'rationale':r['rationale'],'educational_objective':r['educational_objective'],
          'source_organization':r['source_organization'],'source_document_title':r['source_document_title'],'source_version_date':r['source_version_date'],'source_accessed_date':r['source_accessed_date'],'source_locator':r['source_locator'],'source_url':r['source_url'],'source_claim_supported':r['source_claim_supported'],
          'blueprint_source_organization':r['blueprint_source_organization'],'blueprint_document_title':r['blueprint_document_title'],'blueprint_version':r['blueprint_version'],'blueprint_locator':r['blueprint_locator'],'blueprint_url':r['blueprint_url'],
          'audit_status':r['audit_status'],'second_pass_status':r['second_pass_status']
        }
    con.close()
    OUT.write_text(json.dumps({'status':'READ_ONLY_EXTRACTION','canonical_blob':blob,'items':items},ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_NEAR_DUP_EXTRACT='+json.dumps({'count':len(items),'canonical_blob':blob},separators=(',',':')))
if __name__=='__main__': main()
