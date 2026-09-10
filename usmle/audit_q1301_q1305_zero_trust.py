#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess,urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
CAND=ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json'
OUT=ROOT/'audit'/'Q1301_Q1305_ZERO_TRUST.json'
CAND_BLOB='f9e2cf5519886ee736e8bada097b5a745646ea29'
DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
GENERIC={'prescribing','information','study','patients','with','and','the','of','in','a','an','for','to','by'}

def blob(p):
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()

def norm(s):
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())

def toks(s): return set(norm(s).split())
def jac(a,b):
    A,B=toks(a),toks(b)
    return len(A&B)/len(A|B) if A|B else 0.0

def fetch_text(url):
    host=urlparse(url).netloc.casefold()
    if 'pubmed.ncbi.nlm.nih.gov' in host:
        m=re.search(r'/([0-9]+)/?$',url)
        if not m: raise ValueError('pubmed PMID missing')
        url=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={m.group(1)}&retmode=xml'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-QA/1.1'})
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read(4000000)
    txt=raw.decode('utf-8','ignore')
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',txt))

def source_check(s,ex,cache):
    url=s.get('url',''); sid=s.get('source_id'); host=urlparse(url).netloc.casefold()
    ok=bool(url.startswith('https://') and s.get('section_locator') and sid)
    detail={'host':host}
    try:
        if url not in cache: cache[url]=fetch_text(url)
        page=cache[url].casefold(); pt=toks(page)
        title=toks(s.get('title','')); title_overlap=len(title & pt)
        keyt=toks(ex.get('key_explanation','')); semantic=len(keyt & pt)
        detail.update({'title_overlap':title_overlap,'semantic_overlap':semantic})
        if 'dailymed.nlm.nih.gov' in host:
            setid=str(s.get('setid','')).strip().casefold()
            title_core={t for t in title if t not in GENERIC and len(t)>3}
            core_overlap=len(title_core & pt)
            detail.update({'setid':setid,'title_core_overlap':core_overlap})
            ok = ok and bool(setid) and setid in url.casefold() and core_overlap>=1 and semantic>=2
            if '12.1' in str(s.get('section_locator','')):
                ok = ok and 'mechanism of action' in page
        elif 'pubmed.ncbi.nlm.nih.gov' in host:
            m=re.search(r'/([0-9]+)/?$',url)
            pmid=m.group(1) if m else ''
            detail['pmid']=pmid
            need=max(2,min(5,(len(title)+1)//2))
            ok = ok and bool(pmid) and pmid in page and title_overlap>=need and semantic>=1
        else:
            need=max(2,min(4,(len(title)+1)//2 if title else 2))
            ok = ok and title_overlap>=need and semantic>=1
    except Exception as e:
        ok=False; detail={'host':host,'error':type(e).__name__,'message':str(e)[:160]}
    return ok,detail

def item_text(x):
    it=x['item']
    return ' '.join([it.get('vignette',''),it.get('lead_in',''),*it.get('options',{}).values(),it.get('tested_construct','')])

def main():
    assert blob(CAND)==CAND_BLOB,(blob(CAND),CAND_BLOB)
    assert blob(DB)==DB_BLOB,(blob(DB),DB_BLOB)
    raw=CAND.read_text(); assert 'ncjmm' not in raw.casefold()
    b=json.loads(raw); items=b['items']
    assert [x['num'] for x in items]==list(range(1301,1306)) and len(items)==5
    assert b['canonical_count_before']==b['canonical_count_after']==1300
    assert b['production_import_ready'] is False

    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]
    con.close(); assert len(rows)==reviews==1300
    canon=[]
    for cid,pj in rows:
        try:
            p=json.loads(pj); q=p.get('item',{})
            text=' '.join([q.get('vignette',''),q.get('lead_in',''),*q.get('options',{}).values(),q.get('tested_construct','')])
        except Exception: text=pj
        canon.append((cid,text))

    cache={}; reports=[]; failures=[]
    for x in items:
        q=x['num']; it=x['item']; ex=x['explanation']; ev=x['evidence_map']; src=x['sources']; aq=x['author_qa']; f=[]
        opts=it.get('options',{}); key=it.get('intended_key')
        if list(opts)!=list('ABCDE') or len({norm(v) for v in opts.values()})!=5: f.append('options')
        if key not in 'ABCDE': f.append('key')
        if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
        de=ex.get('distractor_explanations',{})
        if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): f.append('rationale_eo')
        if ex.get('key_explanation')!=de.get(key): f.append('key_rationale_binding')
        em={e.get('option'):e for e in ev} if isinstance(ev,list) else {}
        if set(em)!=set('ABCDE'): f.append('evidence_shape')
        direct=[L for L,e in em.items() if e.get('direct_or_inference')=='direct']
        if direct!=[key]: f.append('evidence_derived_key')
        ids={s.get('source_id') for s in src}
        for L,e in em.items():
            if not set(e.get('source_ids',[])).issubset(ids): f.append('evidence_source_binding')
            if e.get('claim_locator')!=f'explanation.distractor_explanations.{L}': f.append('evidence_locator_binding')
        if aq.get('status')!='AUTHOR_QA_PASS' or aq.get('unresolved_content_defects')!=[]: f.append('author_state')
        attack=aq.get('second_answer_attack',{})
        alt=attack.get('strongest_alternative') or attack.get('option')
        if alt not in opts or alt==key or len(attack.get('resolution','').strip())<40: f.append('second_answer_attack')

        source_status=[]
        for s in src:
            ok,detail=source_check(s,ex,cache)
            source_status.append({'source_id':s.get('source_id'),'url':s.get('url'),'status':'PASS' if ok else 'BLOCKED',**detail})
            if not ok: f.append('live_source_binding')

        text=item_text(x); scored=[(jac(text,ct),cid) for cid,ct in canon]; scored.sort(reverse=True)
        maxj=scored[0][0] if scored else 0
        if maxj>=0.45: f.append('canonical_duplicate')
        status='PASS' if not f else 'BLOCKED'
        reports.append({'q':q,'status':status,'evidence_derived_key':direct[0] if len(direct)==1 else None,'intended_key':key,'second_answer_attack':'PASS' if 'second_answer_attack' not in f else 'BLOCKED','source_live_binding':'PASS' if 'live_source_binding' not in f else 'BLOCKED','canonical_max_jaccard':round(maxj,5),'canonical_top_match':scored[0][1] if scored else None,'ncjmm':'NOT_APPLICABLE_USMLE','source_reports':source_status,'failures':sorted(set(f))})
        failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))

    out={'audit_id':'Q1301-Q1305-ZERO-TRUST-R2-20260910','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'canonical_review_count':1300,'item_count':5,'item_reports':reports,'failures':failures,'verdict':'ZERO_TRUST_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':5},sort_keys=True))
    if failures: raise SystemExit(1)

if __name__=='__main__': main()
