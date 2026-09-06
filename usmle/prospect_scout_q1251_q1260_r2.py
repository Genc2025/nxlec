#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1250.json'; BLOB='3eeb306808a842cdcd3ba08fb29ec5145ce36ced'
P={
'muc1_adtkd':['muc1','adtkd-muc1','mucin-1 kidney disease','muc1 frameshift'],
'ren_adtkd':['ren mutation','adtkd-ren','renin precursor mutation','autosomal dominant tubulointerstitial kidney disease ren'],
'sec61a1_adtkd':['sec61a1','adtkd-sec61a1','sec61 translocon kidney disease'],
'pax2_rcs':['pax2','renal coloboma syndrome','papillorenal syndrome'],
'eya1_bor':['eya1','branchio-oto-renal syndrome'],
'hnf1b_rcad':['hnf1b','renal cysts and diabetes','rcad syndrome'],
'coq8b_nephrotic':['coq8b','adck4','coenzyme q10 nephropathy'],
'inf2_fsgs':['inf2','inverted formin 2','fsgs charcot-marie-tooth'],
'lama5_ns':['lama5','laminin alpha 5 nephrotic syndrome'],
'tbx19_acth':['tbx19','t-pit','isolated acth deficiency','tpit deficiency'],
'ghrhr_ghd':['ghrhr','growth hormone releasing hormone receptor deficiency'],
'igfals_def':['igfals','acid-labile subunit deficiency','als deficiency growth hormone'],
'papss2':['papss2','apparent cortisone reductase deficiency','spondyloepimetaphyseal dysplasia pakistani type'],
'cyp19a1_aromatase':['cyp19a1 deficiency','aromatase deficiency','aromatase gene deficiency'],
'hsd17b2':['hsd17b2','17-beta-hydroxysteroid dehydrogenase type 2'],
'nr5a2':['nr5a2 endocrine','liver receptor homolog-1'],
'mrap_familial_gc':['mrap','melanocortin 2 receptor accessory protein','familial glucocorticoid deficiency type 2'],
'aaas_triple_a':['aaas gene','alacrima achalasia adrenal insufficiency','triple a syndrome'],
'pcsk1_def':['pcsk1 deficiency','proprotein convertase 1/3 deficiency','pc1/3 deficiency'],
'prokr2_hh':['prokr2','prokineticin receptor 2 hypogonadotropic hypogonadism'],
'semaphorin3a_hh':['sema3a','semaphorin 3a kallmann'],
'il17rd_hh':['il17rd','interleukin 17 receptor d kallmann'],
'hs6st1_hh':['hs6st1','heparan sulfate 6-o-sulfotransferase 1 hypogonadotropic']
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1250 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1250; con.close()
    corpus=[]
    for cid,pj in rows:
        d=json.loads(pj); item=d.get('item',d); corpus.append((cid,item,' '.join(strings(d)).casefold()))
    out={}
    for name,terms in P.items():
        hits={}; counts={}
        for term in terms:
            for cid,item,text in corpus:
                if term.casefold() in text: hits[cid]={'tested_construct':item.get('tested_construct'),'lead_in':item.get('lead_in')}
            counts[term]=sum(1 for _,_,text in corpus if term.casefold() in text)
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**x} for cid,x in list(hits.items())[:12]]}
    print(json.dumps({'status':'PASS','count':1250,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
