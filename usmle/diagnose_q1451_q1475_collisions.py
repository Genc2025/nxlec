#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import verify_q1451_q1475_preflight as v

ROOT=Path(__file__).resolve().parent
CAND=ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908.json'
TARGETS={1454,1460,1473}

b=json.loads(CAND.read_text())
workstream,_=v.load_workstream()
for x in b['items']:
    if x['num'] not in TARGETS:
        continue
    text=v.item_text(x)
    scores=[]
    for oq,ot in workstream:
        j,s=v.jaccard(text,ot),v.seq(text,ot)
        scores.append((max(j,s),j,s,oq))
    scores.sort(reverse=True)
    print(json.dumps({
        'q':x['num'],
        'drug':x.get('drug'),
        'tested_construct':x['item'].get('tested_construct'),
        'top10':[{'q':oq,'jaccard':round(j,5),'sequence':round(s,5)} for _,j,s,oq in scores[:10]]
    },sort_keys=True))
