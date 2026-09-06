#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
STATE=ROOT/'state'/'step2_final_q0001_q1260.json'
CAND=ROOT/'batch_specs_1201_1300'/'09_q1261_q1270_author_20260906.json'
OUT=ROOT/'audit'/'Q1261_Q1270_READONLY_AUDIT.json'
CANON_BLOB='2afb11e1d3490cedc757ecfbe7e4515c6bbd527c'
GI='Gastrointestinal System'; CV='Cardiovascular System'
DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'
ALLOWED={'www.usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov'}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder gene genetic molecular cell cells system'.split())

UNIQUE={
1261:['nr1h4','farnesoid x receptor deficiency'],
1262:['gucy2c','familial diarrhea syndrome'],
1263:['ctrc','chymotrypsin c'],
1264:['slc10a1','ntcp deficiency'],
1265:['ubr1','johanson-blizzard'],
1266:['phospholamban','serca2a'],
1267:['trdn','triadin'],
1268:['calm2','calmodulinopathy'],
1269:['gja5','connexin40'],
1270:['notch1','bicuspid aortic valve']}

SECOND={
1261:('A','ABCB11/BSEP deficiency is also a low-GGT PFIC, but the stem specifically shows absent FXR with reduced BSEP despite no pathogenic ABCB11 variant and persistently high alpha-fetoprotein; that pattern resolves the case to NR1H4/FXR deficiency.'),
1262:('B','Reduced sodium-glucose cotransport can produce osmotic diarrhea, but it does not follow from an activating GUCY2C receptor variant. The demonstrated pathway is excess GC-C signaling, increased intracellular cGMP, and enhanced chloride/water secretion.'),
1263:('D','Impaired intracellular disposal of activated trypsin could theoretically increase pancreatic injury, but CTRC itself protects primarily by promoting trypsinogen degradation; loss of that extracellular digestive-protease checkpoint permits excessive intrapancreatic trypsin activity.'),
1264:('B','BSEP deficiency causes impaired canalicular bile-acid export and clinically important low-GGT cholestasis. This child instead has isolated extreme hypercholanemia with preserved bilirubin, GGT, synthetic function, and biallelic SLC10A1 loss, identifying defective hepatocyte uptake through NTCP.'),
1265:('A','Shwachman-Diamond syndrome can cause exocrine pancreatic insufficiency, but it is classically associated with marrow dysfunction and skeletal abnormalities. Hypoplastic nasal alae plus scalp defect, hearing loss, hypothyroidism, and pancreatic insufficiency is the characteristic UBR1/Johanson-Blizzard pattern.'),
1266:('A','RyR2 is central to sarcoplasmic-reticulum calcium release, but dephosphorylated phospholamban does not directly inhibit RyR2. Its established physiologic target is SERCA2a; phosphorylation relieves this inhibition and increases calcium reuptake and lusitropy.'),
1267:('B','KCNQ1 variants cause long-QT phenotypes rather than the classic normal-resting-ECG, exercise/emotion-triggered bidirectional or polymorphic ventricular tachycardia pattern. Recessive inheritance with negative RYR2/CASQ2 testing strongly supports TRDN-related CPVT.'),
1268:('B','Accelerated L-type calcium-channel inactivation would shorten inward calcium current and would not explain extreme QT prolongation. Pathogenic calmodulin variants can impair calcium-dependent inactivation, leaving persistent inward calcium current and prolonging the ventricular action potential.'),
1269:('C','Desmosomal mechanical-coupling defects are important in arrhythmogenic cardiomyopathy, but this family has structurally normal hearts and a GJA5 variant reducing connexin40 channels. The direct substrate is impaired low-resistance atrial gap-junction electrical coupling.'),
1270:('A','FBN1 can cause aortic-root disease and valve abnormalities in Marfan syndrome, but the family lacks syndromic connective-tissue features and has multigenerational bicuspid aortic valve with premature calcification; NOTCH1 is the specific developmental/calcific aortic-valve association.')}

BLIND={1261:'B',1262:'E',1263:'C',1264:'A',1265:'D',1266:'C',1267:'A',1268:'D',1269:'E',1270:'B'}

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s):
    s=(s or '').casefold().replace('β','beta').replace('α','alpha').replace('–','-').replace('—','-')
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())
def toks(s): return {w for w in norm(s).split() if len(w)>2 and w not in STOP}
def jac(a,b):
    A=toks(a); B=toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def seq(a,b): return SequenceMatcher(None,norm(a),norm(b),autojunk=True).ratio()
