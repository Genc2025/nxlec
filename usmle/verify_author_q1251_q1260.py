#!/usr/bin/env python3
from __future__ import annotations
import html as html_lib
import json,re,sqlite3,time,urllib.error,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BATCH=ROOT/'batch_specs_1201_1300'/'08_q1251_q1260_author_20260906.json'
DB=ROOT/'data'/'usmle-step1.db'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'

def norm(z): return re.sub(r'[^a-z0-9]+','',z.casefold())
def fetch_retry(url,user_agent,tries=6):
    err=None
    for attempt in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':user_agent,'Accept':'*/*'})
            with urllib.request.urlopen(req,timeout=45) as r: return r.read()
        except urllib.error.HTTPError as e:
            err=e
            if e.code not in {429,500,502,503,504}: raise
        except (urllib.error.URLError,TimeoutError) as e:
            err=e
        time.sleep(min(20,2**attempt))
    raise err

def toks(s):
    stop=set('a an the this that these those is are was were be been being to of in on at by for with from and or but as into due which what most likely patient patients his her their has have had shows show identifies identify'.split())
    return [w for w in re.findall(r'[a-z0-9]+',s.casefold()) if len(w)>2 and w not in stop]
def text_item(d):
    it=d.get('item',d)
    return ' '.join([it.get('vignette',''),it.get('lead_in',''),it.get('tested_construct','')]+list(it.get('options',{}).values()))

def main():
    b=json.loads(BATCH.read_text()); items=b['items']
    assert b['production_count_before']==b['production_count_after']==1250
    assert b['status']=='AUTHOR_ZERO_TRUST_PASS_PENDING_CANONICAL_DUPLICATE_AND_FINAL_QA'
    assert [x['num'] for x in items]==list(range(1251,1261)) and len(items)==10
    assert b['answer_key_sequence']=='DAECBEBDAC' and b['answer_key_distribution']=={'A':2,'B':2,'C':2,'D':2,'E':2}
    assert Counter(x['blueprint']['primary_system'] for x in items)==Counter({'Respiratory & Renal/Urinary Systems':5,'Reproductive & Endocrine Systems':5})
    assert Counter(x['blueprint']['primary_competency'] for x in items)==Counter({'Patient Care: Diagnosis':5,'Medical Knowledge: Applying Foundational Science Concepts':5})

    page=html_lib.unescape(fetch_retry(USMLE,'Mozilla/5.0 USMLE-QA/1.0').decode('utf-8','ignore'))
    for text in ['Respiratory & Renal/Urinary Systems','Reproductive & Endocrine Systems','Medical Knowledge: Applying Foundational Science Concepts','Patient Care: Diagnosis']:
        assert text in page,text

    expected_pubmed={}
    for x in items:
        n=x['num']; key=x['item']['intended_key']; de=x['explanation']['distractor_explanations']; em={e['option']:e for e in x['evidence_map']}
        assert list(x['item']['options'])==list('ABCDE') and len(set(x['item']['options'].values()))==5
        assert x['blueprint']['official_outline_path']==[x['blueprint']['primary_system']] and x['blueprint']['internal_content_path']
        assert set(de)==set(em)==set('ABCDE') and x['explanation']['key_explanation'] and x['explanation']['educational_objective']
        assert 'ncjmm' not in json.dumps(x).casefold()
        assert x['author_self_audit']['unresolved_concerns']==[] and x['author_self_audit']['suggested_changes']==[]
        for L in 'ABCDE':
            assert em[L]['claim']==de[L]
            assert em[L]['direct_or_inference']==('direct' if L==key else 'inference')
            assert em[L]['source_ids']
            if L!=key: assert 'It is not selected because it does not account for' in de[L]
        ids={s['source_id'] for s in x['sources']}
        for e in x['evidence_map']: assert set(e['source_ids']).issubset(ids)
        for s in x['sources']:
            assert s['url'].startswith('https://') and s['section_locator'] and s['supporting_passage'] and s['publication_or_revision_date']
            if 'pubmed.ncbi.nlm.nih.gov' not in s['url']: continue
            m=re.fullmatch(r'https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/',s['url']); assert m,s['url']; pmid=m.group(1)
            if pmid in expected_pubmed: assert norm(expected_pubmed[pmid])==norm(s['title'])
            expected_pubmed[pmid]=s['title']

    pmids=sorted(expected_pubmed,key=int)
    u='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(pmids),'retmode':'xml'})
    xml=ET.fromstring(fetch_retry(u,'USMLE-QA/1.0 contact=qa@example.invalid'))
    found={}
    for art in xml.findall('.//PubmedArticle'):
        p=art.find('.//PMID'); t=art.find('.//ArticleTitle')
        if p is None or t is None: continue
        pmid=''.join(p.itertext()).strip(); title=''.join(t.itertext()).strip()
        abstract=' '.join(''.join(a.itertext()).strip() for a in art.findall('.//Abstract/AbstractText'))
        found[pmid]=(title,abstract)
    assert set(pmids)==set(found),(sorted(set(pmids)-set(found)),sorted(set(found)-set(pmids)))
    for pmid,title_expected in expected_pubmed.items():
        title,abstract=found[pmid]
        assert norm(title)==norm(title_expected),(pmid,title,title_expected)
        assert len(abstract)>80,(pmid,'missing abstract')

    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); con.close(); assert len(rows)==1250
    old=[(cid,set(toks(text_item(json.loads(pj))))) for cid,pj in rows]
    new=[(x['num'],set(toks(text_item(x)))) for x in items]
    maxc=(0,None,None); maxi=(0,None,None)
    for n,nt in new:
        for cid,ot in old:
            j=len(nt&ot)/max(1,len(nt|ot))
            if j>maxc[0]: maxc=(j,n,cid)
        for m,mt in new:
            if m>=n: continue
            j=len(nt&mt)/max(1,len(nt|mt))
            if j>maxi[0]: maxi=(j,n,m)
    assert maxc[0]<0.45,maxc
    assert maxi[0]<0.45,maxi
    print(json.dumps({'status':'PASS','source_metadata':'PASS','current_usmle_labels':'PASS','pubmed_batch_title_locator':'PASS','pubmed_records_verified':len(pmids),'evidence_contract':'PASS','ncjmm':'NOT_APPLICABLE_USMLE','max_canonical_jaccard':maxc,'max_intra_batch_jaccard':maxi},ensure_ascii=False))
if __name__=='__main__': main()
