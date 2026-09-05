#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1230.json'
BLOB='bbfff305e86386f8788e67ea60827416bfb9b3d6'
P={
'rbm20_dcm':['rbm20','rna binding motif protein 20','titin splicing'],
'pln_cardiomyopathy':['phospholamban','pln','serca inhibition'],
'bag3_dcm':['bag3','bcl2-associated athanogene 3','chaperone-assisted selective autophagy'],
'des_dcm':['desmin','des gene','intermediate filament cardiomyopathy'],
'flnc_cardiomyopathy':['filamin c','flnc','left-dominant arrhythmogenic'],
'hcn4':['hcn4','hyperpolarization-activated cyclic nucleotide-gated channel 4','sinus bradycardia left ventricular noncompaction'],
'nkx2_5':['nkx2-5','atrial septal defect atrioventricular block','cardiac transcription factor'],
'jph2':['junctophilin-2','jph2','t-tubule sarcoplasmic reticulum'],
'ryr2_exon3':['ryr2 exon 3','calcium release channel cardiomyopathy'],
'abcb4_pfic3':['abcb4','mdr3','pf ic3','pfic3','phosphatidylcholine floppase'],
'nr1h4_pfic5':['nr1h4','fxr','farnesoid x receptor','pfic5'],
'cldn1_nisc':['cldn1','neonatal ichthyosis sclerosing cholangitis','claudin-1'],
'slc51b_ost':['slc51b','organic solute transporter beta','ost beta','bile acid export enterocyte'],
'hsd3b7':['hsd3b7','3 beta hydroxy delta 5 c27 steroid oxidoreductase','bile acid synthesis defect'],
'kif12_cholestasis':['kif12','progressive familial intrahepatic cholestasis 8','kinesin family member 12'],
'usp53_cholestasis':['usp53','progressive familial intrahepatic cholestasis','tight junction cholestasis'],
'ttc37_the':['ttc37','trichohepatoenteric syndrome','phenotypic diarrhea'],
'skiv2l_the':['skiv2l','trichohepatoenteric syndrome','ski complex'],
'epcam_tufting':['epcam','congenital tufting enteropathy','epithelial cell adhesion molecule'],
'unc45a_diarrhea':['unc45a','congenital diarrhea cholestasis','myosin chaperone'],
'neurog3_diarrhea':['neurog3','neurogenin 3','enteric anendocrinosis','congenital malabsorptive diarrhea'],
'abhd12':['abhd12','pharc','phospholipase'],
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1230 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1230; con.close()
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
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**x} for cid,x in list(hits.items())[:10]]}
    print(json.dumps({'status':'PASS','count':1230,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
