#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1240.json'
BLOB='ec4393c3699a68616ea2877b464916b0db680328'
P={
'pnpla1_arci':['pnpla1','patatin-like phospholipase domain-containing protein 1','autosomal recessive congenital ichthyosis pnpla1'],
'cyp4f22_arci':['cyp4f22','fatty acid omega-hydroxylase','acylceramide ichthyosis'],
'sdr9c7_arci':['sdr9c7','short chain dehydrogenase reductase family 9c member 7'],
'klhl24_ebs':['klhl24','kelch-like family member 24','epidermolysis bullosa simplex klhl24'],
'exph5_ebs':['exph5','exophilin 5','epidermolysis bullosa simplex exph5'],
'pkp1_skin_fragility':['pkp1','plakophilin 1','ectodermal dysplasia-skin fragility syndrome'],
'cdsn_peeling':['cdsn','corneodesmosin','peeling skin syndrome type 1'],
'lor_loricrin':['loricrin keratoderma','lor gene','loricrin'],
'kdsr_erythrokeratoderma':['kdsr','3-ketodihydrosphingosine reductase','progressive symmetric erythrokeratoderma'],
'pnpla2_nl':['pnpla2','adipose triglyceride lipase','neutral lipid storage disease with myopathy'],
'dsg1_sam':['severe dermatitis multiple allergies metabolic wasting','sam syndrome','dsg1'],
'flg_ichthyosis':['filaggrin','flg mutation','ichthyosis vulgaris'],
'plec_ebs_md':['plectin','plec mutation','epidermolysis bullosa simplex muscular dystrophy'],
'dst_ebs':['dystonin','dst mutation','epidermolysis bullosa simplex dystonin'],
'aebp1_eds':['aebp1','classical-like ehlers-danlos syndrome type 2','aortic carboxypeptidase-like protein'],
'b4galt7_eds':['b4galt7','spondylodysplastic ehlers-danlos syndrome b4galt7','galactosyltransferase i'],
'b3galt6_eds':['b3galt6','spondylodysplastic ehlers-danlos syndrome b3galt6','galactosyltransferase ii'],
'zip13_slc39a13':['slc39a13','zip13','spondylodysplastic ehlers-danlos syndrome slc39a13']
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
            for cid,item,text in corpus:
                if term.casefold() in text: hits[cid]={'tested_construct':item.get('tested_construct'),'lead_in':item.get('lead_in')}
            counts[term]=sum(1 for _,_,text in corpus if term.casefold() in text)
        out[name]={'unique_hit_count':len(hits),'by_term_counts':counts,'hits':[{'candidate_id':cid,**x} for cid,x in list(hits.items())[:12]]}
    print(json.dumps({'status':'PASS','count':1240,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
