#!/usr/bin/env python3
import json,sqlite3,re,os
from pathlib import Path
DB='usmle/data/usmle-step1.db'
OUT=Path('usmle/audit/Q1631_Q1635_PROSPECT_SCREEN_20260919.json')
pros={
 'FLVCR1_HEME_EXPORT':['FLVCR1','heme exporter','posterior column ataxia','retinitis pigmentosa'],
 'SLC25A3_PHOSPHATE_CARRIER':['SLC25A3','mitochondrial phosphate carrier','phosphate carrier deficiency'],
 'MTFMT_FORMYLATION':['MTFMT','mitochondrial methionyl-tRNA formyltransferase','formylmethionine','mitochondrial translation initiation'],
 'SLC25A32_FAD_TRANSPORT':['SLC25A32','mitochondrial FAD transporter','FAD transport','riboflavin-responsive exercise intolerance'],
 'ATP13A2_POLYAMINE':['ATP13A2','Kufor-Rakeb','lysosomal polyamine','polyamine exporter'],
 'COA6_COPPER_COX':['COA6','cytochrome c oxidase copper','complex IV copper delivery'],
 'TMEM70_ATP_SYNTHASE':['TMEM70','ATP synthase assembly','complex V assembly'],
 'DDHD2_PHOSPHOLIPASE':['DDHD2','intracellular phospholipase A1','lipid droplets','spastic paraplegia 54'],
 'PNKP_DNA_REPAIR':['PNKP','polynucleotide kinase phosphatase','DNA strand break repair','microcephaly seizures'],
 'COASY_COA_SYNTHASE':['COASY','CoA synthase','dephospho-CoA kinase','CoA synthase protein-associated neurodegeneration']
}
c=sqlite3.connect(DB); rows=c.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); c.close()
res={}
for name,terms in pros.items():
 hits=[]
 for cid,pj in rows:
  low=pj.casefold(); mt=[]
  for t in terms:
   tl=t.casefold()
   if re.fullmatch(r'[a-z0-9]+',tl):
    if re.search(r'(?<![a-z0-9])'+re.escape(tl)+r'(?![a-z0-9])',low): mt.append(t)
   elif tl in low: mt.append(t)
  if mt:
   p=json.loads(pj); it=p.get('item',{})
   hits.append({'candidate_id':cid,'matched_terms':mt,'vignette':it.get('vignette'),'lead_in':it.get('lead_in'),'tested_construct':it.get('tested_construct')})
 res[name]={'terms':terms,'hit_count':len(hits),'hits':hits[:20]}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'canonical_db_blob':os.environ['DB_BLOB'],'canonical_count':len(rows),'prospects':res},indent=2,ensure_ascii=False)+'\n')
