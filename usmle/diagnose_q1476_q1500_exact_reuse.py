#!/usr/bin/env python3
import json
import author_q1476_q1500 as base

prior={}
covered=[]
for p in base.PRIOR_FILES:
    b=json.loads(p.read_text())
    for x in b.get('items',[]):
        q=x.get('num'); d=str(x.get('drug','')).strip().casefold()
        if isinstance(q,int) and 1301<=q<=1475:
            covered.append(q)
            if d:
                prior.setdefault(d,[]).append(q)
assert len(covered)==175 and set(covered)==set(range(1301,1476))
xs=base.items()
collisions=[]
for x in xs:
    d=x['drug'].strip().casefold()
    if d in prior:
        collisions.append({'candidate_q':x['num'],'drug':x['drug'],'prior_qs':prior[d]})
print(json.dumps({'candidate_count':len(xs),'collisions':collisions,'collision_count':len(collisions)},indent=2))
