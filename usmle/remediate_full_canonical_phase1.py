#!/usr/bin/env python3
from __future__ import annotations
import concurrent.futures, hashlib, json, os, re, shutil, sqlite3, subprocess, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
SRC=ROOT/'data'/'usmle-step1.db'
WORK=Path(os.environ.get('WORK_DB','/tmp/usmle-step1-remediation.db'))
OUT=REPO/os.environ.get('REMEDIATION_OUT','usmle/audit/FULL_CANONICAL_Q0001_Q1535_REMEDIATION_PHASE1.json')
EXPECTED=int(os.environ.get('EXPECTED_COUNT','1535'))
DB_BLOB=os.environ['DB_BLOB']
TODAY=os.environ.get('AUDIT_DATE','2026-09-11')
MAX_WORKERS=int(os.environ.get('MAX_WORKERS','16'))

def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def nloc(s):
    s=str(s).casefold().replace('–','-').replace('—','-').replace('−','-')
    s=re.sub(r'[^a-z0-9.]+',' ',s)
    return ' '.join(s.split())
def clean(raw):
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()
def resolve_part(nt,part):
    np=nloc(part); anchors=[]
    if np: anchors.append(np)
    no_num=re.sub(r'^\d+(?:\.\d+)*\s*','',np).strip()
    if no_num and no_num not in anchors: anchors.append(no_num)
    for phrase in ('mechanism of action','microbiology','description','clinical pharmacology','warnings and precautions','adverse reactions','indications and usage'):
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
    if not candidates: raise RuntimeError('locator_not_resolved')
    candidates.sort(key=lambda z:(z[0],z[1]),reverse=True)
    return candidates[0][2]
def cited_material(text,locator):
    nt=nloc(text)
    parts=[p.strip() for p in re.split(r'[;|]',locator or '') if p.strip()]
    if not parts: raise RuntimeError('empty_locator')
    windows=[resolve_part(nt,p) for p in parts]
    return '\n--LOCATOR-COMPONENT--\n'.join(windows),len(parts)
def fetch_one(k):
    url,loc=k
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Remediation/1.0'})
        with urllib.request.urlopen(req,timeout=20) as r: raw=r.read(4000000)
        mat,nparts=cited_material(clean(raw),loc)
        return k,{'ok':True,'page_sha256':hashlib.sha256(raw).hexdigest(),'cited_sha256':hashlib.sha256(mat.encode()).hexdigest(),'parts':nparts}
    except Exception as e:
        return k,{'ok':False,'error':type(e).__name__+':'+str(e)[:160]}
def recurse_remove_ncjmm(x):
    count=0
    if isinstance(x,dict):
        if 'ncjmm' in x:
            x.pop('ncjmm',None); count+=1
        for v in x.values(): count+=recurse_remove_ncjmm(v)
    elif isinstance(x,list):
        for v in x: count+=recurse_remove_ncjmm(v)
    return count
def is_sha(s):
    return isinstance(s,str) and bool(re.fullmatch(r'[0-9a-f]{64}',s.casefold()))

