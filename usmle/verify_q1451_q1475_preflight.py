#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
CAND=ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908.json'
OUT=ROOT/'audit'/'Q1451_Q1475_DETERMINISTIC_PREFLIGHT.json'
EXPECTED_DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
EXPECTED_CAND_BLOB='1fb2d5ea9dd1b687555c6fbbe82281bb4476b9d0'
EXPECTED_CANONICAL_COUNT=1300
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'

WORKSTREAM_FILES=[
    ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',
    ROOT/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',
    ROOT/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',
    ROOT/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',
]

ALLOWED_DISCIPLINES={'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology','Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'}
ALLOWED_SOURCE_HOSTS={'dailymed.nlm.nih.gov','www.accessdata.fda.gov','accessdata.fda.gov','www.fda.gov','fda.gov','www.usmle.org','usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','ncbi.nlm.nih.gov'}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder drug treatment therapy cells cell receptor protein enzyme mechanism action'.split())


def gitblob(p:Path)->str:
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()


def norm(s:str)->str:
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',s.casefold().replace('β','beta').replace('α','alpha')).split())


def toks(s:str)->set[str]:
    return {w for w in norm(s).split() if len(w)>2 and w not in STOP}


def item_text(x:dict)->str:
    it=x.get('item',x)
    ex=x.get('explanation',{})
    return ' '.join([it.get('vignette',''),it.get('lead_in',''),it.get('tested_construct',''),*it.get('options',{}).values(),ex.get('key_explanation',''),ex.get('educational_objective','')])


def canonical_text(payload_json:str)->str:
    return item_text(json.loads(payload_json))


def jaccard(a:str,b:str)->float:
    A,B=toks(a),toks(b)
    return len(A&B)/len(A|B) if A|B else 0.0


def seq(a:str,b:str)->float:
    return SequenceMatcher(None,norm(a),norm(b),autojunk=True).ratio()


def fetch_retry(url:str,tries:int=5)->bytes:
    err=None
    for attempt in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-preflight/1.0'})
            with urllib.request.urlopen(req,timeout=45) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            err=e
            if e.code not in {429,500,502,503,504}: raise
        except (urllib.error.URLError,TimeoutError) as e:
            err=e
        time.sleep(min(15,2**attempt))
    raise err


def htmltext(raw:bytes)->str:
    return ' '.join(re.sub(r'<[^>]+>',' ',html.unescape(raw.decode('utf-8','ignore'))).split())


