#!/usr/bin/env python3
import json,sqlite3,re,os
from pathlib import Path
DB='usmle/data/usmle-step1.db'
OUT=Path('usmle/audit/Q1627_REPLACEMENT_PROSPECT_SCREEN_20260919.json')
pros={
 'MRAP_MC2R':['MRAP','melanocortin 2 receptor accessory protein','MC2R trafficking','ACTH receptor trafficking'],
 'SEC23B_COPII':['SEC23B','COPII','ER-to-Golgi transport','congenital dyserythropoietic anemia type II'],
 'PCSK1_PROHORMONE':['PCSK1','prohormone convertase 1/3','proinsulin processing','prohormone processing'],
 'RAB27A_GRANULE':['RAB27A','Griscelli syndrome','cytotoxic granule exocytosis','melanosome transport'],
 'ATP6V0A2_GOLGI_PH':['ATP6V0A2','Golgi acidification','cutis laxa type II','V-ATPase']
}
c=sqlite3.connect(DB); rows=c.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); c.close()
res={}
for name,terms in pros.items():
 hits=[]
 for cid,pj in rows:
  low=pj.casefold()
  mt=[]
  for t in terms:
   tl=t.casefold()
   if re.fullmatch(r'[a-z0-9]+',tl):
    if re.search(r'(?<![a-z0-9])'+re.escape(tl)+r'(?![a-z0-9])',low): mt.append(t)
   elif tl in low: mt.append(t)
  if mt:
   p=json.loads(pj); it=p.get('item',{})
   hits.append({'candidate_id':cid,'matched_terms':mt,'vignette':it.get('vignette'),'tested_construct':it.get('tested_construct')})
 res[name]={'terms':terms,'hit_count':len(hits),'hits':hits[:15]}
OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps({'canonical_db_blob':os.environ['DB_BLOB'],'canonical_count':len(rows),'prospects':res},indent=2,ensure_ascii=False)+'\n')
