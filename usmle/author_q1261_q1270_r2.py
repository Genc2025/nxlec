#!/usr/bin/env python3
from __future__ import annotations
import author_q1261_q1270 as a

_orig_make = a.make

def make_fixed(n,system,comp,path,disc,coverage,vignette,lead,options,key,keyexp,obj,anchor,pubs,fingerprint,steps=4):
    # The source-of-truth calls use coverage as the tested-construct label.
    # Insert it into the legacy helper's explicit `tested` slot so every
    # subsequent argument (rationale, objective, anchor, sources, fingerprint)
    # remains correctly aligned.
    return _orig_make(n,system,comp,path,disc,coverage,vignette,lead,options,key,coverage,keyexp,obj,anchor,pubs,fingerprint,steps)

a.make = make_fixed

if __name__ == '__main__':
    a.main()
