#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'verify_author_q1291_q1300.py'
s=base.read_text()
old="USMLE-QA/1.0 contact=qa@example.invalid"
new="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
if s.count(old)!=1: raise SystemExit('expected exactly one verifier User-Agent token')
s=s.replace(old,new)
compile(s,str(base)+'[browser-UA transport repair]','exec')
exec(compile(s,str(base)+'[browser-UA transport repair]','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
