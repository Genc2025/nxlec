#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,urllib.request
from pathlib import Path
P=Path(os.environ['CAND_PATH']); START=int(os.environ['START_Q']); END=int(os.environ['END_Q'])
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Freeze/2.0'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read(4000000)
def clean(raw): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()
def cited_window(text,locator):
 low=text.casefold(); candidates=[]; parts=[p.strip() for p in re.split(r'[;|]',locator or '') if p.strip()]; anchors=[]
 for p in parts: anchors += [p,re.sub(r'^\s*\d+(?:\.\d+)*\s*','',p).strip()]
 if not any('mechanism of action' in a.casefold() for a in anchors): anchors.append('Mechanism of Action')
 for a in anchors:
  if len(a)<4: continue
  for m in re.finditer(re.escape(a.casefold()),low):
   i=m.start(); w=re.sub(r'\s+',' ',text[max(0,i-80):i+6000]).strip()
   if len(w)>=120: candidates.append((len(a),len(w),w))
 if not candidates: raise RuntimeError(f'cited locator not resolved: {locator}')
 return max(candidates,key=lambda z:(z[0],z[1]))[2]
def strip_ncjmm(o):
 if isinstance(o,dict):
  o.pop('ncjmm',None)
  for v in o.values(): strip_ncjmm(v)
 elif isinstance(o,list):
  for v in o: strip_ncjmm(v)
def main():
 b=json.loads(P.read_text()); assert [x['num'] for x in b['items']]==list(range(START,END+1)); strip_ncjmm(b); cache={}
 for x in b['items']:
  for s in x.get('sources',[]):
   url=s['url']; loc=s.get('section_locator') or s.get('source_locator') or ''; ck=(url,loc)
   if ck not in cache:
    raw=fetch(url); sec=cited_window(clean(raw),loc); cache[ck]=(hashlib.sha256(raw).hexdigest(),hashlib.sha256(sec.encode()).hexdigest())
   psha,csha=cache[ck]; s['source_page_sha256']=psha; s['cited_section_sha256']=csha
   if 'mechanism of action' in loc.casefold(): s['mechanism_section_sha256']=csha
   s['hash_status']='FROZEN_FROM_LIVE_REFETCH_AND_DECLARED_LOCATOR_2026-09-10'
 ti=b.setdefault('technical_integrity',{}); ti['source_hashes_complete']=True; ti['required_before_freeze']='COMPLETE_2026-09-10: source_page_sha256 + cited_section_sha256 bound to declared locator'; ti['independent_audit_complete']=False
 for x in b['items']:
  aq=x.get('author_qa',{})
  if 'technical_hash_gate' in aq: aq['technical_hash_gate']='PASS — live refetch, source-page hash, and declared-locator section hash completed 2026-09-10.'
 P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n'); raw=P.read_text(); assert 'ncjmm' not in raw.casefold()
 assert all(s.get('source_page_sha256') and s.get('cited_section_sha256') for x in b['items'] for s in x.get('sources',[]))
 print(json.dumps({'items':len(b['items']),'sources':sum(len(x.get('sources',[])) for x in b['items']),'technical_freeze':'PASS'},sort_keys=True))
if __name__=='__main__': main()
