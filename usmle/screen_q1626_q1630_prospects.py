#!/usr/bin/env python3
import json,sqlite3,re,os
from pathlib import Path

DB=Path('usmle/data/usmle-step1.db')
OUT=Path('usmle/audit/Q1626_Q1630_PROSPECT_SCREEN_20260919.json')
PROSPECTS={
 'LIPT1_LIPOYLTRANSFERASE':['LIPT1','lipoyltransferase','lipoylation defect','lipoic acid transfer'],
 'SERAC1_PHOSPHATIDYLGLYCEROL':['SERAC1','MEGDEL','phosphatidylglycerol remodeling','3-methylglutaconic aciduria'],
 'PMPCA_MPP':['PMPCA','mitochondrial processing peptidase','presequence processing','MEGCANN'],
 'GNE_SIALIC_ACID':['GNE','UDP-N-acetylglucosamine 2-epimerase','N-acetylmannosamine kinase','sialic acid biosynthesis'],
 'SLC30A10_MN_EFFLUX':['SLC30A10','manganese efflux','hypermanganesemia','polycythemia dystonia'],
 'PGM3_UDP_GLCNAC':['PGM3','phosphoglucomutase 3','UDP-GlcNAc','immunodeficiency glycosylation'],
 'LRPPRC_MRNA_STABILITY':['LRPPRC','Leigh syndrome French Canadian','mitochondrial mRNA stability'],
 'SLC25A32_FAD':['SLC25A32','mitochondrial FAD transporter','FAD transport','riboflavin-responsive'],
 'COA6_COPPER_COX':['COA6','cytochrome c oxidase copper','complex IV copper'],
 'SLC25A42_COA_TRANSPORT':['SLC25A42','mitochondrial coenzyme A transporter','CoA transporter']
}

def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 return int(m.group(1)) if m else None

c=sqlite3.connect(DB)
rows=c.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
c.close()
res={}
for name,terms in PROSPECTS.items():
 hits=[]
 for cid,pj in rows:
  low=pj.casefold()
  mt=[t for t in terms if t.casefold() in low]
  if mt:
   p=json.loads(pj); it=p.get('item',{})
   hits.append({'candidate_id':cid,'q':qnum(cid),'matched_terms':mt,'vignette':it.get('vignette'),'lead_in':it.get('lead_in'),'tested_construct':it.get('tested_construct')})
 res[name]={'terms':terms,'hit_count':len(hits),'hits':hits[:20]}
out={'canonical_db_blob':os.environ.get('DB_BLOB'),'canonical_count':len(rows),'prospects':res}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v['hit_count'] for k,v in res.items()},sort_keys=True))
