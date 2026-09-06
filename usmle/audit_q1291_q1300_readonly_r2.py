#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'audit_q1291_q1300_readonly.py'
s=base.read_text()
repls=[
("1293:['qualified sign language interpreter','effective communication']","1293:['prisoner representative','45 cfr 46.304']"),
("1293:('A','An accompanying adult may sometimes assist with communication under narrow ADA circumstances, but conversational ASL does not establish qualification for a complex procedural consent. The patient requests ASL interpretation and the interaction is lengthy, technical, and bidirectional, making an appropriate qualified interpreter or equally effective auxiliary aid the defensible answer.'),","1293:('E','Option E is the strongest alternative because independence from the prison is also regulated, but 45 CFR 46.304 requires only a majority of the Board, exclusive of prisoner members, to have no prison association. The stem explicitly says that majority requirement is already satisfied; the missing mandatory element is at least one prisoner or appropriately experienced prisoner representative.'),"),
("if q==1293 and not all(t in norm(it['vignette']) for t in ['deaf','american sign language','requests an asl interpreter']):fail.append('communication_scope_hidden_assumption')","if q==1293 and not all(t in norm(it['vignette']) for t in ['hhs supported','prisoner representative','45 cfr part 46 subpart c']):fail.append('federal_scope_hidden_assumption')")
]
for old,new in repls:
    if s.count(old)!=1: raise SystemExit('audit R2 replacement token count != 1: '+old[:100])
    s=s.replace(old,new)
for stale in ['qualified sign language interpreter','american sign language','requests an asl interpreter']:
    if stale in s: raise SystemExit('stale Q1293 audit token remains: '+stale)
compile(s,str(base)+'[Q1293 prisoner-research replacement audit]','exec')
exec(compile(s,str(base)+'[Q1293 prisoner-research replacement audit]','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
