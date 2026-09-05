#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,re,sqlite3,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1230.json'
BATCH=ROOT/'batch_specs_1201_1300'/'06_q1231_q1240_author_20260906.json'
EXPECTED_BLOB='bbfff305e86386f8788e67ea60827416bfb9b3d6'
EXPECTED_KEYS={1231:'C',1232:'A',1233:'E',1234:'B',1235:'D',1236:'B',1237:'D',1238:'A',1239:'C',1240:'E'}
SYSTEMS={'Human Development','Respiratory and Renal/Urinary Systems','Blood, Lymphoreticular and Immune Systems','Behavioral Health, Nervous Systems and Special Senses','Musculoskeletal, Skin and Subcutaneous Tissue','Cardiovascular System','Gastrointestinal System','Reproductive and Endocrine Systems','Multisystem Processes and Disorders','Biostatistics, Epidemiology and Population Health','Social Sciences: Communication and Interpersonal Skills'}
DISC={'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology','Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'}
COMP={'Medical Knowledge: Applying Foundational Science Concepts','Patient Care: Diagnosis, including history and physical examination','Practice-Based Learning and Improvement','Communication and Interpersonal Skills'}
TERMS={
1231:['lmna','lamin a/c','conduction disease','pacemaker'],
1232:['bag3','chaperone-assisted selective autophagy','hsp70','proteostasis'],
1233:['hcn4','familial sinus bradycardia','left ventricular noncompaction'],
1234:['nkx2-5','homeobox','atrial septal defect','atrioventricular block'],
1235:['jph2','junctophilin-2','junctional complexes','t-tubule'],
1236:['atp8b1','pfic1','progressive familial intrahepatic cholestasis type 1','hearing loss'],
1237:['neurog3','enteric anendocrinosis','congenital malabsorptive diarrhea','enteroendocrine cells'],
1238:['vps33b','arc syndrome','arthrogryposis-renal dysfunction-cholestasis'],
1239:['slc51b','ost-beta','ostalpha-ostbeta','basolateral export'],
1240:['hsd3b7','3beta-hydroxy-delta5','bile acid synthesis defect']}
TOKEN=re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
STOP={'the','and','for','with','that','this','from','into','which','most','patient','patients','cell','cells','normal','shows','show','directly','findings','disease','disorder','diagnosis','genetic','testing','variant','variants','protein','function','gene'}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def text(x): return ' '.join(strings(x))
def toks(s): return [x for x in TOKEN.findall(s.casefold()) if len(x)>2 and x not in STOP]
def vec(ts,idf):
    c=Counter(ts); return {k:(1+math.log(v))*idf.get(k,1.0) for k,v in c.items()}
def cosine(a,b):
    if not a or not b:return 0.0
    n=sum(a[k]*b[k] for k in set(a)&set(b)); da=math.sqrt(sum(v*v for v in a.values())); db=math.sqrt(sum(v*v for v in b.values()))
    return n/(da*db) if da and db else 0.0
