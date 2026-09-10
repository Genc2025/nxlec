#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3
from pathlib import Path
import author_q1501_q1505_v2 as a
P=Path('usmle/batch_specs_1501_1600/01_q1501_q1505_author_20260910.json'); DB=Path('usmle/data/usmle-step1.db'); OUT=Path('usmle/audit/Q1501_Q1505_CANONICAL_DIAGNOSTIC.json')
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def toks(s): return set(norm(s).split())
def jac(a,b):
 A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0
def text_item(i): return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct','')])
def main():
 a.main(); b=json.loads(P.read_text()); c=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); rows=c.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); c.close()
 canon=[]
 for cid,pj in rows:
  p=json.loads(pj); canon.append((cid,p.get('drug'),p.get('item',{}).get('tested_construct'),text_item(p.get('item',{}))))
 rep=[]
 for x in b['items']:
  t=text_item(x['item']); ss=sorted([(jac(t,ct),cid,drug,tc) for cid,drug,tc,ct in canon],reverse=True)[:5]
  rep.append({'q':x['num'],'drug':x['drug'],'tested_construct':x['item']['tested_construct'],'top_matches':[{'jaccard':round(j,5),'candidate_id':cid,'drug':drug,'tested_construct':tc} for j,cid,drug,tc in ss]})
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps({'canonical_count':len(canon),'reports':rep},indent=2,ensure_ascii=False)+'\n'); print(json.dumps({'reports':rep},ensure_ascii=False))
if __name__=='__main__': main()
