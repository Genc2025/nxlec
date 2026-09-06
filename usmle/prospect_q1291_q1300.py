#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1290.json'
PRE_BLOB='8e2f2badc5e1cac3c4dc438cd469c3a05cc7092e'
TERMS=[
 'NURSE statements','Ask-Tell-Ask','teach-back method','qualified medical interpreter','limited English proficiency',
 'substituted judgment','best interest standard','supported decision-making','decision-making capacity','appreciation reasoning choice',
 'medical error disclosure','therapeutic privilege','pediatric assent','shared decision making','informed refusal','health literacy',
 'SOST','sclerostin','sclerosteosis','LRP5','high bone mass','PHEX','FGF23','X-linked hypophosphatemia',
 'IFITM5','osteogenesis imperfecta type V','ACAN','aggrecan','short stature advanced bone age','FLNB','Larsen syndrome',
 'COMP','pseudoachondroplasia','PTH1R','Jansen metaphyseal chondrodysplasia','TNFSF11','RANKL deficiency',
 'TNFRSF11B','osteoprotegerin','juvenile Paget disease','TRPV4','metatropic dysplasia','WNT1','SERPINH1'
]
def gitblob(p):return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def material_text(p):
 d=json.loads(p); i=d.get('item',d); bp=d.get('blueprint',{}); sf=d.get('semantic_fingerprint',{})
 parts=[i.get('tested_construct',''),i.get('lead_in',''),bp.get('coverage_deficit_addressed','')]
 if isinstance(sf,list):parts+=map(str,sf)
 elif isinstance(sf,dict):parts+=map(str,sf.values())
 return ' '.join(parts).casefold()
def full_text(p):return p.casefold()
def main():
 s=json.load(open(STATE)); assert s['final_status']=='FINAL_10_10_PASS' and s['item_count']==1290 and s['step2_final_review_count']==1290 and s['contiguous_q0001_q1290'] is True and s['post_authoritative_db_blob']==PRE_BLOB
 assert gitblob(DB)==PRE_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); con.close(); assert len(rows)==1290
 out={}
 for term in TERMS:
  t=term.casefold(); material=[]; incidental=[]
  for cid,pj in rows:
   if t in material_text(pj):
    d=json.loads(pj); i=d.get('item',d); material.append({'candidate_id':cid,'tested_construct':i.get('tested_construct',''),'lead_in':i.get('lead_in',''),'key':i.get('options',{}).get(i.get('intended_key',''),'')})
   elif t in full_text(pj): incidental.append(cid)
  out[term]={'material_hits':material,'incidental_hit_count':len(incidental),'incidental_examples':incidental[:5]}
 print(json.dumps({'status':'PASS','canonical_count':len(rows),'db_blob':PRE_BLOB,'hits':out},ensure_ascii=False))
if __name__=='__main__':main()
