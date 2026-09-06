#!/usr/bin/env python3
from __future__ import annotations
import html,json,re,sqlite3,time,urllib.error,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BATCH=ROOT/'batch_specs_1201_1300'/'11_q1281_q1290_author_20260906.json'; DB=ROOT/'data'/'usmle-step1.db'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'; CURRENT='USMLE Step 1 current official specifications verified 2026-09-06'
ENDO='Reproductive & Endocrine Systems'; RENAL='Respiratory & Renal/Urinary Systems'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'
ANCHORS={1281:['pcsk1','prohormone convertase 1/3'],1282:['secisbp2','sbp2'],1283:['gnrhr'],1284:['resistance to thyroid hormone alpha'],1285:['tbx19','tpit'],1286:['maged2'],1287:['slc22a12','urat1'],1288:['inf2'],1289:['trpc6'],1290:['lamb2','pierson syndrome']}
def norm(z):return re.sub(r'[^a-z0-9]+','',z.casefold())
def fetch_retry(url,tries=6):
    err=None
    for a in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'USMLE-QA/1.0 contact=qa@example.invalid'})
            with urllib.request.urlopen(req,timeout=45) as r:return r.read()
        except urllib.error.HTTPError as e:
            err=e
            if e.code not in {429,500,502,503,504}:raise
        except (urllib.error.URLError,TimeoutError) as e:err=e
        time.sleep(min(20,2**a))
    raise err
def toks(s):
    stop=set('a an the this that these those is are was were be been being to of in on at by for with from and or but as into due which what most likely patient patients his her their has have had shows show identifies identify option proposes selected because account complete vignette support keyed answer'.split())
    return [w for w in re.findall(r'[a-z0-9]+',s.casefold()) if len(w)>2 and w not in stop]
def text_item(d):
    it=d.get('item',d);return ' '.join([it.get('vignette',''),it.get('lead_in',''),it.get('tested_construct','')]+list(it.get('options',{}).values()))
def material_text(d):
    it=d.get('item',d);k=it.get('intended_key','');return ' '.join([it.get('tested_construct',''),it.get('lead_in',''),it.get('options',{}).get(k,'')]).casefold()
def anchor_hit(text,a):
    a=a.casefold()
    if re.fullmatch(r'[a-z0-9_.+-]+',a):return re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])',text) is not None
    return a in text

