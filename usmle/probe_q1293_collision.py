#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'usmle-step1.db'
ANCHORS=['qualified sign language interpreter','effective communication']

def norm(s):
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',(s or '').casefold()).split())

def material_text(p):
    it=p.get('item',p);k=it.get('intended_key','')
    return ' '.join([it.get('tested_construct',''),it.get('lead_in',''),it.get('options',{}).get(k,'')])
con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();con.close()
out=[]
for cid,pj in rows:
    p=json.loads(pj); mt=norm(material_text(p)); hits=[]
    for a in ANCHORS:
        if norm(a) in mt:hits.append(a)
    if hits:
        it=p.get('item',p); out.append({'candidate_id':cid,'hits':hits,'tested_construct':it.get('tested_construct',''),'lead_in':it.get('lead_in',''),'key':it.get('intended_key',''),'key_option':it.get('options',{}).get(it.get('intended_key',''),'')})
print(json.dumps({'count':len(out),'hits':out},indent=2,ensure_ascii=False))
