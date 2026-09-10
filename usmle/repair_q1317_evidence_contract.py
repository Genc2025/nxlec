#!/usr/bin/env python3
import json
from pathlib import Path
p=Path('usmle/batch_specs_1301_1400/02_q1306_q1330_author_20260907.json')
b=json.loads(p.read_text())
xs=[x for x in b['items'] if x['num']==1317]
assert len(xs)==1
x=xs[0]
assert x['item']['intended_key']=='B'
em={e['option']:e for e in x['evidence_map']}
assert set(em)==set('ABCDE')
assert em['B']['direct_or_inference']=='inference'
for L,e in em.items():
    e['direct_or_inference']='direct' if L=='B' else 'inference'
x['author_qa']['unresolved_content_defects']=[]
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
print('Q1317_EVIDENCE_CONTRACT_REPAIRED')