def source_binding_ok(source:dict,page_text:str)->tuple[bool,dict]:
    title_tokens=toks(source.get('title','')); actual=toks(page_text)
    overlap=len(title_tokens&actual); need=max(2,min(5,max(1,len(title_tokens)//2)))
    setid=source.get('setid'); setid_ok=True
    if setid:
        setid_ok=setid.casefold() in page_text.casefold() or setid.casefold() in source.get('url','').casefold()
    locator=source.get('section_locator',''); locator_ok=bool(locator.strip())
    if '12.1' in locator:
        locator_ok=locator_ok and ('mechanism of action' in page_text.casefold())
    if '12.3' in locator:
        locator_ok=locator_ok and ('pharmacokinetics' in page_text.casefold())
    if '11 Description' in locator:
        locator_ok=locator_ok and ('description' in page_text.casefold())
    return overlap>=need and setid_ok and locator_ok,{'title_token_overlap':overlap,'title_token_minimum':need,'setid_ok':setid_ok,'locator_ok':locator_ok}


def load_workstream():
    out=[]; files=[]
    for p in WORKSTREAM_FILES:
        if not p.exists():
            raise SystemExit(f'missing workstream corpus file: {p}')
        b=json.loads(p.read_text())
        files.append({'path':str(p.relative_to(REPO)),'git_blob':gitblob(p),'count':len(b.get('items',[]))})
        for x in b.get('items',[]):
            q=x.get('num')
            if isinstance(q,int) and 1301<=q<=1450:
                out.append((q,item_text(x)))
    nums=[q for q,_ in out]
    if len(nums)!=150 or set(nums)!=set(range(1301,1451)):
        raise SystemExit(f'workstream corpus must cover Q1301-Q1450 exactly once; got count={len(nums)} unique={len(set(nums))}')
    return out,files


def main():
    assert gitblob(DB)==EXPECTED_DB_BLOB,(gitblob(DB),EXPECTED_DB_BLOB)
    assert gitblob(CAND)==EXPECTED_CAND_BLOB,(gitblob(CAND),EXPECTED_CAND_BLOB)

    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("SELECT candidate_id,payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("SELECT count(*) FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]
    con.close()
    assert len(rows)==reviews==EXPECTED_CANONICAL_COUNT,(len(rows),reviews)
    canonical=[(cid,canonical_text(pj)) for cid,pj in rows]
    workstream,workstream_files=load_workstream()

    usmle_text=htmltext(fetch_retry(USMLE))
    for d in sorted(ALLOWED_DISCIPLINES):
        assert d in usmle_text,('current USMLE discipline label missing',d)

    b=json.loads(CAND.read_text()); items=b['items']
    assert [x['num'] for x in items]==list(range(1451,1476)) and len(items)==25
    assert b['candidate_count']==25 and b['production_import_ready'] is False
    assert b['canonical_count_before']==b['canonical_count_after']==1300
    assert b['answer_key_sequence']=='ABCDEABCDEABCDEABCDEABCDE'
    assert b['answer_key_distribution']=={'A':5,'B':5,'C':5,'D':5,'E':5}
    assert 'ncjmm' not in CAND.read_text().casefold()

    source_cache={}; source_reports=[]; item_reports=[]; global_fail=[]
    for x in items:
        q=x['num']; it=x['item']; bp=x['blueprint']; ex=x['explanation']; ev=x['evidence_map']; srcs=x['sources']; fail=[]
        if bp['primary_system'] not in usmle_text: fail.append('system_label')
        if bp['primary_competency'] not in usmle_text: fail.append('competency_label')
        if bp.get('official_outline_path')!=[bp['primary_system']]: fail.append('outline_path')
        if not set(bp.get('disciplines',[])).issubset(ALLOWED_DISCIPLINES): fail.append('discipline_enum')
        if any(d not in usmle_text for d in bp.get('disciplines',[])): fail.append('discipline_currentness')

        if list(it.get('options',{}))!=list('ABCDE'): fail.append('options_labels')
        if len(set(norm(v) for v in it.get('options',{}).values()))!=5: fail.append('options_unique')
        key=it.get('intended_key')
        if key not in 'ABCDE': fail.append('key')
        if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): fail.append('stem_leadin')
        de=ex.get('distractor_explanations',{})
        if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): fail.append('rationale_eo')
        if ex.get('key_explanation')!=de.get(key): fail.append('key_rationale_binding')

        if not isinstance(ev,list) or len(ev)!=5:
            fail.append('evidence_map_shape'); em={}
        else:
            em={e.get('option'):e for e in ev}
            if set(em)!=set('ABCDE'): fail.append('evidence_map_options')
        ids={s.get('source_id') for s in srcs}
        if em:
            for L in 'ABCDE':
                e=em[L]
                if e.get('claim')!=de.get(L): fail.append('evidence_rationale_binding')
                if e.get('direct_or_inference')!=('direct' if L==key else 'inference'): fail.append('evidence_class')
                if not set(e.get('source_ids',[])).issubset(ids): fail.append('evidence_source_ids')
                if not e.get('source_locator'): fail.append('evidence_locator')

        for s in srcs:
            u=urlparse(s.get('url',''))
            if u.scheme!='https' or u.netloc not in ALLOWED_SOURCE_HOSTS:
                fail.append('source_domain'); continue
            if not s.get('section_locator') or s.get('retrieved_at')!='2026-09-08': fail.append('source_metadata')
            url=s['url']
            if url not in source_cache:
                source_cache[url]=htmltext(fetch_retry(url))
            ok,detail=source_binding_ok(s,source_cache[url])
            source_reports.append({'q':q,'source_id':s.get('source_id'),'url':url,'status':'PASS' if ok else 'BLOCKED',**detail})
            if not ok: fail.append('live_source_binding')

        text=item_text(x)
        cscore=[]
        for cid,ct in canonical:
            j,s=jaccard(text,ct),seq(text,ct); cscore.append((max(j,s),j,s,cid))
        cscore.sort(reverse=True); cmaxj=max(z[1] for z in cscore); cmaxs=max(z[2] for z in cscore)
        if cmaxj>=0.45: fail.append('canonical_jaccard_collision')
        if cmaxs>=0.70: fail.append('canonical_sequence_collision')

        wscore=[]
        for oq,ot in workstream:
            j,s=jaccard(text,ot),seq(text,ot); wscore.append((max(j,s),j,s,oq))
        wscore.sort(reverse=True); wmaxj=max(z[1] for z in wscore); wmaxs=max(z[2] for z in wscore)
        if wmaxj>=0.40: fail.append('workstream_jaccard_collision')
        if wmaxs>=0.65: fail.append('workstream_sequence_collision')

        item_reports.append({
            'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'key':key,
            'evidence_contract':'PASS' if not any(f.startswith('evidence_') or f=='key_rationale_binding' for f in fail) else 'BLOCKED',
            'source_live_binding':'PASS' if 'live_source_binding' not in fail else 'BLOCKED',
            'blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path','discipline_enum','discipline_currentness']) else 'BLOCKED',
            'ncjmm':'NOT_APPLICABLE_USMLE',
            'canonical_duplicate_gate':{'status':'PASS' if not any(f.startswith('canonical_') for f in fail) else 'BLOCKED','max_jaccard':round(cmaxj,5),'max_sequence':round(cmaxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in cscore[:5]]},
            'prior_workstream_duplicate_gate':{'status':'PASS' if not any(f.startswith('workstream_') for f in fail) else 'BLOCKED','max_jaccard':round(wmaxj,5),'max_sequence':round(wmaxs,5),'top5':[{'q':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in wscore[:5]]}
        })
        global_fail.extend(f'Q{q}:{f}' for f in sorted(set(fail)))

    intra=[]
    for i,a in enumerate(items):
        for c in items[i+1:]:
            j,s=jaccard(item_text(a),item_text(c)),seq(item_text(a),item_text(c)); intra.append((max(j,s),j,s,a['num'],c['num']))
            if j>=0.40 or s>=0.65: global_fail.append(f"INTRABATCH:{a['num']}-{c['num']}")
    intra.sort(reverse=True)
    if any(s['status']!='PASS' for s in source_reports): global_fail.append('SOURCE_REPORT_BLOCKED')

    out={
        'audit_id':'Q1451-Q1475-DETERMINISTIC-PREFLIGHT-20260908',
        'scope':'Deterministic author-batch preflight. Not blind Auditor A/B and not production acceptance evidence.',
        'canonical_db_blob':EXPECTED_DB_BLOB,'canonical_count':EXPECTED_CANONICAL_COUNT,'canonical_review_count':reviews,
        'candidate_file':str(CAND.relative_to(REPO)),'candidate_git_blob':EXPECTED_CAND_BLOB,'candidate_count':25,'item_range':'Q1451-Q1475',
        'answer_distribution':dict(Counter(x['item']['intended_key'] for x in items)),
        'prior_workstream_range':'Q1301-Q1450','prior_workstream_count':len(workstream),'prior_workstream_files':workstream_files,
        'live_source_reverification_performed':True,'current_usmle_blueprint_reverification_performed':True,
        'item_reports':item_reports,'source_reports':source_reports,
        'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for _,j,s,q1,q2 in intra[:10]],
        'failures':sorted(set(global_fail)),'verdict':'DETERMINISTIC_PREFLIGHT_PASS' if not global_fail else 'BLOCKED',
        'independent_auditor_a_complete':False,'independent_auditor_b_complete':False,'production_import_ready':False,'production_db_modified':False
    }
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({
        'verdict':out['verdict'],'failures':out['failures'],'candidate_count':25,'source_checks':len(source_reports),
        'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in item_reports),
        'max_canonical_sequence':max(r['canonical_duplicate_gate']['max_sequence'] for r in item_reports),
        'max_workstream_jaccard':max(r['prior_workstream_duplicate_gate']['max_jaccard'] for r in item_reports),
        'max_workstream_sequence':max(r['prior_workstream_duplicate_gate']['max_sequence'] for r in item_reports),
        'max_intrabatch_jaccard':round(max(z[1] for z in intra),5),'max_intrabatch_sequence':round(max(z[2] for z in intra),5)
    },sort_keys=True))
    if global_fail: raise SystemExit(2)


if __name__=='__main__': main()
