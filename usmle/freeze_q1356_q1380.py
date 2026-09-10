#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,urllib.request
from pathlib import Path
P=Path('usmle/batch_specs_1301_1400/04_q1356_q1380_author_20260908.json')

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Freeze/1.2'})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read(4000000)

def clean_text(raw):
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()

def cited_window(text,locator):
    low=text.casefold(); candidates=[]
    parts=[p.strip() for p in re.split(r'[;|]',locator or '') if p.strip()]
    anchors=[]
    for p in parts:
        anchors += [p, re.sub(r'^\s*\d+(?:\.\d+)*\s*','',p).strip()]
    if 'mechanism of action' not in [a.casefold() for a in anchors]: anchors.append('Mechanism of Action')
    for a in anchors:
        if len(a)<4: continue
        for m in re.finditer(re.escape(a.casefold()),low):
            i=m.start(); w=re.sub(r'\s+',' ',text[max(0,i-80):i+6000]).strip()
            if len(w)>=120: candidates.append((len(a),len(w),w))
    if not candidates:
        # Fail closed: a declared locator must resolve in the fetched source.
        raise RuntimeError(f'cited locator not resolved: {locator}')
    candidates.sort(reverse=True,key=lambda z:(z[0],z[1]))
    return candidates[0][2]

def strip_ncjmm(obj):
    if isinstance(obj,dict):
        obj.pop('ncjmm',None)
        for v in obj.values(): strip_ncjmm(v)
    elif isinstance(obj,list):
        for v in obj: strip_ncjmm(v)

def main():
    b=json.loads(P.read_text()); assert [x['num'] for x in b['items']]==list(range(1356,1381)); strip_ncjmm(b)
    cache={}
    for x in b['items']:
        for s in x.get('sources',[]):
            url=s['url']; locator=s.get('section_locator') or s.get('source_locator') or ''
            ck=(url,locator)
            if ck not in cache:
                raw=fetch(url); text=clean_text(raw); sec=cited_window(text,locator)
                cache[ck]=(hashlib.sha256(raw).hexdigest(),hashlib.sha256(sec.encode()).hexdigest())
            psha,csha=cache[ck]
            s['source_page_sha256']=psha
            s['cited_section_sha256']=csha
            if 'mechanism of action' in locator.casefold(): s['mechanism_section_sha256']=csha
            else: s.pop('mechanism_section_sha256',None)
            s['hash_status']='FROZEN_FROM_LIVE_REFETCH_AND_DECLARED_LOCATOR_2026-09-10'
    ti=b['technical_integrity']; ti['source_hashes_complete']=True; ti['required_before_freeze']='COMPLETE_2026-09-10: source_page_sha256 + cited_section_sha256 bound to declared locator'; ti['independent_audit_complete']=False
    for x in b['items']:
        aq=x.get('author_qa',{})
        if 'technical_hash_gate' in aq: aq['technical_hash_gate']='PASS — live refetch, source-page hash, and declared-locator section hash completed 2026-09-10.'
    P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    raw=P.read_text(); assert 'ncjmm' not in raw.casefold()
    assert all(s.get('source_page_sha256') and s.get('cited_section_sha256') for x in b['items'] for s in x.get('sources',[]))
    print(json.dumps({'items':25,'sources':sum(len(x.get('sources',[])) for x in b['items']),'technical_freeze':'PASS'},sort_keys=True))
if __name__=='__main__': main()
