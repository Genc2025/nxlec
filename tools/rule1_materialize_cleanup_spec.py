#!/usr/bin/env python3
import base64, json, lzma
from pathlib import Path
PARTS=[Path(f'RULE1_CLEANUP_2000_SPEC.part{i}') for i in range(1,5)]
OUT=Path('RULE1_CLEANUP_2000_CORRECTIONS.json')
packed=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
spec=json.loads(lzma.decompress(base64.b64decode(packed)).decode('utf-8'))
sem={}
for row in spec['cueing']:
    uid,a,b,c,d,correct=row
    v={'options':{'A':a,'B':b,'C':c,'D':d}}
    if correct is not None:
        v['correct_option']=correct
    sem[uid]=v
for uid,v in spec['rich'].items():
    if uid in sem:
        sem[uid].update(v)
    else:
        sem[uid]=v
uids=sorted(sem)
config={
    'cleanup_scope':'V2-Q0001–V2-Q2000 standalone bank-level cleanup',
    'input_canonical_blob':'182a1e979e11d62bebc85c5ceb859056b8812963',
    'semantic_corrections':sem,
    'required_semantic_review_uids':uids,
    'semantic_reviewed_uids':uids,
}
OUT.write_text(json.dumps(config,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps({'materialized':str(OUT),'semantic_correction_count':len(uids)},sort_keys=True))
