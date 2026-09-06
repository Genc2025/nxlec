#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1240.json'
BLOB='ec4393c3699a68616ea2877b464916b0db680328'
P={
'whim_cxcr4':['whim syndrome','cxcr4 gain of function','myelokathexis'],
'gata2_monomac':['gata2 deficiency','monomac','dendritic cell monocyte b nk deficiency'],
'dada2':['deficiency of adenosine deaminase 2','ada2 deficiency','dada2','cecr1'],
'lrba_ctla4':['lrba deficiency','lipopolysaccharide responsive beige like anchor','ctla4 recycling'],
'ctla4_haplo':['ctla4 haploinsufficiency','ctla-4 haploinsufficiency'],
'pik3cd_apds':['activated pi3k delta syndrome','pik3cd','apds'],
'nfkb2_david':['nfkb2','david syndrome','deficient anterior pituitary variable immune deficiency'],
'plcg2_plaid':['plaid syndrome','plcg2 associated antibody deficiency','plcg2'],
'card11_benta':['benta disease','card11 gain of function','card11'],
'xiap_xlp2':['xiap deficiency','x-linked lymphoproliferative syndrome type 2','xlp2'],
'sh2d1a_xlp1':['sh2d1a','sap deficiency','x-linked lymphoproliferative disease type 1'],
'c1q_sle':['c1q deficiency','hereditary c1q deficiency'],
'fermt1_kindler':['fermt1','kindler syndrome','kindlin-1'],
'atp2c1_hailey':['atp2c1','hailey-hailey disease','secretory pathway calcium manganese atpase'],
'atp2a2_darier':['atp2a2','darier disease','serca2'],
'spink5_netherton':['spink5','netherton syndrome','lekti'],
'abcc6_pxe':['abcc6','pseudoxanthoma elasticum'],
'tnxb_eds':['tnxb','tenascin-x','classical-like ehlers-danlos'],
'fkbp14_eds':['fkbp14','kyphoscoliotic ehlers-danlos'],
'chst14_eds':['chst14','musculocontractural ehlers-danlos','dermatan 4-o-sulfotransferase'],
'slc39a13_eds':['slc39a13','spondylodysplastic ehlers-danlos','zip13'],
'lemd3_bos':['lemd3','buschke-ollendorff syndrome','osteopoikilosis elastoma'],
'dsg1_sam':['dsg1','severe dermatitis multiple allergies metabolic wasting','sam syndrome'],
'tgm1_ichthyosis':['tgm1','lamellar ichthyosis','transglutaminase 1']
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1240 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1240; con.close()
    corpus=[]
    for cid,pj in rows:
        d=json.loads(pj); item=d.get('item',d); corpus.append((cid,item,' '.join(strings(d)).casefold()))
    out={}
    for name,terms in P.items():
        hits={}; counts={}
        for term in terms:
            ids=[]
            for cid,item,text in corpus:
                if term.casefold() in text:
                    ids.append(cid); hits[cid]={'tested_construct':item.get('tested_construct'),'lead_in':item.get('lead_in')}
            counts[term]=len(ids)
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**x} for cid,x in list(hits.items())[:12]]}
    print(json.dumps({'status':'PASS','count':1240,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
