#!/usr/bin/env python3
from __future__ import annotations
import concurrent.futures, hashlib, json, os, re, shutil, sqlite3, subprocess, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
SRC=ROOT/'data'/'usmle-step1.db'
WORK=Path(os.environ.get('WORK_DB','/tmp/usmle-step1-remediation-phase1b.db'))
OUT=REPO/os.environ.get('REMEDIATION_OUT','usmle/audit/FULL_CANONICAL_Q0001_Q1535_REMEDIATION_PHASE1B.json')
EXPECTED=int(os.environ.get('EXPECTED_COUNT','1535')); DB_BLOB=os.environ['DB_BLOB']; TODAY='2026-09-11'
MAX_WORKERS=int(os.environ.get('MAX_WORKERS','16'))
STOP={'the','and','for','with','from','into','that','this','what','which','most','directly','overview','normal','disease','disorder','clinical','features','changes','effects','effect','health','information'}

def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def nloc(s):
    s=str(s).casefold().replace('–','-').replace('—','-').replace('−','-')
    s=re.sub(r'[^a-z0-9.]+',' ',s)
    return ' '.join(s.split())
def clean(raw): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()
def toks(s): return [t for t in nloc(s).split() if len(t)>=4 and t not in STOP]
def variants(url):
    out=[url]
    p=urllib.parse.urlparse(url)
    if p.netloc.casefold()=='medlineplus.gov':
        out.append(urllib.parse.urlunparse((p.scheme,'www.medlineplus.gov',p.path,p.params,p.query,p.fragment)))
    return list(dict.fromkeys(out))
def get_raw(url):
    errs=[]
    for u in variants(url):
        try:
            req=urllib.request.Request(u,headers={
              'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36',
              'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Language':'en-US,en;q=0.9'
            })
            with urllib.request.urlopen(req,timeout=20) as r:
                raw=r.read(4000000)
                if len(raw)>=200: return raw,u
        except Exception as e: errs.append(type(e).__name__+':'+str(e)[:100])
        try:
            cp=subprocess.run(['curl','-L','--compressed','--max-time','20','-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36','-H','Accept: text/html,application/xhtml+xml','-sS',u],capture_output=True,timeout=25)
            if cp.returncode==0 and len(cp.stdout)>=200: return cp.stdout,u
            errs.append('curl_rc_'+str(cp.returncode))
        except Exception as e: errs.append('curl_'+type(e).__name__)
    raise RuntimeError('|'.join(errs[-4:]))
def exact_window(nt,anchor):
    i=nt.find(anchor)
    if i<0: return None
    # prefer later body occurrence if duplicated in TOC
    pos=[]
    st=0
    while True:
        z=nt.find(anchor,st)
        if z<0: break
        pos.append(z); st=z+1
    i=pos[-1]
    return nt[max(0,i-180):i+6500]
def fuzzy_window(nt,phrase,support=''):
    pt=set(toks(phrase)); st=set(toks(support))
    target=pt|set(list(st)[:18])
    if not target: return None,0.0
    words=nt.split()
    best=(0.0,None)
    step=120
    width=900
    for i in range(0,max(1,len(words)),step):
        w=' '.join(words[i:i+width]); ws=set(words[i:i+width])
        # Locator tokens dominate; supporting-passage tokens provide corroboration.
        pc=(len(pt & ws)/len(pt)) if pt else 0
        sc=(len(st & ws)/min(len(st),18)) if st else 0
        score=0.75*pc+0.25*sc
        if score>best[0]: best=(score,w)
    return best[1],best[0]
def cited_material(text,locator,support):
    nt=nloc(text)
    parts=[p.strip() for p in re.split(r'[;|]',locator or '') if p.strip()]
    if not parts: raise RuntimeError('empty_locator')
    wins=[]
    for part in parts:
        np=nloc(part); cand=[]
        if np: cand.append(np)
        no_num=re.sub(r'^\d+(?:\.\d+)*\s*','',np).strip()
        if no_num and no_num not in cand: cand.append(no_num)
        w=None
        for a in sorted(cand,key=len,reverse=True):
            if len(a)>=4:
                w=exact_window(nt,a)
                if w: break
        if not w:
            w,score=fuzzy_window(nt,part,support)
            # require strong locator coverage/corroboration; do not accept weak semantic proximity
            if not w or score<0.58: raise RuntimeError(f'locator_not_resolved_score_{score:.2f}')
        wins.append(w)
    material='\n--LOCATOR-COMPONENT--\n'.join(wins)
    # If supporting passage exists, demand at least moderate token overlap somewhere in cited material.
    st=set(toks(support))
    if len(st)>=4:
        mt=set(material.split()); cov=len(st&mt)/min(len(st),18)
        if cov<0.28: raise RuntimeError(f'supporting_passage_not_bound_{cov:.2f}')
    return material,len(parts)
