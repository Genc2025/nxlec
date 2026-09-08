#!/usr/bin/env python3
from __future__ import annotations
import json
import author_q1476_q1500 as base

def prior_drugs_allow_historical_duplicates():
    out={}
    covered=[]
    duplicate_history={}
    for p in base.PRIOR_FILES:
        b=json.loads(p.read_text())
        for x in b.get('items',[]):
            q=x.get('num'); d=str(x.get('drug','')).strip().casefold()
            if isinstance(q,int) and 1301<=q<=1475:
                covered.append(q)
                if d:
                    if d in out:
                        prev=out[d]
                        duplicate_history.setdefault(d,[prev] if isinstance(prev,int) else list(prev))
                        duplicate_history[d].append(q)
                        out[d]=duplicate_history[d]
                    else:
                        out[d]=q
    if len(covered)!=175 or set(covered)!=set(range(1301,1476)):
        raise SystemExit(f'prior workstream coverage failure: count={len(covered)} unique={len(set(covered))}')
    # Exact-new-drug gate uses membership in all historical drug names regardless of historical duplicates.
    return out

base.prior_drugs=prior_drugs_allow_historical_duplicates
base.main()