def main():
    b=json.loads(BATCH.read_text());items=b['items']
    assert b['production_count_before']==b['production_count_after']==1280 and b['status']=='AUTHOR_ZERO_TRUST_PASS_PENDING_CANONICAL_DUPLICATE_AND_FINAL_QA' and b['specification_version']==CURRENT
    assert [x['num'] for x in items]==list(range(1281,1291)) and b['answer_key_sequence']=='BDACECAEDB' and b['answer_key_distribution']=={'A':2,'B':2,'C':2,'D':2,'E':2}
    assert Counter(x['blueprint']['primary_system'] for x in items)==Counter({ENDO:5,RENAL:5});assert Counter(x['blueprint']['primary_competency'] for x in items)==Counter({DX:5,MK:5})

    raw=html.unescape(fetch_retry(USMLE).decode('utf-8','ignore')); page=' '.join(re.sub(r'<[^>]+>',' ',raw).split())
    for label in [ENDO,RENAL,MK,DX,'Pathology','Physiology','Biochemistry','Genetics','Histology & Cell Biology','Gross Anatomy & Embryology']:
        assert label in page,('official current label missing',label)
    assert re.search(r'Respiratory\s*&\s*Renal/Urinary Systems\s*\|?\s*11-15',page)
    assert re.search(r'Reproductive\s*&\s*Endocrine Systems\s*\|?\s*12.?16',page)

    expected={};support={}
    for x in items:
        n=x['num'];bp=x['blueprint'];it=x['item'];key=it['intended_key'];de=x['explanation']['distractor_explanations'];em={e['option']:e for e in x['evidence_map']}
        assert x['specification_version']==CURRENT and bp['primary_system'] in {ENDO,RENAL} and bp['primary_competency'] in {DX,MK} and bp['official_outline_path']==[bp['primary_system']] and bp['internal_content_path']
        assert list(it['options'])==list('ABCDE') and len(set(it['options'].values()))==5 and it['difficulty']=='moderate-hard' and it['lead_in'].endswith('?')
        assert set(de)==set(em)==set('ABCDE') and x['explanation']['key_explanation'] and x['explanation']['educational_objective'] and 'ncjmm' not in json.dumps(x).casefold()
        assert x['author_self_audit']['unresolved_concerns']==[] and x['author_self_audit']['suggested_changes']==[] and len(x['sources'])>=3
        ids={s['source_id'] for s in x['sources']}
        for L in 'ABCDE':
            assert em[L]['claim']==de[L] and em[L]['direct_or_inference']==('direct' if L==key else 'inference') and set(em[L]['source_ids']).issubset(ids)
            if L!=key:assert de[L].startswith(f"Option {L} proposes '") and 'It is not selected because it does not account for' in de[L] and len(de[L])>=160
        official=x['sources'][0];assert official['agency']=='USMLE' and official['url']==USMLE and official['official_exam_specification'] is True and official['publication_or_revision_date']=='current official specifications' and official['retrieved_at']=='2026-09-06'
        assert bp['primary_system'] in official['section_locator'] and bp['primary_competency'] in official['section_locator'] and all(d in official['section_locator'] for d in bp['disciplines'])
        for s in x['sources']:
            assert s['url'].startswith('https://') and s['section_locator'] and s['supporting_passage'] and s['publication_or_revision_date'] and s['retrieved_at']=='2026-09-06'
            if 'pubmed.ncbi.nlm.nih.gov' not in s['url']:continue
            m=re.fullmatch(r'https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/',s['url']);assert m,s['url'];pmid=m.group(1)
            if pmid in expected:assert norm(expected[pmid])==norm(s['title'])
            expected[pmid]=s['title'];support[pmid]=s['supporting_passage']
    pmids=sorted(expected,key=int);u='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(pmids),'retmode':'xml'});xml=ET.fromstring(fetch_retry(u));found={}
    for art in xml.findall('.//PubmedArticle'):
        p=art.find('.//PMID');t=art.find('.//ArticleTitle')
        if p is None or t is None:continue
        pmid=''.join(p.itertext()).strip();title=''.join(t.itertext()).strip();ab=' '.join(''.join(a.itertext()).strip() for a in art.findall('.//Abstract/AbstractText'));found[pmid]=(title,ab)
    assert set(found)==set(pmids),(set(pmids)-set(found),set(found)-set(pmids))
    for pmid,title in expected.items():
        actual_title,ab=found[pmid];assert norm(actual_title)==norm(title),(pmid,actual_title,title);assert len(ab)>80,(pmid,'abstract')
        st=set(toks(support[pmid]));at=set(toks(actual_title+' '+ab));assert len(st&at)>=max(3,min(6,len(st)//3)),(pmid,st&at,support[pmid])

    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);assert con.execute('pragma integrity_check').fetchone()[0]=='ok';rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();con.close();assert len(rows)==1280
    old=[(cid,set(toks(text_item(json.loads(pj)))),material_text(json.loads(pj))) for cid,pj in rows];new=[(x['num'],set(toks(text_item(x)))) for x in items];maxc=(0,None,None);maxi=(0,None,None)
    for x in items:
        n=x['num']
        for a in ANCHORS[n]:
            hits=[cid for cid,_,mt in old if anchor_hit(mt,a)]
            assert not hits,(n,a,hits[:5])
    for n,nt in new:
        for cid,ot,_ in old:
            j=len(nt&ot)/max(1,len(nt|ot));
            if j>maxc[0]:maxc=(j,n,cid)
        for m,mt in new:
            if m>=n:continue
            j=len(nt&mt)/max(1,len(nt|mt));
            if j>maxi[0]:maxi=(j,n,m)
    assert maxc[0]<0.45,maxc;assert maxi[0]<0.40,maxi
    print(json.dumps({'status':'PASS','current_usmle_labels':'PASS_EXTERNALLY_VERIFIED_2026-09-06','official_url_locator':'PASS','pubmed_records_verified':len(pmids),'supporting_passage_abstract_binding':'PASS','evidence_contract':'PASS','material_anchor_collision_gate':'PASS','ncjmm':'NOT_APPLICABLE_USMLE','max_canonical_jaccard':maxc,'max_intra_batch_jaccard':maxi},ensure_ascii=False))
if __name__=='__main__':main()
