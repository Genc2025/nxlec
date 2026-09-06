#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1260.json'; BLOB='2afb11e1d3490cedc757ecfbe7e4515c6bbd527c'
P={
'slc10a1_ntcp':['slc10a1','ntcp deficiency','sodium taurocholate cotransporting polypeptide deficiency'],
'usp53_cholestasis':['usp53','usp53 cholestasis','tight junction cholestasis usp53'],
'kif12_pfic':['kif12','kinesin family member 12 cholestasis','pfic kif12'],
'zfyve19_pfic':['zfyve19','zinc finger fyve-type containing 19 cholestasis','pfic zfyve19'],
'scyl1_calfan':['scyl1','calfan syndrome','low gamma gt recurrent liver failure scyl1'],
'nbas_liver':['nbas','neuroblastoma amplified sequence recurrent acute liver failure','soph syndrome'],
'lars1_ilfs':['lars1','infantile liver failure syndrome 1','leucyl-trna synthetase 1 liver failure'],
'akrd1_bile':['akr1d1','5 beta reductase deficiency bile acid','delta4-3-oxosteroid 5beta-reductase deficiency'],
'baat_bile':['baat','bile acid-coa amino acid n-acyltransferase deficiency','bile acid conjugation defect'],
'slc27a5_bile':['slc27a5','bile acid coa ligase deficiency','very long-chain acyl-coa synthetase homolog 2'],
'cldn1_nisch':['cldn1','neonatal ichthyosis sclerosing cholangitis','nischn syndrome'],
'ctrc_pancreatitis':['ctrc','chymotrypsin c chronic pancreatitis','ctrc pancreatitis'],
'cpa1_pancreatitis':['cpa1','carboxypeptidase a1 chronic pancreatitis','cpa1 endoplasmic reticulum stress'],
'cel_mody8':['cel gene','mody8','carboxyl ester lipase diabetes pancreatic exocrine dysfunction'],
'ubr1_jbs':['ubr1','johanson-blizzard syndrome','ubiquitin protein ligase e3 component n-recognin 1'],
'ctrb1_ctrb2':['ctrb1','ctrb2','chymotrypsin b1 b2 pancreatitis'],
'casr_pancreatitis':['casr pancreatitis','calcium sensing receptor chronic pancreatitis']
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1260 and s['step2_final_review_count']==1260 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1260; con.close()
    corpus=[]
    for cid,pj in rows:
        d=json.loads(pj); it=d.get('item',d); corpus.append((cid,it,' '.join(strings(d)).casefold()))
    out={}
    for name,terms in P.items():
        hits={}; counts={}
        for term in terms:
            n=0
            for cid,it,text in corpus:
                if term.casefold() in text:
                    n+=1; hits[cid]={'tested_construct':it.get('tested_construct'),'lead_in':it.get('lead_in')}
            counts[term]=n
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**v} for cid,v in list(hits.items())[:10]]}
    print(json.dumps({'status':'PASS','count':1260,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
