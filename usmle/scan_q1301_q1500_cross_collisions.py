#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES=[
ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',
ROOT/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',
ROOT/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',
ROOT/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',
ROOT/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',
ROOT/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',
ROOT/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',
ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json',
ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json']
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def grams(s,n=5):
 w=norm(s).split(); return {tuple(w)} if len(w)<n else {tuple(w[i:i+n]) for i in range(len(w)-n+1)}
def jac(a,b): return len(a&b)/len(a|b) if a|b else 0.0
def txt(d):
 i=d['item']; return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct','')])
def main():
 docs=[]
 for p in FILES:
  b=json.loads(p.read_text()); docs.extend(b['items'])
 docs=sorted(docs,key=lambda x:x['num']); assert [x['num'] for x in docs]==list(range(1301,1501))
 rows=[]
 for i,a in enumerate(docs):
  ga=grams(txt(a)); ta=norm(a['item'].get('tested_construct','')); da=norm(a.get('drug',''))
  for b in docs[:i]:
   gb=grams(txt(b)); tb=norm(b['item'].get('tested_construct','')); db=norm(b.get('drug','')); j=jac(ga,gb)
   reasons=[]
   if ta and ta==tb: reasons.append('EXACT_TESTED_CONSTRUCT')
   if da and da==db: reasons.append('SAME_DRUG')
   if j>=0.45: reasons.append('JACCARD_GE_0.45')
   if reasons:
    rows.append({'q1':b['num'],'q2':a['num'],'drug1':b.get('drug'),'drug2':a.get('drug'),'construct1':b['item'].get('tested_construct'),'construct2':a['item'].get('tested_construct'),'jaccard':round(j,5),'reasons':reasons})
 rows.sort(key=lambda r:(-r['jaccard'],r['q1'],r['q2']))
 out={'scope':'Q1301-Q1500','pair_count':len(rows),'pairs':rows}
 Path('usmle/audit/Q1301_Q1500_CROSS_COLLISION_INVENTORY.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
