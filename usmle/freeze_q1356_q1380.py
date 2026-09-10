#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,urllib.request
from pathlib import Path
P=Path('usmle/batch_specs_1301_1400/04_q1356_q1380_author_20260908.json')

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Freeze/1.1'})
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(4000000)
    return raw

def clean_text(raw):
    s=raw.decode('utf-8','ignore')
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s)).strip()

def section12_1(text):
    low=text.casefold()
    starts=[m.start() for m in re.finditer(r'12\.1\s+mechanism of action',low)]
    if not starts:
        starts=[m.start() for m in re.finditer(r'mechanism of action',low)]
    if not starts: raise RuntimeError('12.1 mechanism section not found')
    candidates=[]
    for i in starts:
        tail=text[i:i+20000]
        cuts=[m.start() for m in re.finditer(r'\b(?:12\.2|12\.3|13\.1)\b',tail[80:],re.I)]
        sec=tail[:80+cuts[0]] if cuts else tail[:12000]
        sec=re.sub(r'\s+',' ',sec).strip()
        if len(sec)>=160: candidates.append(sec)
    if not candidates: raise RuntimeError('substantive mechanism section not found')
    # TOC hits are short; the substantive label section is the longest valid candidate.
    return max(candidates,key=len)

def strip_ncjmm(obj):
    if isinstance(obj,dict):
        obj.pop('ncjmm',None)
        for v in obj.values(): strip_ncjmm(v)
    elif isinstance(obj,list):
        for v in obj: strip_ncjmm(v)

def main():
    b=json.loads(P.read_text())
    assert [x['num'] for x in b['items']]==list(range(1356,1381))
    strip_ncjmm(b)
    cache={}
    for x in b['items']:
        for s in x.get('sources',[]):
            url=s['url']
            if url not in cache:
                raw=fetch(url); text=clean_text(raw); sec=section12_1(text)
                cache[url]=(hashlib.sha256(raw).hexdigest(),hashlib.sha256(sec.encode()).hexdigest())
            psha,msha=cache[url]
            s['source_page_sha256']=psha
            s['mechanism_section_sha256']=msha
            s['hash_status']='FROZEN_FROM_DETERMINISTIC_REFETCH_2026-09-10'
    b['technical_integrity']['source_hashes_complete']=True
    b['technical_integrity']['required_before_freeze']='COMPLETE_2026-09-10'
    b['technical_integrity']['independent_audit_complete']=False
    for x in b['items']:
        aq=x.get('author_qa',{})
        if 'technical_hash_gate' in aq: aq['technical_hash_gate']='PASS — deterministic source refetch and SHA-256 computation completed 2026-09-10.'
    P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    assert 'ncjmm' not in P.read_text().casefold()
    assert all(s.get('source_page_sha256') and s.get('mechanism_section_sha256') for x in b['items'] for s in x.get('sources',[]))
    print(json.dumps({'items':25,'sources':sum(len(x.get('sources',[])) for x in b['items']),'technical_freeze':'PASS'},sort_keys=True))
if __name__=='__main__': main()