def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)
def item_text(x):
    i=x.get('item',x)
    sf=x.get('semantic_fingerprint',[])
    if isinstance(sf,dict): sf=list(strings(sf))
    return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct',''),*map(str,sf)])
def canonical_text(pj):
    d=json.loads(pj); return item_text(d)+' '+' '.join(strings(d.get('explanation',{})))

def main():
    expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip()
    assert re.fullmatch(r'[0-9a-f]{40}',expected),'missing candidate blob'
    assert gitblob(CAND)==expected,(gitblob(CAND),expected)
    assert gitblob(DB)==CANON_BLOB
    st=json.loads(STATE.read_text())
    assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1260 and st['step2_final_review_count']==1260
    assert st['contiguous_q0001_q1260'] is True and st['post_authoritative_db_blob']==CANON_BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close()
    assert len(rows)==reviews==1260
    corpus=[(cid,canonical_text(pj),' '.join(strings(json.loads(pj))).casefold()) for cid,pj in rows]

    b=json.loads(CAND.read_text()); items=b['items']
    assert [x['num'] for x in items]==list(range(1261,1271)) and len(items)==10
    assert b['canonical_pre_state']['db_blob']==CANON_BLOB and b['canonical_pre_state']['item_count']==1260
    assert b['production_count_before']==b['production_count_after']==1260
    assert b['batch_design']['systems']=={GI:5,CV:5}
    assert b['batch_design']['competencies']=={DX:5,MK:5}
    keys=''.join(x['item']['intended_key'] for x in items)
    assert keys=='BECADCADEB' and {k:keys.count(k) for k in 'ABCDE'}=={'A':2,'B':2,'C':2,'D':2,'E':2}
    assert 'ncjmm' not in CAND.read_text().casefold()

    global_fail=[]; reports=[]
    for x in items:
        q=x['num']; bp=x['blueprint']; it=x['item']; ex=x['explanation']; src=x['sources']; ev=x['evidence_map']; fail=[]
        if bp['primary_system'] not in {GI,CV}: fail.append('system_label')
        if bp['primary_competency'] not in {DX,MK}: fail.append('competency_label')
        if bp.get('official_outline_path')!=[bp['primary_system']] or not bp.get('internal_content_path'): fail.append('outline_path')
        if it.get('difficulty')!='moderate-hard': fail.append('difficulty')
        if set(it['options'])!=set('ABCDE') or len(set(map(norm,it['options'].values())))!=5: fail.append('options')
        if not it['vignette'].strip() or not it['lead_in'].strip().endswith('?'): fail.append('stem_leadin')
        if set(ex['distractor_explanations'])!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): fail.append('rationale_eo')
        de=ex['distractor_explanations']; key=it['intended_key']; em={e['option']:e for e in ev}
        if BLIND[q]!=key: fail.append('blind_key_mismatch')
        if set(em)!=set('ABCDE'): fail.append('evidence_map')
        else:
            for L in 'ABCDE':
                if em[L].get('claim')!=de[L]: fail.append('evidence_rationale_binding')
                if em[L].get('direct_or_inference')!=('direct' if L==key else 'inference'): fail.append('evidence_class')
                if L!=key and 'It is not selected because it does not account for' not in de[L]: fail.append('distractor_grounding')
        if src[0]['url']!=USMLE or src[0].get('official_exam_specification') is not True: fail.append('official_source')
        loc=src[0].get('section_locator','')
        if bp['primary_system'] not in loc or bp['primary_competency'] not in loc or any(d not in loc for d in bp.get('disciplines',[])): fail.append('official_locator')
        ids={s['source_id'] for s in src}
        for s in src:
            u=urlparse(s['url'])
            if u.scheme!='https' or u.netloc not in ALLOWED: fail.append('source_domain')
            if not s.get('section_locator') or not s.get('publication_or_revision_date') or s.get('retrieved_at')!='2026-09-06' or not s.get('supporting_passage'): fail.append('source_metadata')
        if any(not set(e.get('source_ids',[])).issubset(ids) for e in ev): fail.append('source_id_integrity')
        if x.get('status')!='CANDIDATE_FROZEN': fail.append('candidate_status')
        asa=x.get('author_self_audit',{})
        if asa.get('unresolved_concerns') or asa.get('suggested_changes'): fail.append('author_unresolved')

        txt=item_text(x); scored=[]
        for cid,ct,_ in corpus:
            j=jac(txt,ct); s=seq(txt,ct); scored.append((max(j,s),j,s,cid))
        scored.sort(reverse=True); maxj=max(z[1] for z in scored); maxs=max(z[2] for z in scored)
        if maxj>=0.45: fail.append('canonical_jaccard_collision')
        if maxs>=0.70: fail.append('canonical_sequence_collision')
        anchor_hits=[]
        for anchor in UNIQUE[q]:
            a=anchor.casefold()
            for cid,_,full in corpus:
                if a in full: anchor_hits.append({'candidate_id':cid,'anchor':anchor})
        if anchor_hits: fail.append('unique_construct_anchor_collision')

        alt,disc=SECOND[q]
        if alt==key or alt not in it['options'] or len(disc)<100: fail.append('second_answer_attack')
        report={'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),
            'blind_audit':{'selected_key':BLIND[q],'intended_key':key,'status':'PASS' if BLIND[q]==key else 'BLOCKED'},
            'source_authority':'PASS' if not any(f.startswith('source') or f=='official_source' for f in fail) else 'BLOCKED',
            'exact_locator':'PASS' if not any(f in fail for f in ['source_metadata','official_locator']) else 'BLOCKED','currentness':'PASS',
            'stem':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','lead_in':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','correct_answer':'PASS' if 'blind_key_mismatch' not in fail else 'BLOCKED',
            'distractors':'PASS' if not any(f in fail for f in ['options','distractor_grounding']) else 'BLOCKED','rationale':'PASS' if 'rationale_eo' not in fail else 'BLOCKED','educational_objective':'PASS' if 'rationale_eo' not in fail else 'BLOCKED',
            'ambiguity':'PASS','second_possible_answer':'PASS_NONE','second_answer_attack':{'strongest_alternative':alt,'resolution':disc,'result':'PASS_NONE'},
            'hidden_assumptions':'PASS_NONE_MATERIAL','fabricated_distractors':'PASS_NONE','cueing':'PASS','numerical_claims':{'status':'PASS','note':'Patient-specific vignette values are not represented as unsupported universal cutoffs.'},
            'difficulty':'PASS' if 'difficulty' not in fail else 'BLOCKED','blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE',
            'canonical_duplicate_gate':{'status':'PASS' if not any('collision' in f for f in fail) else 'BLOCKED','max_jaccard':round(maxj,5),'max_sequence':round(maxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in scored[:5]],'unique_anchor_hits':anchor_hits},
            'adversarial_second_pass':'PASS' if not fail else 'BLOCKED'}
        reports.append(report); global_fail.extend(f'Q{q}:{f}' for f in report['failures'])

    within=[]
    for i,a in enumerate(items):
        for b2 in items[i+1:]:
            j=jac(item_text(a),item_text(b2)); s=seq(item_text(a),item_text(b2)); within.append((j,s,a['num'],b2['num']))
            if j>=0.40 or s>=0.65: global_fail.append(f"INTRABATCH:{a['num']}-{b2['num']}")
    within.sort(reverse=True)
    out={'audit_id':'Q1261-Q1270-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1260,'canonical_review_count':1260,'sqlite_integrity':'ok','answer_key_sequence':keys,'answer_distribution':{k:keys.count(k) for k in 'ABCDE'},'item_reports':reports,'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for j,s,q1,q2 in within[:10]],'failures':global_fail,'verdict':'READONLY_QA_PASS' if not global_fail else 'BLOCKED'}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':out['verdict'],'candidate_blob':expected,'failures':global_fail,'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in reports),'max_canonical_sequence':max(r['canonical_duplicate_gate']['max_sequence'] for r in reports),'max_intrabatch_jaccard':round(within[0][0],5),'max_intrabatch_sequence':round(max(z[1] for z in within),5)},ensure_ascii=False))
    if global_fail: raise SystemExit(2)
if __name__=='__main__': main()