def compact(i): return {'vignette':i.get('vignette'),'lead_in':i.get('lead_in'),'options':i.get('options'),'intended_key':i.get('intended_key'),'tested_construct':i.get('tested_construct')}
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1230 and s['contiguous_q0001_q1230'] is True and s['post_authoritative_db_blob']==EXPECTED_BLOB and gitblob(DB)==EXPECTED_BLOB
    b=json.loads(BATCH.read_text()); assert b['production_count_before']==b['production_count_after']==1230
    docs={int(x['num']):x for x in b['items']}; assert set(docs)==set(range(1231,1241))
    validations={}; keys=[]
    for n,d in docs.items():
        i=d['item']; opts=i['options']; tags=d['blueprint']['disciplines']; src=d['sources']; ev=d['evidence_map']
        validations[f'Q{n}']={
          'candidate_frozen':d.get('status')=='CANDIDATE_FROZEN',
          'canonical_system':d['blueprint']['primary_system'] in SYSTEMS,
          'canonical_competency':d['blueprint']['primary_competency'] in COMP,
          'official_disciplines':bool(tags) and all(x in DISC for x in tags),
          'five_unique_options':list(opts)==list('ABCDE') and len(set(opts.values()))==5,
          'key_exact':i['intended_key']==EXPECTED_KEYS[n] and i['intended_key'] in opts,
          'explanations_all_options':set(d['explanation']['distractor_explanations'])==set('ABCDE') and bool(d['explanation']['key_explanation'].strip()) and bool(d['explanation']['educational_objective'].strip()),
          'evidence_all_options':{x.get('option') for x in ev}==set('ABCDE'),
          'source_minimum':len(src)>=2,
          'source_urls_locators':all(str(x.get('url','')).startswith('https://') and str(x.get('section_locator','')).strip() for x in src),
          'source_ids_unique':len({x.get('source_id') for x in src})==len(src),
          'ncjmm_absent':'ncjmm' not in text(d).casefold(),
          'no_production_permission':d.get('production_import_permitted') is not True,
          'self_audit_10':all(d.get('author_self_audit',{}).get(k)==10 for k in ['blueprint_fidelity','key_correctness','distractor_integrity','single_best_answer','reasoning_and_difficulty','item_writing','cueing_bias_fairness','evidence_quality','originality_duplication_rights','technical_integrity']),
          'self_audit_no_findings':d.get('author_self_audit',{}).get('unresolved_concerns')==[] and d.get('author_self_audit',{}).get('suggested_changes')==[]
        }
        if not all(validations[f'Q{n}'].values()): raise SystemExit(f'Q{n} validation fail {validations[f"Q{n}"]}')
        keys.append(i['intended_key'])
    assert Counter(keys)==Counter({'A':2,'B':2,'C':2,'D':2,'E':2})
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json,payload_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1230; con.close()
    prod=[]; mismatch=[]
    for cid,pj,ps in rows:
        d=json.loads(pj)
        if hobj(d)!=ps:mismatch.append(cid)
        i=d.get('item',d); prod.append({'candidate_id':cid,'item':i,'text':text(d)})
    assert not mismatch,mismatch
    term_hits={}
    for n,terms in TERMS.items():
        q=f'Q{n}'; term_hits[q]={}
        for term in terms:
            hits=[]; needle=term.casefold()
            for r in prod:
                if needle in r['text'].casefold(): hits.append({'candidate_id':r['candidate_id'],'item':compact(r['item'])})
            term_hits[q][term]=hits
    pt=[toks(r['text']) for r in prod]; N=len(pt); df=Counter()
    for ts in pt: df.update(set(ts))
    idf={t:math.log((N+1)/(v+1))+1 for t,v in df.items()}; pv=[vec(ts,idf) for ts in pt]
    nearest={}; cv={}; ct={}
    for n,d in docs.items():
        ts=toks(text(d)); v=vec(ts,idf); cv[n]=v; ct[n]=ts; st=set(ts); scored=[]
        for r,pts,pvv in zip(prod,pt,pv):
            sc=cosine(v,pvv); ov=sorted(st&set(pts),key=lambda x:idf.get(x,0),reverse=True)[:20]; scored.append((sc,r,ov))
        scored.sort(key=lambda x:x[0],reverse=True)
        nearest[f'Q{n}']=[{'candidate_id':r['candidate_id'],'tfidf_cosine':round(sc,6),'overlap':ov,'item':compact(r['item'])} for sc,r,ov in scored[:15]]
    within=[]
    for a in range(1231,1241):
        for b2 in range(a+1,1241):
            sc=cosine(cv[a],cv[b2])
            if sc>=0.15: within.append({'a':f'Q{a}','b':f'Q{b2}','tfidf_cosine':round(sc,6),'overlap':sorted(set(ct[a])&set(ct[b2]),key=lambda x:idf.get(x,0),reverse=True)[:20]})
    within.sort(key=lambda x:x['tfidf_cosine'],reverse=True)
    print(json.dumps({'status':'RETRIEVAL_AUDIT_COMPLETE_REQUIRES_ADVERSARIAL_REVIEW','canonical_count':1230,'authoritative_db_blob':EXPECTED_BLOB,'batch_blob':gitblob(BATCH),'batch_object_sha256':hobj(b),'answer_key_distribution':dict(Counter(keys)),'candidate_validation':validations,'term_hits':term_hits,'nearest_neighbours':nearest,'within_batch_similarity':within,'production_db_modified':False},indent=2,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
