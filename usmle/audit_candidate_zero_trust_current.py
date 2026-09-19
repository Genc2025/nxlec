#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parent
base=ROOT/'audit_candidate_zero_trust_adaptive.py'
source=base.read_text()
compile(source,str(base),'exec')
ns={'__name__':'__main__','__file__':str(base)}
exec(compile(source,str(base),'exec'),ns)
