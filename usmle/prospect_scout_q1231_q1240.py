#!/usr/bin/env python3
from __future__ import annotations
import json,re,sqlite3,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
STATE=ROOT/'state'/'step2_final_q0001_q1230.json'
EXPECTED_BLOB='bbfff305e86386f8788e67ea60827416bfb9b3d6'
PROSPECTS={
 'barh_tafazzin':['barh','barth syndrome','tafazzin','taz','cardiolipin remodeling','monolysocardiolipin'],
 'danon_lamp2':['danon','lamp2','lamp-2','autophagy','vacuolar myopathy'],
 'cpvt_ryr2':['catecholaminergic polymorphic','cpvt','ryr2','bidirectional ventricular tachycardia'],
 'prkag2':['prkag2','amp-activated protein kinase','glycogen cardiomyopathy','ventricular preexcitation'],
 'lmna_cardiomyopathy':['lmna','lamin a/c','nuclear lamina','dilated cardiomyopathy conduction disease'],
 'dsp_cardiomyopathy':['desmoplakin','dsp','desmosome cardiomyopathy','arrhythmogenic cardiomyopathy'],
 'ttr_amyloid':['transthyretin','ttr','amyloid cardiomyopathy','tetramer stabil'],
 'fabry_gla':['fabry','alpha-galactosidase a','gla','globotriaosylceramide'],
 'abcb11_bsep':['abcb11','bsep','bile salt export pump','progressive familial intrahepatic cholestasis type 2'],
 'atp8b1_pfic1':['atp8b1','familial intrahepatic cholestasis type 1','fic1','aminophospholipid'],
 'tjp2_cholestasis':['tjp2','tight junction protein 2','progressive familial intrahepatic cholestasis type 4'],
 'slc10a2_asbt':['slc10a2','asbt','apical sodium-dependent bile acid transporter','ileal bile acid transporter'],
 'sucrase_isomaltase':['sucrase-isomaltase','sucrase isomaltase','congenital sucrase-isomaltase deficiency','si gene'],
 'dgat1_diarrhea':['dgat1','diacylglycerol acyltransferase 1','protein-losing enteropathy congenital diarrhea'],
 'lipa_lal':['lysosomal acid lipase','lipa','cholesteryl ester storage','wolman disease'],
 'mtpp_abetalipo':['mttp','microsomal triglyceride transfer protein','abetalipoproteinemia','apo b-containing lipoproteins'],
 'npc1':['npc1','niemann-pick type c','lysosomal cholesterol trafficking','vertical gaze palsy'],
 'slc26a3_cld':['slc26a3','congenital chloride diarrhea','chloride bicarbonate exchanger','watery diarrhea metabolic alkalosis'],
 'myo5b_pfic6':['myo5b','microvillus inclusion disease','progressive familial intrahepatic cholestasis type 6'],
 'vps33b_arc':['vps33b','arc syndrome','arthrogryposis renal dysfunction cholestasis'],
 'apob_fhbl':['familial hypobetalipoproteinemia','apob','apo b truncation','hepatic steatosis low ldl'],
 'pcsk9_gof':['pcsk9 gain of function','pcsk9','familial hypercholesterolemia'],
 'scn5a_brugada':['scn5a','brugada','cardiac sodium channel'],
 'casq2_cpvt':['casq2','calsequestrin 2','catecholaminergic polymorphic'],
}

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def compact(item): return {'vignette':item.get('vignette'),'lead_in':item.get('lead_in'),'intended_key':item.get('intended_key'),'tested_construct':item.get('tested_construct')}

def main():
    s=json.loads(STATE.read_text())
    assert s['item_count']==1230 and s['contiguous_q0001_q1230'] is True
    assert s['post_authoritative_db_blob']==EXPECTED_BLOB and gitblob(DB)==EXPECTED_BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("SELECT candidate_id,payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    assert len(rows)==1230
    corpus=[]
    for cid,pj in rows:
        p=json.loads(pj); item=p.get('item',p); txt=' '.join(strings(p)).casefold()
        corpus.append((cid,item,txt))
    con.close()
    out={}
    for name,terms in PROSPECTS.items():
        by_term={}; union={}
        for term in terms:
            hits=[]; needle=term.casefold()
            for cid,item,txt in corpus:
                if needle in txt:
                    hits.append({'candidate_id':cid,'item':compact(item)})
                    union[cid]=compact(item)
            by_term[term]=hits
        out[name]={'unique_hit_count':len(union),'hits':[{"candidate_id":cid,'item':item} for cid,item in union.items()],'by_term_counts':{t:len(h) for t,h in by_term.items()}}
    print(json.dumps({'status':'PASS','canonical_count':1230,'db_blob':EXPECTED_BLOB,'prospects':out},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
