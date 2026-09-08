#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sqlite3
from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from pypdf import PdfReader
import verify_q1451_q1475_preflight as v

ROOT=v.ROOT
REPO=v.REPO
DB=v.DB
CAND=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
OUT=ROOT/'audit'/'Q1476_Q1500_DETERMINISTIC_PREFLIGHT.json'
EXPECTED_DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
EXPECTED_CAND_BLOB='36326c344c041be23ba393d5ea6ad5771112d600'
EXPECTED_CANONICAL_COUNT=1300
USMLE=v.USMLE

WORKSTREAM_FILES=[
    ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',
    ROOT/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',
    ROOT/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',
    ROOT/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',
    ROOT/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',
    ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json',
]


def load_workstream():
    out=[]; files=[]
    for p in WORKSTREAM_FILES:
        if not p.exists(): raise SystemExit(f'missing workstream corpus file: {p}')
        b=json.loads(p.read_text())
        files.append({'path':str(p.relative_to(REPO)),'git_blob':v.gitblob(p),'count':len(b.get('items',[]))})
        for x in b.get('items',[]):
            q=x.get('num')
            if isinstance(q,int) and 1301<=q<=1475:
                out.append((q,v.item_text(x)))
    nums=[q for q,_ in out]
    if len(nums)!=175 or set(nums)!=set(range(1301,1476)):
        raise SystemExit(f'workstream corpus must cover Q1301-Q1475 exactly once; count={len(nums)} unique={len(set(nums))}')
    return out,files


def extract_source_text(raw:bytes,url:str)->str:
    if raw.startswith(b'%PDF') or url.casefold().endswith('.pdf'):
        reader=PdfReader(BytesIO(raw))
        text=' '.join((page.extract_text() or '') for page in reader.pages)
        return ' '.join(text.split())
    return v.htmltext(raw)


