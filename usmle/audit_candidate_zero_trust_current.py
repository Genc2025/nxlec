#!/usr/bin/env python3
from __future__ import annotations
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'audit_candidate_zero_trust_adaptive.py'
s=base.read_text()
AUDIT_DATE=os.environ.get('AUDIT_DATE','20260910')
s=s.replace('ZERO-TRUST-ADAPTIVE-20260910',f'ZERO-TRUST-ADAPTIVE-{AUDIT_DATE}')
s=s.replace("STOP={'the'", "CANON_COUNT=int(os.environ.get('CANONICAL_COUNT','1500'))\nSTOP={'the'",1)
s=s.replace("b.get('canonical_count_before')==b.get('canonical_count_after')==1300", "b.get('canonical_count_before')==b.get('canonical_count_after')==CANON_COUNT")
s=s.replace("assert len(rows)==rc==1300", "assert len(rows)==rc==CANON_COUNT")
s=s.replace("'canonical_count':1300,'canonical_review_count':1300", "'canonical_count':CANON_COUNT,'canonical_review_count':CANON_COUNT")
for stale in ["==b.get('canonical_count_after')==1300","len(rows)==rc==1300","'canonical_count':1300,'canonical_review_count':1300"]:
    if stale in s: raise SystemExit('stale hard-coded canonical count: '+stale)
compile(s,str(base)+'[current canonical transformed]','exec')
ns={'__name__':'__main__','__file__':str(Path(__file__).resolve())}
exec(compile(s,str(base)+'[current canonical transformed]','exec'),ns)
