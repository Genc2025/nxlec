#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parent
base=ROOT/'audit_candidate_zero_trust_adaptive.py'
s=base.read_text()
compile(s,str(base)+'[current canonical]','exec')
ns={'__name__':'__main__','__file__':str(Path(__file__).resolve())}
exec(compile(s,str(base)+'[current canonical]','exec'),ns)
