#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1260.json'; BLOB='2afb11e1d3490cedc757ecfbe7e4515c6bbd527c'
P={
'atp8b1_pfic1':['atp8b1','fic1','progressive familial intrahepatic cholestasis type 1','pfic1'],
'abcb11_pfic2':['abcb11','bsep deficiency','bile salt export pump deficiency','pfic2'],
'abcb4_pfic3':['abcb4','mdr3 deficiency','pfic3','phosphatidylcholine floppase'],
'tjp2_pfic4':['tjp2','tight junction protein 2 cholestasis','pfic4'],
'nr1h4_pfic5':['nr1h4','fxr deficiency','pfic5','farnesoid x receptor deficiency'],
'myo5b_pfic6':['myo5b','pfic6','myosin vb cholestasis'],
'dgat1_diarrhea':['dgat1','diacylglycerol acyltransferase 1 deficiency','congenital diarrhea dgat1'],
'slc26a3_cld':['slc26a3','congenital chloride diarrhea','down-regulated in adenoma'],
'slc9a3_csd':['slc9a3','congenital sodium diarrhea','nhe3 deficiency'],
'tmprss15_enteropeptidase':['tmprss15','enteropeptidase deficiency','enterokinase deficiency'],
'gucy2c_diarrhea':['gucy2c','guanylate cyclase c activating mutation','familial diarrhea syndrome'],
'ttc37_the':['ttc37','trichohepatoenteric syndrome','tricho-hepato-enteric'],
'skiv2l_the':['skiv2l','trichohepatoenteric syndrome','ski complex diarrhea'],
'pln_dcm':['pln','phospholamban cardiomyopathy','pln r14del'],
'rbm20_dcm':['rbm20','rna binding motif protein 20 cardiomyopathy','rbm20 dilated cardiomyopathy'],
'bag3_dcm':['bag3','bcl2 associated athanogene 3 cardiomyopathy','bag3 dilated cardiomyopathy'],
'flnc_dcm':['flnc','filamin c dilated cardiomyopathy','filamin-c cardiomyopathy'],
'prkag2':['prkag2','prkag2 syndrome','glycogen storage cardiomyopathy wolff parkinson white'],
'hcn4':['hcn4','hyperpolarization activated cyclic nucleotide gated channel 4','sinus bradycardia left ventricular noncompaction'],
'casq2_cpvt':['casq2','calsequestrin 2','catecholaminergic polymorphic ventricular tachycardia type 2'],
'trdn_cpvt':['trdn','triadin','catecholaminergic polymorphic ventricular tachycardia triadin'],
'calm2_lqt':['calm2','calmodulin 2 long qt','calmodulinopathy'],
'ank2':['ank2','ankyrin-b syndrome','ankyrin b syndrome'],
'nkx2_5':['nkx2-5','nkx2.5','atrial septal defect atrioventricular block nkx'],
'tbx20':['tbx20','t-box transcription factor 20 congenital heart'],
'notch1_bav':['notch1','notch1 bicuspid aortic valve','notch1 aortic valve disease'],
'smad6_bav':['smad6','smad6 bicuspid aortic valve','smad6 aortic coarctation'],
'gja5_af':['gja5','connexin 40 atrial fibrillation','gap junction alpha 5 atrial fibrillation'],
'myl2_hcm':['myl2','myosin light chain 2 hypertrophic cardiomyopathy','regulatory myosin light chain hcm'],
'myl3_hcm':['myl3','myosin light chain 3 hypertrophic cardiomyopathy','essential myosin light chain hcm']
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['final_status']=='FINAL_10_10_PASS' and s['item_count']==1260 and s['step2_final_review_count']==1260 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1260; con.close()
    corpus=[]
    for cid,pj in rows:
        d=json.loads(pj); it=d.get('item',d); corpus.append((cid,it,' '.join(strings(d)).casefold()))
    out={}
    for name,terms in P.items():
        hits={}; counts={}
        for term in terms:
            ids=[]
            for cid,it,text in corpus:
                if term.casefold() in text:
                    ids.append(cid); hits[cid]={'tested_construct':it.get('tested_construct'),'lead_in':it.get('lead_in')}
            counts[term]=len(ids)
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**x} for cid,x in list(hits.items())[:10]]}
    print(json.dumps({'status':'PASS','count':1260,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
