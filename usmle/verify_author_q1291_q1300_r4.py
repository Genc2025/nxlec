#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'verify_author_q1291_q1300.py'
s=base.read_text()
old_ua="USMLE-QA/1.0 contact=qa@example.invalid"
new_ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
if s.count(old_ua)!=1: raise SystemExit('expected exactly one verifier User-Agent token')
s=s.replace(old_ua,new_ua)
old="1293:['qualified sign language interpreter','deaf or hard of hearing']"
new="1293:['prisoner representative','45 cfr 46.304']"
if s.count(old)!=1: raise SystemExit('expected exactly one Q1293 anchor token')
s=s.replace(old,new)
# Add an item-specific scope/source guard after the batch-level distribution checks.
needle="assert Counter(x['blueprint']['primary_system'] for x in items)==Counter({SOC:3,MSK:7});assert Counter(x['blueprint']['primary_competency'] for x in items)==Counter({COMM:3,MK:5,DX:2})"
insert=needle+"\n q1293=items[2]; assert q1293['num']==1293 and 'HHS-supported' in q1293['item']['vignette'] and '45 CFR part 46, subpart C' in q1293['item']['vignette']; assert q1293['item']['intended_key']=='D'; assert 'prisoner representative' in q1293['item']['options']['D'].casefold(); assert any(src['url']=='https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-C/section-46.304' for src in q1293['sources']); assert all('ada.gov' not in src['url'] for src in q1293['sources'])"
if s.count(needle)!=1: raise SystemExit('batch distribution verifier token missing')
s=s.replace(needle,insert)
compile(s,str(base)+'[Q1293 replacement + browser-UA verification]','exec')
exec(compile(s,str(base)+'[Q1293 replacement + browser-UA verification]','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
