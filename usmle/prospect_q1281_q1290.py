#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1280.json'
PRE_BLOB='c6d3a9df9c8887b6ff3f3dbac6c710ed564bb4ed'
TERMS=[
 'PCSK1','prohormone convertase 1/3','IGSF1','macroorchidism','NR0B1','DAX1','adrenal hypoplasia congenita',
 'POR deficiency','P450 oxidoreductase deficiency','Antley-Bixler','THRB','resistance to thyroid hormone beta',
 'MAGED2','transient antenatal Bartter','SLC4A4','NBCe1','proximal renal tubular acidosis',
 'SLC22A12','URAT1','renal hypouricemia','INF2','Charcot-Marie-Tooth','focal segmental glomerulosclerosis',
 'CA2 deficiency','carbonic anhydrase II deficiency','osteopetrosis renal tubular acidosis cerebral calcification',
 'KISS1R','GNRHR','hypogonadotropic hypogonadism','SECISBP2','selenocysteine insertion sequence-binding protein 2',
 'TRPC6','DGKE','atypical hemolytic uremic syndrome','COQ8B','ADCK4','LAMB2','Pierson syndrome',
 'MC2R','melanocortin 2 receptor','MRAP','familial glucocorticoid deficiency','HSD3B2','3 beta hydroxysteroid dehydrogenase type 2',
 'CYP11A1','cholesterol side-chain cleavage','STAR','steroidogenic acute regulatory protein','TSHR','familial nonautoimmune hyperthyroidism'
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
 s=json.load(open(STATE)); assert s['final_status']=='FINAL_10_10_PASS' and s['item_count']==1280 and s['step2_final_review_count']==1280 and s['contiguous_q0001_q1280'] is True and s['post_authoritative_db_blob']==PRE_BLOB
 assert gitblob(DB)==PRE_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); con.close(); assert len(rows)==1280
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