def fetch_one(k):
    url,loc,support=k
    try:
        raw,resolved=get_raw(url); mat,nparts=cited_material(clean(raw),loc,support)
        return k,{'ok':True,'resolved_url':resolved,'page_sha256':hashlib.sha256(raw).hexdigest(),'cited_sha256':hashlib.sha256(mat.encode()).hexdigest(),'parts':nparts}
    except Exception as e:
        return k,{'ok':False,'error':type(e).__name__+':'+str(e)[:240]}
def issha(s): return isinstance(s,str) and bool(re.fullmatch(r'[0-9a-f]{64}',s.casefold()))
def rm_ncjmm(o):
    n=0
    if isinstance(o,dict):
        if 'ncjmm' in o: o.pop('ncjmm'); n+=1
        for v in o.values(): n+=rm_ncjmm(v)
    elif isinstance(o,list):
        for v in o: n+=rm_ncjmm(v)
    return n

def main():
    assert gitblob(SRC)==DB_BLOB
    shutil.copy2(SRC,WORK); c=sqlite3.connect(WORK)
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=c.execute("select candidate_id,payload_json,audit_sha256,final_status from step2_final_items order by candidate_id").fetchall()
    revs=c.execute("select candidate_id,review_sha256,final_status from step2_final_reviews").fetchall()
    assert len(rows)==len(revs)==EXPECTED
    docs=[]; keys=set(); before_missing=0
    for cid,pj,ash,status in rows:
        p=json.loads(pj)
        for s in p.get('sources',[]) if isinstance(p.get('sources'),list) else []:
            if isinstance(s,dict) and (not issha(s.get('source_page_sha256')) or not issha(s.get('cited_section_sha256'))):
                before_missing+=1
                u=str(s.get('url','')); loc=str(s.get('section_locator') or s.get('source_locator') or ''); sup=str(s.get('supporting_passage') or '')
                if u.startswith('https://') and loc.strip(): keys.add((u,loc,sup))
        docs.append((cid,p,ash,status))
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for k,v in ex.map(fetch_one,sorted(keys)): results[k]=v
    rc={'blueprint_path_fixed':0,'evidence_contract_normalized':0,'source_hashes_frozen':0,'source_urls_canonicalized':0,'payloads_modified':0}
    unresolved=[]
    c.execute('BEGIN IMMEDIATE')
    try:
        for cid,p,ash,status in docs:
            changed=False
            bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
            if bp.get('primary_system') and bp.get('official_outline_path') != [bp.get('primary_system')]:
                bp['official_outline_path']=[bp.get('primary_system')]; rc['blueprint_path_fixed']+=1; changed=True
            if rm_ncjmm(p): changed=True
            ev=p.get('evidence_map'); key=(p.get('item') or {}).get('intended_key')
            if isinstance(ev,list) and key in 'ABCDE':
                em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
                if len(em)==5 and {e.get('option') for e in em}==set('ABCDE'):
                    local=False
                    for e in em:
                        want='direct' if e.get('option')==key else 'inference'
                        if e.get('direct_or_inference')!=want: e['direct_or_inference']=want; local=True
                    if local: rc['evidence_contract_normalized']+=1; changed=True
            for idx,s in enumerate(p.get('sources',[]) if isinstance(p.get('sources'),list) else []):
                if not isinstance(s,dict) or (issha(s.get('source_page_sha256')) and issha(s.get('cited_section_sha256'))): continue
                k=(str(s.get('url','')),str(s.get('section_locator') or s.get('source_locator') or ''),str(s.get('supporting_passage') or ''))
                rr=results.get(k)
                if rr and rr.get('ok'):
                    if rr['resolved_url']!=s.get('url'):
                        s['url']=rr['resolved_url']; rc['source_urls_canonicalized']+=1
                    s['source_page_sha256']=rr['page_sha256']; s['cited_section_sha256']=rr['cited_sha256']; s['cited_locator_component_count']=rr['parts']
                    s['hash_status']='FROZEN_FROM_LIVE_REFETCH_STRICT_PHASE1B_2026-09-11'
                    s['retrieved_at']=TODAY
                    rc['source_hashes_frozen']+=1; changed=True
                else:
                    unresolved.append({'candidate_id':cid,'source_index':idx+1,'url':k[0],'locator':k[1],'error':(rr or {}).get('error','not_fetchable')})
            if changed:
                p.setdefault('remediation',{})['phase1b_deterministic_20260911']='APPLIED_DETACHED_NOT_FINAL'
                c.execute('update step2_final_items set payload_json=?,payload_sha256=? where candidate_id=?',(canon(p),hobj(p),cid)); rc['payloads_modified']+=1
        c.commit()
    except Exception:
        c.rollback(); raise
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    revmap={x[0]:x for x in revs}; consistency=[]; after_missing=0; second=0; bpbad=0; evbad=0
    for cid,pj,ps,ash,status in c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256,final_status from step2_final_items"):
        p=json.loads(pj)
        if hobj(p)!=ps: consistency.append([cid,'payload_hash'])
        rr=revmap.get(cid)
        if not rr or rr[1]!=ash or rr[2]!='FINAL_10_10_PASS' or status!='FINAL_10_10_PASS': consistency.append([cid,'review_link'])
        bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
        if bp.get('primary_system') and bp.get('official_outline_path') != [bp.get('primary_system')]: bpbad+=1
        ev=p.get('evidence_map'); key=(p.get('item') or {}).get('intended_key')
        if isinstance(ev,list):
            em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
            if len(em)==5 and {e.get('option') for e in em}==set('ABCDE'):
                strong=[e.get('option') for e in em if e.get('direct_or_inference') in {'direct','mixed'}]
                if strong!=[key] or any(e.get('direct_or_inference')!='inference' for e in em if e.get('option')!=key): evbad+=1
        for s in p.get('sources',[]) if isinstance(p.get('sources'),list) else []:
            if isinstance(s,dict) and (not issha(s.get('source_page_sha256')) or not issha(s.get('cited_section_sha256'))): after_missing+=1
        aq=p.get('author_qa') if isinstance(p.get('author_qa'),dict) else {}; at=aq.get('second_answer_attack') if isinstance(aq.get('second_answer_attack'),dict) else {}
        opts=(p.get('item') or {}).get('options') if isinstance((p.get('item') or {}).get('options'),dict) else {}; alt=at.get('strongest_alternative') or at.get('option')
        if at.get('status')!='PASS' or alt not in opts or alt==key or len(str(at.get('resolution','')).strip())<30: second+=1
    c.close()
    out={
      'audit_id':'FULL-CANONICAL-Q0001-Q1535-REMEDIATION-PHASE1B-20260911','production_db_blob':DB_BLOB,'production_db_modified':False,
      'before_missing_source_hash_instances':before_missing,'unique_source_bindings_attempted':len(keys),
      'successful_source_bindings':sum(1 for v in results.values() if v.get('ok')),'failed_source_bindings':sum(1 for v in results.values() if not v.get('ok')),
      'repairs':rc,'after':{'missing_source_hash_instances':after_missing,'blueprint_path_mismatch':bpbad,'evidence_contract_mismatch':evbad,'second_answer_missing_or_weak':second},
      'candidate_payload_review_consistency_failures':consistency,'unresolved_source_instances':len(unresolved),'unresolved_sources_sample':unresolved[:500],
      'production_promotion_ready':False,'note':'Detached candidate only. Source binding requires live URL plus strict locator/supporting-passage resolution; unresolved sources and second-answer adjudication remain BLOCKED.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'attempted':len(keys),'success':out['successful_source_bindings'],'failed':out['failed_source_bindings'],'repairs':rc,'after':out['after'],'consistency_failures':len(consistency)},sort_keys=True))
if __name__=='__main__': main()