def source_binding(item:dict,source:dict,page_text:str)->tuple[bool,dict]:
    url=source.get('url',''); host=urlparse(url).netloc
    actual=v.toks(page_text)
    title_tokens=v.toks(source.get('title',''))
    title_overlap=len(title_tokens & actual)
    title_need=max(2,min(4,max(1,len(title_tokens)//2)))
    locator=source.get('section_locator','')
    locator_ok=bool(locator.strip())
    if '12.1' in locator:
        locator_ok=locator_ok and 'mechanism of action' in page_text.casefold()
    if '12.3' in locator:
        locator_ok=locator_ok and 'pharmacokinetics' in page_text.casefold()
    if '12.4' in locator:
        locator_ok=locator_ok and ('microbiology' in page_text.casefold() or 'mechanism of action' in page_text.casefold())
    if '11 Description' in locator:
        locator_ok=locator_ok and 'description' in page_text.casefold()

    identifier_ok=False; identifier_type=None
    if host in {'dailymed.nlm.nih.gov','www.dailymed.nlm.nih.gov'}:
        identifier_type='DAILYMED_SETID'
        sid=str(source.get('setid','')).strip()
        identifier_ok=bool(sid) and (sid.casefold() in url.casefold() or sid.casefold() in page_text.casefold()) and not source.get('fda_application_id')
    elif host in {'www.accessdata.fda.gov','accessdata.fda.gov'}:
        identifier_type='FDA_NDA'
        m=re.search(r'/([0-9]{6})(?:Orig1)?s[0-9]{3}lbl\.pdf$',url,re.I)
        expected=f'NDA {m.group(1)}' if m else None
        identifier_ok=bool(expected) and source.get('identifier_type')=='FDA_NDA' and source.get('fda_application_id')==expected and not source.get('setid')

    key=item['item']['intended_key']
    key_text=item['explanation']['key_explanation']
    key_overlap=len(v.toks(key_text) & actual)
    drug_overlap=len(v.toks(str(item.get('drug',''))) & actual)
    semantic_ok=(key_overlap>=2 and drug_overlap>=1)
    ok=(title_overlap>=title_need and locator_ok and identifier_ok and semantic_ok)
    return ok,{
        'title_token_overlap':title_overlap,'title_token_minimum':title_need,
        'locator_ok':locator_ok,'identifier_type':identifier_type,'identifier_ok':identifier_ok,
        'key_explanation_token_overlap':key_overlap,'drug_token_overlap':drug_overlap,'semantic_anchor_ok':semantic_ok,
        'key':key,
    }


def main():
    assert v.gitblob(DB)==EXPECTED_DB_BLOB,(v.gitblob(DB),EXPECTED_DB_BLOB)
    assert v.gitblob(CAND)==EXPECTED_CAND_BLOB,(v.gitblob(CAND),EXPECTED_CAND_BLOB)

    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("SELECT candidate_id,payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("SELECT count(*) FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]
    con.close()
    assert len(rows)==reviews==EXPECTED_CANONICAL_COUNT,(len(rows),reviews)
    canonical=[(cid,v.canonical_text(pj)) for cid,pj in rows]
    workstream,workstream_files=load_workstream()

    usmle_text=extract_source_text(v.fetch_retry(USMLE),USMLE)
    for d in sorted(v.ALLOWED_DISCIPLINES):
        assert d in usmle_text,('current USMLE discipline label missing',d)

    b=json.loads(CAND.read_text()); items=b['items']
    assert [x['num'] for x in items]==list(range(1476,1501)) and len(items)==25
    assert b['candidate_count']==25 and b['production_import_ready'] is False
    assert b['canonical_count_before']==b['canonical_count_after']==1300
    assert b['answer_key_sequence']=='ABCDEABCDEABCDEABCDEABCDE'
    assert b['answer_key_distribution']=={'A':5,'B':5,'C':5,'D':5,'E':5}
    assert 'ncjmm' not in CAND.read_text().casefold()
    ti=b['technical_integrity']
    assert ti['exact_drug_reuse_gate_q1301_q1475']=='PASS'
    assert ti['source_identifier_contract']=='PASS_DAILYMED_SETID_OR_FDA_NDA_AS_APPLICABLE'
    assert ti['independent_auditor_a_complete'] is False and ti['independent_auditor_b_complete'] is False
    assert ti['trusted_importer_complete'] is False

    source_cache={}; source_reports=[]; item_reports=[]; global_fail=[]
    for x in items:
        q=x['num']; it=x['item']; bp=x['blueprint']; ex=x['explanation']; ev=x['evidence_map']; srcs=x['sources']; fail=[]
        if bp['primary_system'] not in usmle_text: fail.append('system_label')
        if bp['primary_competency'] not in usmle_text: fail.append('competency_label')
        if bp.get('official_outline_path')!=[bp['primary_system']]: fail.append('outline_path')
        if not set(bp.get('disciplines',[])).issubset(v.ALLOWED_DISCIPLINES): fail.append('discipline_enum')
        if any(d not in usmle_text for d in bp.get('disciplines',[])): fail.append('discipline_currentness')

        if list(it.get('options',{}))!=list('ABCDE'): fail.append('options_labels')
        if len(set(v.norm(z) for z in it.get('options',{}).values()))!=5: fail.append('options_unique')
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
            if u.scheme!='https' or u.netloc not in v.ALLOWED_SOURCE_HOSTS:
                fail.append('source_domain'); continue
            if not s.get('section_locator') or s.get('retrieved_at')!='2026-09-08': fail.append('source_metadata')
            url=s['url']
            try:
                if url not in source_cache:
                    source_cache[url]=extract_source_text(v.fetch_retry(url),url)
                ok,detail=source_binding(x,s,source_cache[url])
            except Exception as e:
                ok=False; detail={'exception':type(e).__name__,'message':str(e)[:200]}
            source_reports.append({'q':q,'source_id':s.get('source_id'),'url':url,'status':'PASS' if ok else 'BLOCKED',**detail})
            if not ok: fail.append('live_source_binding')

        text=v.item_text(x)
        cscore=[]
        for cid,ct in canonical:
            j,s=v.jaccard(text,ct),v.seq(text,ct); cscore.append((max(j,s),j,s,cid))
        cscore.sort(reverse=True); cmaxj=max(z[1] for z in cscore); cmaxs=max(z[2] for z in cscore)
        if cmaxj>=0.45: fail.append('canonical_jaccard_collision')
        if cmaxs>=0.70: fail.append('canonical_sequence_collision')

        wscore=[]
        for oq,ot in workstream:
            j,s=v.jaccard(text,ot),v.seq(text,ot); wscore.append((max(j,s),j,s,oq))
        wscore.sort(reverse=True); wmaxj=max(z[1] for z in wscore); wmaxs=max(z[2] for z in wscore)
        if wmaxj>=0.40: fail.append('workstream_jaccard_collision')
        if wmaxs>=0.65: fail.append('workstream_sequence_collision')

        item_reports.append({
            'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'key':key,
            'evidence_contract':'PASS' if not any(f.startswith('evidence_') or f=='key_rationale_binding' for f in fail) else 'BLOCKED',
            'source_live_binding':'PASS' if 'live_source_binding' not in fail else 'BLOCKED',
            'blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path','discipline_enum','discipline_currentness']) else 'BLOCKED',
            'canonical_duplicate_gate':{'status':'PASS' if not any(f.startswith('canonical_') for f in fail) else 'BLOCKED','max_jaccard':round(cmaxj,5),'max_sequence':round(cmaxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in cscore[:5]]},
            'prior_workstream_duplicate_gate':{'status':'PASS' if not any(f.startswith('workstream_') for f in fail) else 'BLOCKED','max_jaccard':round(wmaxj,5),'max_sequence':round(wmaxs,5),'top5':[{'q':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in wscore[:5]]}
        })
        global_fail.extend(f'Q{q}:{f}' for f in sorted(set(fail)))

    intra=[]
    for i,a in enumerate(items):
        for c in items[i+1:]:
            j,s=v.jaccard(v.item_text(a),v.item_text(c)),v.seq(v.item_text(a),v.item_text(c))
            intra.append((max(j,s),j,s,a['num'],c['num']))
            if j>=0.40 or s>=0.65: global_fail.append(f"INTRABATCH:{a['num']}-{c['num']}")
    intra.sort(reverse=True)
    if any(s['status']!='PASS' for s in source_reports): global_fail.append('SOURCE_REPORT_BLOCKED')

    out={
        'audit_id':'Q1476-Q1500-DETERMINISTIC-PREFLIGHT-20260908',
        'scope':'Deterministic immutable-blob preflight. Not independent Auditor A/B and not production acceptance evidence.',
        'canonical_db_blob':EXPECTED_DB_BLOB,'canonical_count':EXPECTED_CANONICAL_COUNT,'canonical_review_count':reviews,
        'candidate_file':str(CAND.relative_to(REPO)),'candidate_git_blob':EXPECTED_CAND_BLOB,'candidate_count':25,'item_range':'Q1476-Q1500',
        'answer_distribution':dict(Counter(x['item']['intended_key'] for x in items)),
        'prior_workstream_range':'Q1301-Q1475','prior_workstream_count':len(workstream),'prior_workstream_files':workstream_files,
        'live_source_reverification_performed':True,'current_usmle_blueprint_reverification_performed':True,
        'source_identifier_policy':'DailyMed SetID or FDA NDA identifier, according to source system',
        'item_reports':item_reports,'source_reports':source_reports,
        'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for _,j,s,q1,q2 in intra[:10]],
        'failures':sorted(set(global_fail)),'verdict':'DETERMINISTIC_PREFLIGHT_PASS' if not global_fail else 'BLOCKED',
        'independent_auditor_a_complete':False,'independent_auditor_b_complete':False,'production_import_ready':False,'production_db_modified':False
    }
    assert 'ncjmm' not in json.dumps(out,ensure_ascii=False).casefold()
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
