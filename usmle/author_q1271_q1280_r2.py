#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

p=Path(__file__).resolve().parent/'author_q1271_q1280.py'
s=p.read_text()
pattern=r",disc=(\[[^\n]+?\]),'([^'\n]+)',\n(\s+)vignette="
repl=r",disc=\1,coverage='\2',\n\3vignette="
fixed,count=re.subn(pattern,repl,s)
if count!=10: raise SystemExit(f'expected 10 coverage-binding repairs, got {count}')
compile(fixed,str(p)+'[repaired]','exec')
ns={'__name__':'__main__','__file__':str(p)}
exec(compile(fixed,str(p)+'[repaired]','exec'),ns)
