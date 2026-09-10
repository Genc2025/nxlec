#!/usr/bin/env python3
from __future__ import annotations
import simulate_import_q1301_q1500 as s

a,b,bp,mp,_=s.BATCHES[3]
assert (a,b)==(1356,1380)
s.BATCHES[3]=(a,b,bp,mp,'5545d82cc8e4f07a80702d95ef3bcffd4a78a361')

if __name__=='__main__':
    s.main()
