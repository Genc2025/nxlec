#!/usr/bin/env python3
import json,os,re,sqlite3,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent; REPO=R.parent; DB=R/'data'/'usmle-step1.db'; OUT=REPO/'usmle/audit/Q0021_Q0323_CONSTRUCT_REVIEW.json'
B=os.environ['DB_BLOB']
def gb():return subprocess.check_output(['git','-C',str(REPO),'hash-object','usmle/data/usmle-step1.db'],text=True).strip()
def q(cid):
 m=re.search(r'DIRECT-(\d{4})',cid);return int(m.group(1)) if m else None
def main():
 assert gb()==B
 c=sqlite3.connect(DB)
 rows=c.execute("select candidate_id,payload_json from step2_final_items").fetchall();c.close()
 out={}
 for cid,pj in rows:
  n=q(cid)
  if n in (21,323):
   p=json.loads(pj);it=p.get('item',{});ex=p.get('explanation',{})
   out[str(n)]={'candidate_id':cid,'blueprint':p.get('blueprint'),'vignette':it.get('vignette'),'lead_in':it.get('lead_in'),'options':it.get('options'),'key':it.get('intended_key'),'tested_construct':it.get('tested_construct'),'key_explanation':ex.get('key_explanation'),'educational_objective':ex.get('educational_objective')}
 assert set(out)=={'21','323'}
 OUT.write_text(json.dumps({'db_blob':B,'items':out},indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
