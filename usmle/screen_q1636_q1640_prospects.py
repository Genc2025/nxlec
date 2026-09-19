#!/usr/bin/env python3
import json,sqlite3,re,os
from pathlib import Path
DB=Path('usmle/data/usmle-step1.db')
OUT=Path('usmle/audit/Q1636_Q1640_PROSPECT_SCREEN_20260919.json')
PROSPECTS={
 'HGSNAT_MPSIIIC':['HGSNAT','heparan-alpha-glucosaminide N-acetyltransferase','Sanfilippo type C'],
 'SLC25A42_MITO_COA':['SLC25A42','mitochondrial coenzyme A transporter','mitochondrial CoA transport'],
 'COA6_COPPER_COX':['COA6','cytochrome c oxidase copper delivery','COX copper assembly'],
 'SLC25A32_MITO_FAD':['SLC25A32','mitochondrial FAD transporter','mitochondrial FAD transport'],
 'SLC13A5_CITRATE':['SLC13A5','sodium citrate cotransporter','developmental epileptic encephalopathy citrate'],
 'LONP1_PROTEOSTASIS':['LONP1','mitochondrial matrix protease','CODAS syndrome'],
 'FLVCR1_HEME':['FLVCR1','heme exporter','posterior column ataxia retinitis pigmentosa'],
 'PISD_PE':['PISD','phosphatidylserine decarboxylase','mitochondrial phosphatidylethanolamine'],
 'ABCB7_FE_S_EXPORT':['ABCB7','mitochondrial iron-sulfur','sideroblastic anemia ataxia'],
 'MPDU1_GLYCOSYLATION':['MPDU1','dolichol-phosphate-mannose utilization','congenital disorder glycosylation MPDU1']
}

def match(text,term):
 t=term.casefold()
 if re.fullmatch(r'[a-z0-9]+',t) and len(t)<=10:
  return re.search(r'(?<![a-z0-9])'+re.escape(t)+r'(?![a-z0-9])',text) is not None
 return t in text

c=sqlite3.connect(DB)
rows=c.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
c.close()
res={}
for name,terms in PROSPECTS.items():
 hits=[]
 for cid,pj in rows:
  low=pj.casefold()
  mt=[t for t in terms if match(low,t)]
  if mt:
   p=json.loads(pj); it=p.get('item',{})
   hits.append({'candidate_id':cid,'matched_terms':mt,'vignette':it.get('vignette'),'lead_in':it.get('lead_in'),'tested_construct':it.get('tested_construct')})
 res[name]={'terms':terms,'hit_count':len(hits),'hits':hits[:20]}
out={'canonical_db_blob':os.environ.get('DB_BLOB'),'canonical_count':len(rows),'prospects':res}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v['hit_count'] for k,v in res.items()},sort_keys=True))
