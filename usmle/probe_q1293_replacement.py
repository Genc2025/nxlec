#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'usmle-step1.db'
ANCHORS=[
 'prisoner representative','prisoner research','45 cfr 46.304',
 'therapeutic misconception','certificate of confidentiality','medical error disclosure',
 'conflict of interest','informed refusal','genetic discrimination','ginaa','incidental findings'
]
def norm(s):return ' '.join(re.sub(r'[^a-z0-9]+',' ',(s or '').casefold()).split())
def material_text(p):
 it=p.get('item',p);k=it.get('intended_key','')
 return ' '.join([it.get('tested_construct',''),it.get('lead_in',''),it.get('options',{}).get(k,'')])
con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();con.close()
res={a:[] for a in ANCHORS}
for cid,pj in rows:
 p=json.loads(pj);mt=norm(material_text(p));it=p.get('item',p)
 for a in ANCHORS:
  if norm(a) in mt:
   res[a].append({'candidate_id':cid,'tested_construct':it.get('tested_construct',''),'lead_in':it.get('lead_in',''),'key_option':it.get('options',{}).get(it.get('intended_key',''),'')})
print(json.dumps({'counts':{a:len(v) for a,v in res.items()},'hits':res},indent=2,ensure_ascii=False))
