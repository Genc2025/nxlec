#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,urllib.request
from pathlib import Path
P=Path(os.environ['CAND_PATH']); START=int(os.environ['START_Q']); END=int(os.environ['END_Q'])
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Freeze/2.2'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read(4000000)
def clean(raw): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()
def nloc(s):
 s=str(s).casefold().replace('–','-').replace('—','-').replace('−','-')
 s=re.sub(r'[^a-z0-9.]+',' ',s)
 return ' '.join(s.split())
def resolve_part(nt,part):
 np=nloc(part); anchors=[]
 if np: anchors.append(np)
 no_num=re.sub(r'^\d+(?:\.\d+)*\s*','',np).strip()
 if no_num and no_num not in anchors: anchors.append(no_num)
 # fallback phrases are allowed only when explicitly present in this locator component.
 for phrase in ('mechanism of action','microbiology','description','clinical pharmacology'):
  if phrase in no_num and phrase not in anchors: anchors.append(phrase)
 candidates=[]
 for a in anchors:
  if len(a)<4: continue
  start=0
  while True:
   i=nt.find(a,start)
   if i<0: break
   w=nt[max(0,i-120):i+6000].strip()
   if len(w)>=120: candidates.append((len(a),i,w))
   start=i+1
 if not candidates: raise RuntimeError(f'cited locator component not resolved: {part}')
 # prefer the most specific anchor; for duplicate TOC/body hits prefer the later substantive occurrence.
 candidates.sort(key=lambda z:(z[0],z[1]),reverse=True)
 return candidates[0][2]
def cited_material(text,locator):
 nt=nloc(text)
 parts=[p.strip() for p in re.split(r'[;|]',locator or '') if p.strip()]
 if not parts: raise RuntimeError('empty cited locator')
 windows=[resolve_part(nt,p) for p in parts]
 # deterministic separators make a multi-section hash unambiguous and bind every declared component.
 return '\n--LOCATOR-COMPONENT--\n'.join(windows),len(parts)
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
    raw=fetch(url); material,nparts=cited_material(clean(raw),loc); cache[ck]=(hashlib.sha256(raw).hexdigest(),hashlib.sha256(material.encode()).hexdigest(),nparts)
   psha,csha,nparts=cache[ck]; s['source_page_sha256']=psha; s['cited_section_sha256']=csha; s['cited_locator_component_count']=nparts
   if 'mechanism of action' in nloc(loc): s['mechanism_section_sha256']=csha
   s['hash_status']='FROZEN_FROM_LIVE_REFETCH_ALL_DECLARED_LOCATOR_COMPONENTS_2026-09-10'
 ti=b.setdefault('technical_integrity',{}); ti['source_hashes_complete']=True; ti['required_before_freeze']='COMPLETE_2026-09-10: source_page_sha256 + cited_section_sha256 bind every declared locator component'; ti['independent_audit_complete']=False
 for x in b['items']:
  aq=x.get('author_qa',{})
  if 'technical_hash_gate' in aq: aq['technical_hash_gate']='PASS — live refetch and hashes for every declared locator component completed 2026-09-10.'
 P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n'); raw=P.read_text(); assert 'ncjmm' not in raw.casefold()
 assert all(s.get('source_page_sha256') and s.get('cited_section_sha256') and s.get('cited_locator_component_count',0)>=1 for x in b['items'] for s in x.get('sources',[]))
 print(json.dumps({'items':len(b['items']),'sources':sum(len(x.get('sources',[])) for x in b['items']),'technical_freeze':'PASS'},sort_keys=True))
if __name__=='__main__': main()