def main():
    assert gitblob(SRC)==DB_BLOB
    shutil.copy2(SRC,WORK)
    c=sqlite3.connect(WORK)
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256,final_status from step2_final_items order by candidate_id").fetchall()
    revs=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews").fetchall()
    assert len(rows)==len(revs)==EXPECTED

    docs=[]
    fetch_keys=set()
    before={'blueprint_path_mismatch':0,'evidence_contract_mismatch':0,'missing_source_hashes':0,'ncjmm_present':0}
    for cid,pj,ps,ash,status in rows:
        p=json.loads(pj)
        bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
        if bp.get('primary_system') and bp.get('official_outline_path') != [bp.get('primary_system')]:
            before['blueprint_path_mismatch']+=1
        ev=p.get('evidence_map'); key=(p.get('item') or {}).get('intended_key')
        if isinstance(ev,list):
            em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
            if len(em)==5 and {e.get('option') for e in em}==set('ABCDE'):
                strong=[e.get('option') for e in em if e.get('direct_or_inference') in {'direct','mixed'}]
                bad=strong!=[key] or any(e.get('direct_or_inference')!='inference' for e in em if e.get('option')!=key)
                if bad: before['evidence_contract_mismatch']+=1
        if '"ncjmm"' in canon(p).casefold(): before['ncjmm_present']+=1
        for s in p.get('sources',[]) if isinstance(p.get('sources'),list) else []:
            if not isinstance(s,dict): continue
            if not is_sha(s.get('source_page_sha256')) or not is_sha(s.get('cited_section_sha256')):
                before['missing_source_hashes']+=1
                url=str(s.get('url','')); loc=s.get('section_locator') or s.get('source_locator') or ''
                if url.startswith('https://') and str(loc).strip(): fetch_keys.add((url,str(loc)))
        docs.append((cid,p,ash,status))

    fetch_results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for k,res in ex.map(fetch_one,sorted(fetch_keys)):
            fetch_results[k]=res

    repair_counts={'blueprint_path_fixed':0,'evidence_contract_normalized':0,'source_hashes_frozen':0,'ncjmm_removed':0,'payloads_modified':0}
    unresolved_sources=[]
    c.execute('BEGIN IMMEDIATE')
    try:
        for cid,p,ash,status in docs:
            changed=False
            bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else None
            if isinstance(bp,dict) and bp.get('primary_system') and bp.get('official_outline_path') != [bp.get('primary_system')]:
                bp['official_outline_path']=[bp.get('primary_system')]
                repair_counts['blueprint_path_fixed']+=1; changed=True

            removed=recurse_remove_ncjmm(p)
            if removed:
                repair_counts['ncjmm_removed']+=removed; changed=True

            ev=p.get('evidence_map'); key=(p.get('item') or {}).get('intended_key')
            if isinstance(ev,list) and key in 'ABCDE':
                em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
                if len(em)==5 and {e.get('option') for e in em}==set('ABCDE'):
                    local=False
                    for e in em:
                        want='direct' if e.get('option')==key else 'inference'
                        if e.get('direct_or_inference')!=want:
                            e['direct_or_inference']=want; local=True
                    if local:
                        repair_counts['evidence_contract_normalized']+=1; changed=True

            for idx,s in enumerate(p.get('sources',[]) if isinstance(p.get('sources'),list) else []):
                if not isinstance(s,dict): continue
                need=not is_sha(s.get('source_page_sha256')) or not is_sha(s.get('cited_section_sha256'))
                if not need: continue
                k=(str(s.get('url','')),str(s.get('section_locator') or s.get('source_locator') or ''))
                rr=fetch_results.get(k)
                if rr and rr.get('ok'):
                    s['source_page_sha256']=rr['page_sha256']
                    s['cited_section_sha256']=rr['cited_sha256']
                    s['cited_locator_component_count']=rr['parts']
                    s['hash_status']=f'FROZEN_FROM_LIVE_REFETCH_ALL_DECLARED_LOCATOR_COMPONENTS_{TODAY}'
                    if not s.get('retrieved_at'): s['retrieved_at']=TODAY
                    repair_counts['source_hashes_frozen']+=1; changed=True
                else:
                    unresolved_sources.append({'candidate_id':cid,'source_index':idx+1,'url':k[0],'locator':k[1],'error':(rr or {}).get('error','not_eligible_for_fetch')})

            if changed:
                p.setdefault('remediation',{})['phase1_deterministic_20260911']='APPLIED_DETACHED_NOT_FINAL'
                pj2=canon(p); ps2=hobj(p)
                c.execute('update step2_final_items set payload_json=?,payload_sha256=? where candidate_id=?',(pj2,ps2,cid))
                repair_counts['payloads_modified']+=1
        c.commit()
    except Exception:
        c.rollback(); raise

    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows2=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256,final_status from step2_final_items order by candidate_id").fetchall()
    # verify payload hashes and review linkage remain internally valid
    revmap={r[0]:r for r in revs}
    consistency=[]
    after={'blueprint_path_mismatch':0,'evidence_contract_mismatch':0,'missing_source_hashes':0,'ncjmm_present':0,'second_answer_missing_or_weak':0}
    for cid,pj,ps,ash,status in rows2:
        p=json.loads(pj)
        if hobj(p)!=ps: consistency.append({'candidate_id':cid,'defect':'payload_hash'})
        rr=revmap.get(cid)
        if not rr or rr[2]!=ash or rr[3]!='FINAL_10_10_PASS' or status!='FINAL_10_10_PASS': consistency.append({'candidate_id':cid,'defect':'review_link'})
        bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
        if bp.get('primary_system') and bp.get('official_outline_path') != [bp.get('primary_system')]: after['blueprint_path_mismatch']+=1
        ev=p.get('evidence_map'); key=(p.get('item') or {}).get('intended_key')
        if isinstance(ev,list):
            em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
            if len(em)==5 and {e.get('option') for e in em}==set('ABCDE'):
                strong=[e.get('option') for e in em if e.get('direct_or_inference') in {'direct','mixed'}]
                if strong!=[key] or any(e.get('direct_or_inference')!='inference' for e in em if e.get('option')!=key): after['evidence_contract_mismatch']+=1
        if '"ncjmm"' in canon(p).casefold(): after['ncjmm_present']+=1
        for s in p.get('sources',[]) if isinstance(p.get('sources'),list) else []:
            if isinstance(s,dict) and (not is_sha(s.get('source_page_sha256')) or not is_sha(s.get('cited_section_sha256'))): after['missing_source_hashes']+=1
        aq=p.get('author_qa') if isinstance(p.get('author_qa'),dict) else {}
        at=aq.get('second_answer_attack') if isinstance(aq.get('second_answer_attack'),dict) else {}
        opts=(p.get('item') or {}).get('options') if isinstance((p.get('item') or {}).get('options'),dict) else {}
        alt=at.get('strongest_alternative') or at.get('option')
        if at.get('status')!='PASS' or alt not in opts or alt==key or len(str(at.get('resolution','')).strip())<30:
            after['second_answer_missing_or_weak']+=1
    c.close()

    report={
      'audit_id':f'FULL-CANONICAL-Q0001-Q{EXPECTED}-REMEDIATION-PHASE1-20260911',
      'scope':f'Q0001-Q{EXPECTED}',
      'production_db_blob':DB_BLOB,
      'production_db_modified':False,
      'candidate_db_location':'ephemeral GitHub Actions workspace only',
      'candidate_sqlite_integrity':'ok',
      'candidate_payload_review_consistency_failures':consistency,
      'before':before,
      'deterministic_repairs_applied':repair_counts,
      'live_source_fetch':{
        'unique_url_locator_pairs_attempted':len(fetch_keys),
        'successful_pairs':sum(1 for r in fetch_results.values() if r.get('ok')),
        'failed_pairs':sum(1 for r in fetch_results.values() if not r.get('ok')),
        'unresolved_source_instances':len(unresolved_sources),
        'unresolved_sources_sample':unresolved_sources[:300]
      },
      'after':after,
      'remaining_substantive_blocker':'second-answer adjudication and any source/locator failures must be re-reviewed; no automatic PASS is asserted',
      'production_promotion_ready':False
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({
      'before':before,
      'repairs':repair_counts,
      'source_pairs_attempted':len(fetch_keys),
      'source_pairs_success':report['live_source_fetch']['successful_pairs'],
      'source_pairs_failed':report['live_source_fetch']['failed_pairs'],
      'after':after,
      'consistency_failures':len(consistency),
      'production_modified':False,
      'production_promotion_ready':False
    },sort_keys=True))

if __name__=='__main__':
    main()
