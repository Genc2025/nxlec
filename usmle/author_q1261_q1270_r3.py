#!/usr/bin/env python3
from __future__ import annotations
import json,sqlite3
import author_q1261_q1270 as a
from collections import Counter

_orig_make=a.make

def make_fixed(n,system,comp,path,disc,coverage,vignette,lead,options,key,keyexp,obj,anchor,pubs,fingerprint,steps=4):
    return _orig_make(n,system,comp,path,disc,coverage,vignette,lead,options,key,coverage,keyexp,obj,anchor,pubs,fingerprint,steps)

a.make=make_fixed

def replacement_q1266():
    return make_fixed(
      1266,a.CV,a.MK,
      ['Cardiac muscle','Cytoskeletal and intercalated-disc integrity in arrhythmogenic cardiomyopathy'],
      ['Pathology','Genetics','Histology & Cell Biology'],
      'FLNC truncating-variant arrhythmogenic cardiomyopathy with myocardial fibrosis and cell-cell adhesion disruption',
      'A 39-year-old man is evaluated after several episodes of sustained ventricular tachycardia. Cardiac magnetic resonance imaging shows mild left ventricular dilation with extensive subepicardial and midmyocardial late gadolinium enhancement. His mother died suddenly at age 44, and a maternal uncle has dilated cardiomyopathy. He has no skeletal muscle weakness. Genetic testing identifies a heterozygous truncating variant in FLNC.',
      'Which myocardial abnormality is most consistent with this genotype?',
      {'A':'Diffuse glycogen accumulation within cardiomyocytes with ventricular preexcitation','B':'Selective loss of cardiac ryanodine receptors causing impaired systolic calcium release','C':'Reduced filamin C with disruption of cytoskeletal/cell-cell adhesion structures and fibrotic remodeling','D':'Abnormal titin isoform splicing caused by loss of an RNA-binding splicing factor','E':'Desmin-positive skeletal-muscle aggregates with primary myofibrillar myopathy as the obligatory phenotype'},
      'C',
      'Truncating FLNC variants can produce a predominantly cardiac arrhythmogenic dilated-cardiomyopathy phenotype with ventricular arrhythmias, sudden-death risk, myocardial fibrosis/fibrofatty change, and abnormalities of cell-cell adhesion/intercalated-disc structures. The mechanism is consistent with reduced functional filamin C from truncation/haploinsufficiency rather than a primary ion-channel or glycogen-storage defect.',
      'Truncating FLNC variants can cause cardiac-restricted arrhythmogenic dilated cardiomyopathy characterized by myocardial fibrosis and disruption of cytoskeletal/intercalated-disc integrity, creating a substrate for ventricular arrhythmias.',
      'familial ventricular arrhythmias, left-ventricular fibrosis, a truncating FLNC variant, and absence of an obligatory skeletal-myopathy phenotype',
      [a.S(1266,2,'Filamin C Truncation Mutations Are Associated With Arrhythmogenic Dilated Cardiomyopathy and Changes in the Cell-Cell Adhesion Structures','30067491','2018','FLNC truncation carriers showed ventricular arrhythmias/sudden death, fibrosis or fibrofatty infiltration, and altered cell-cell adhesion structures including reduced desmoplakin and SAP97.'),
       a.S(1266,3,'Truncating FLNC Mutations Are Associated With High-Risk Dilated and Arrhythmogenic Cardiomyopathies','27908349','2016','Truncating FLNC variants are associated with a high-risk dilated/arrhythmogenic cardiomyopathy phenotype, frequent ventricular arrhythmias and sudden cardiac death, often without skeletal-muscle disease.')],
      ['FLNC','filamin C truncating variant','arrhythmogenic dilated cardiomyopathy','myocardial fibrosis','cell-cell adhesion'],4)

def custom_anchor_scan(items):
    con=sqlite3.connect(a.DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); con.close()
    assert len(rows)==1260
    corpus='\n'.join(pj.casefold() for (pj,) in rows)
    anchors=['nr1h4','gucy2c','ctrc','slc10a1','ubr1','flnc','trdn','calm2','gja5','notch1']
    for anchor in anchors:
        if anchor in corpus:
            raise SystemExit('canonical tested-anchor collision '+anchor)

def main():
    st=json.loads(a.STATE.read_text())
    if st.get('final_status')!='FINAL_10_10_PASS' or st.get('item_count')!=1260 or st.get('step2_final_review_count')!=1260 or st.get('post_authoritative_db_blob')!=a.PRE_BLOB or st.get('contiguous_q0001_q1260') is not True:
        raise SystemExit('Q1260 binding')
    if a.gitblob(a.DB)!=a.PRE_BLOB: raise SystemExit('DB blob')
    items=a.build()
    items=[replacement_q1266() if x['num']==1266 else x for x in items]
    a.validate(items)
    custom_anchor_scan(items)
    seq=''.join(x['item']['intended_key'] for x in items)
    assert seq=='BECADCADEB' and Counter(seq)==Counter({'A':2,'B':2,'C':2,'D':2,'E':2})
    b={'batch_id':'Q1261-Q1270-20260906-AUTHOR-R3','production_count_before':1260,'production_count_after':1260,'status':'AUTHOR_ZERO_TRUST_PASS_PENDING_CANONICAL_DUPLICATE_AND_FINAL_QA','created_at':'2026-09-06','country_scope':'United States','specification_version':'USMLE Step 1 current official specifications verified 2026-09-06','canonical_pre_state':{'item_count':1260,'db_blob':a.PRE_BLOB,'state_file':'usmle/state/step2_final_q0001_q1260.json'},'batch_design':{'systems':{a.GI:5,a.CV:5},'competencies':{a.DX:5,a.MK:5},'reason':'Current USMLE-aligned GI/Cardiovascular deficit coverage after canonical prospect scans and replacement of a detected true construct duplicate before FINAL QA.'},'answer_key_distribution':dict(sorted(Counter(x['item']['intended_key'] for x in items).items())),'answer_key_sequence':'BECADCADEB','items':items}
    a.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','output':str(a.OUT.relative_to(a.REPO)),'items':10,'keys':'BECADCADEB','canonical_blob':a.PRE_BLOB,'q1266_replacement':'FLNC'},sort_keys=True))

if __name__=='__main__': main()
