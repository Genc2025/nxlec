#!/usr/bin/env python3
import json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1250.json'
BLOB='3eeb306808a842cdcd3ba08fb29ec5145ce36ced'
P={
'umod_adtkd':['adtkd-umod','autosomal dominant tubulointerstitial kidney disease','umod','uromodulin kidney disease'],
'hypomag_cldn16':['cldn16','claudin-16','familial hypomagnesemia with hypercalciuria and nephrocalcinosis'],
'drta_atp6v1b1':['atp6v1b1','distal renal tubular acidosis with deafness','v-type proton atpase b1'],
'drta_atp6v0a4':['atp6v0a4','v-type proton atpase a4','distal renal tubular acidosis hearing loss'],
'nephrogenic_di_slc14a2':['slc14a2','urea transporter b','ut-b deficiency'],
'nephronophthisis_nphp1':['nphp1','nephronophthisis 1','juvenile nephronophthisis'],
'pulm_microlithiasis_slc34a2':['slc34a2','pulmonary alveolar microlithiasis','type iib sodium phosphate cotransporter'],
'abca3_surfactant':['abca3','atp binding cassette a3','surfactant dysfunction abca3'],
'sftpc_ild':['sftpc','surfactant protein c deficiency','surfactant protein c associated interstitial lung disease'],
'foxf1_acdmpv':['foxf1','alveolar capillary dysplasia with misalignment of pulmonary veins','acdmpv'],
'flcn_bhd':['flcn','birt-hogg-dube','birt hogg dube'],
'cysltr1_aer':['cysteinyl leukotriene receptor 1','cysltr1'],
'nr0b1_ahc':['nr0b1','x-linked adrenal hypoplasia congenita','dax1','dax-1'],
'kiss1r_hh':['kiss1r','kisspeptin receptor','gpr54','kiss1 receptor'],
'tac3_hh':['tac3','neurokinin b deficiency','tachykinin 3'],
'tacr3_hh':['tacr3','neurokinin 3 receptor','nk3r deficiency'],
'gnrhr_hh':['gnrhr','gonadotropin releasing hormone receptor deficiency'],
'prop1_cpd':['prop1','prophet of pit-1','combined pituitary hormone deficiency prop1'],
'pou1f1_cpd':['pou1f1','pit-1 deficiency','pit1 deficiency','combined pituitary hormone deficiency pou1f1'],
'lhcgr_leydig':['lhcgr','leydig cell hypoplasia','luteinizing hormone receptor mutation'],
'fshr_resistance':['fshr','fsh receptor resistance','follicle stimulating hormone receptor mutation'],
'amh_pmds':['anti-mullerian hormone deficiency','amh mutation','persistent mullerian duct syndrome amh'],
'amhr2_pmds':['amhr2','anti-mullerian hormone receptor type 2','persistent mullerian duct syndrome amhr2'],
'cyp11a1_pai':['cyp11a1','cholesterol side chain cleavage deficiency','p450scc deficiency'],
'star_lipoid_cah':['star deficiency','steroidogenic acute regulatory protein','lipoid congenital adrenal hyperplasia'],
'por_deficiency':['p450 oxidoreductase deficiency','por deficiency','antley-bixler syndrome por'],
'igf1r_resistance':['igf1r','igf-1 receptor resistance','insulin-like growth factor 1 receptor mutation']
}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def main():
    s=json.loads(STATE.read_text()); assert s['item_count']==1250 and s['step2_final_review_count']==1250 and s['post_authoritative_db_blob']==BLOB and gitblob(DB)==BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); assert len(rows)==1250; con.close()
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
    print(json.dumps({'status':'PASS','count':1250,'db_blob':BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
