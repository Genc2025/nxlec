#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=ROOT/'verify_author_q1291_q1300.py'
s=base.read_text()
# Browser-compatible transport, same as the successful R4 verifier.
old_ua="USMLE-QA/1.0 contact=qa@example.invalid"
new_ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
if s.count(old_ua)!=1: raise SystemExit('expected one base UA token')
s=s.replace(old_ua,new_ua)
# Bind repaired Q1293 construct, not the blocked effective-communication construct.
old="1293:['qualified sign language interpreter','deaf or hard of hearing']"
new="1293:['prisoner representative','45 cfr 46.304']"
if s.count(old)!=1: raise SystemExit('expected one Q1293 anchor token')
s=s.replace(old,new)
# Item-specific federal scope/source guard.
needle="assert Counter(x['blueprint']['primary_system'] for x in items)==Counter({SOC:3,MSK:7});assert Counter(x['blueprint']['primary_competency'] for x in items)==Counter({COMM:3,MK:5,DX:2})"
insert=needle+"\n q1293=items[2]; assert q1293['num']==1293 and 'HHS-supported' in q1293['item']['vignette'] and '45 CFR part 46, subpart C' in q1293['item']['vignette']; assert q1293['item']['intended_key']=='D'; assert 'prisoner representative' in q1293['item']['options']['D'].casefold(); assert any(src['url']=='https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-C/section-46.304' for src in q1293['sources']); assert all('ada.gov' not in src['url'] for src in q1293['sources'])"
if s.count(needle)!=1: raise SystemExit('distribution guard token missing')
s=s.replace(needle,insert)
# Strengthen live government-page verification: a nominal HTTP 200 is insufficient.
# Retry the whole semantic binding so transient WAF/render responses cannot be mistaken for source verification.
old_loop=""" for sid,url,title,passage in official_web:\n  txt=htmltext(fetch_retry(url)); tt=set(toks(title)); pt=set(toks(passage)); actual=set(toks(txt))\n  assert len(tt&actual)>=max(2,min(5,len(tt)//2)),(sid,'title binding',tt&actual)\n  assert len(pt&actual)>=max(4,min(8,len(pt)//3)),(sid,'support binding',pt&actual)\n"""
new_loop=""" for sid,url,title,passage in official_web:\n  tt=set(toks(title)); pt=set(toks(passage)); last=(set(),set(),0)\n  bound=False\n  for semantic_attempt in range(6):\n   txt=htmltext(fetch_retry(url)); actual=set(toks(txt)); th=tt&actual; ph=pt&actual; last=(th,ph,len(txt))\n   title_need=max(2,min(5,len(tt)//2)); support_need=max(4,min(8,len(pt)//3))\n   if len(th)>=title_need and len(ph)>=support_need:\n    bound=True;break\n   time.sleep(min(8,1+semantic_attempt))\n  assert bound,(sid,'authoritative live semantic binding failed after retries',{'title_hits':sorted(last[0]),'support_hits':sorted(last[1]),'text_len':last[2]})\n"""
if s.count(old_loop)!=1: raise SystemExit('government live-binding loop token missing')
s=s.replace(old_loop,new_loop)
compile(s,str(base)+'[R5 semantic-response retry + Q1293 repair]','exec')
exec(compile(s,str(base)+'[R5 semantic-response retry + Q1293 repair]','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
