#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1270.json'
PRE_BLOB='cbfe7c4b469fa49555813cffcc6604d2003dcdac'
TERMS=[
 'KCNQ2','M-current','Kv7.2','ATP1A3','alternating hemiplegia','DNM1','dynamin-1','STXBP1','syntaxin-binding protein 1',
 'CACNA1A','P/Q-type calcium channel','SLC12A5','KCC2','TUBB4A','KCNC1','Kv3.1','PRRT2','paroxysmal kinesigenic dyskinesia',
 'GNAO1','HCN1','hyperpolarization-activated current','teach-back','health literacy','root cause analysis','failure mode and effects analysis',
 'FMEA','SBAR','closed-loop communication','TeamSTEPPS','motivational interviewing','professional interpreter','decision-making capacity',
 'medical error disclosure','I-PASS','shared decision making','two-challenge rule','CUS words','handoff communication'
]
def gitblob(p):return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def main():
 s=json.load(open(STATE)); assert s['final_status']=='FINAL_10_10_PASS' and s['item_count']==1270 and s['step2_final_review_count']==1270 and s['contiguous_q0001_q1270'] is True and s['post_authoritative_db_blob']==PRE_BLOB
 assert gitblob(DB)==PRE_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); con.close(); assert len(rows)==1270
 out={}
 for term in TERMS:
  t=term.casefold(); hits=[]
  for cid,pj in rows:
   if t in pj.casefold():
    p=json.loads(pj); i=p.get('item',p)
    hits.append({'candidate_id':cid,'tested_construct':i.get('tested_construct',''),'lead_in':i.get('lead_in',''),'key':i.get('options',{}).get(i.get('intended_key',''),'')})
  out[term]=hits
 print(json.dumps({'status':'PASS','canonical_count':len(rows),'db_blob':PRE_BLOB,'hits':out},ensure_ascii=False))
if __name__=='__main__':main()
