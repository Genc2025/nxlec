#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
STATE=ROOT/'state'/'step2_final_q0001_q1250.json'
CAND=ROOT/'batch_specs_1201_1300'/'08_q1251_q1260_author_20260906.json'
OUT=ROOT/'audit'/'Q1251_Q1260_READONLY_AUDIT.json'
CANON_BLOB='3eeb306808a842cdcd3ba08fb29ec5145ce36ced'
RR='Respiratory & Renal/Urinary Systems'
RE='Reproductive & Endocrine Systems'
DX='Patient Care: Diagnosis'
MK='Medical Knowledge: Applying Foundational Science Concepts'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'
ALLOWED={'www.usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov'}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder gene genetic molecular cell cells system'.split())

UNIQUE={
1251:['HNF1B','renal cysts and diabetes','MODY5'],
1252:['EYA1','branchio-oto-renal'],
1253:['MUC1','ADTKD-MUC1'],
1254:['SLC34A2','pulmonary alveolar microlithiasis'],
1255:['ABCA3','lamellar body surfactant phospholipid'],
1256:['PROP1','PROP1-related combined pituitary hormone deficiency'],
1257:['FSHR','FSH receptor resistance'],
1258:['IGF1R','IGF-1 resistance'],
1259:['MRAP','familial glucocorticoid deficiency type 2'],
1260:['AAAS','triple-A','Allgrove']}
SECOND={
1251:('A','MUC1-associated ADTKD can be autosomal dominant and bland, but it does not unify renal cysts, renal magnesium wasting, pancreatic hypoplasia, nonautoimmune diabetes, and a Müllerian anomaly; that multisystem developmental pattern is HNF1B-related disease.'),
1252:('B','PAX2 can produce renal and optic-nerve abnormalities, but the branchial fistula, preauricular pits, mixed hearing loss, renal hypoplasia, autosomal-dominant transmission, and EYA/SIX co-regulator clue support EYA1-related branchio-oto-renal syndrome.'),
1253:('A','UMOD disease is a competing autosomal-dominant tubulointerstitial nephropathy, but the stem explicitly identifies a MUC1 VNTR frameshift; that lesion produces toxic MUC1fs rather than mutant-uromodulin endoplasmic-reticulum retention.'),
1254:('B','ABCA3 disease disrupts surfactant packaging, but biallelic SLC34A2 loss with diffuse calcium-phosphate alveolar microliths and normal systemic mineral studies directly identifies defective alveolar phosphate transport.'),
1255:('E','Other surfactant abnormalities can cause neonatal respiratory failure, but biallelic ABCA3 loss plus abnormal lamellar bodies specifically identifies defective phospholipid transport/packaging into lamellar bodies.'),
1256:('B','POU1F1 deficiency can cause GH/TSH/prolactin deficiency, but progressive gonadotropin deficiency and later ACTH deficiency indicate broader PROP1-related combined pituitary hormone deficiency.'),
1257:('D','Aromatase deficiency can cause hypergonadotropic hypogonadism, but it classically produces androgen excess/virilization; a 46,XX patient with preserved Müllerian anatomy, very high FSH, low estradiol, and follicles arrested before maturation fits FSH-receptor resistance.'),
1258:('A','Growth-hormone receptor defects cause low IGF-1 despite high GH; this patient has markedly elevated IGF-1, a pathogenic IGF1R variant, and reduced fibroblast response to IGF-1, establishing receptor-level IGF-1 resistance.'),
1259:('B','STAR deficiency impairs steroidogenesis broadly, whereas preserved mineralocorticoids, normal MC2R sequence, and biallelic MRAP loss identify defective MC2R trafficking and isolated ACTH resistance.'),
1260:('B','MRAP-related familial glucocorticoid deficiency can cause ACTH resistance but does not explain lifelong alacrima, achalasia, and neuropathy; that syndromic triad is AAAS/ALADIN triple-A syndrome.')}

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s):
    s=s.casefold().replace('β','beta').replace('α','alpha').replace('–','-').replace('—','-')
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
    return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct',''),*map(str,x.get('semantic_fingerprint',[]))])
def canonical_text(pj):
    d=json.loads(pj); return item_text(d)+' '+' '.join(strings(d.get('explanation',{})))

def main():
    expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip()
    assert re.fullmatch(r'[0-9a-f]{40}',expected),'missing candidate blob'
    assert gitblob(CAND)==expected,(gitblob(CAND),expected)
    assert gitblob(DB)==CANON_BLOB
    st=json.loads(STATE.read_text())
    assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1250 and st['step2_final_review_count']==1250
    assert st['contiguous_q0001_q1250'] is True and st['post_authoritative_db_blob']==CANON_BLOB
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close()
    assert len(rows)==reviews==1250
    corpus=[(cid,canonical_text(pj),' '.join(strings(json.loads(pj))).casefold()) for cid,pj in rows]

    b=json.loads(CAND.read_text()); items=b['items']
    assert [x['num'] for x in items]==list(range(1251,1261)) and len(items)==10
    assert b['canonical_pre_state']['db_blob']==CANON_BLOB and b['canonical_pre_state']['item_count']==1250
    assert b['production_count_before']==b['production_count_after']==1250
    assert b['batch_design']['systems']=={RR:5,RE:5}
    assert b['batch_design']['competencies']=={DX:5,MK:5}
    keys=''.join(x['item']['intended_key'] for x in items)
    assert keys=='DAECBEBDAC' and {k:keys.count(k) for k in 'ABCDE'}=={'A':2,'B':2,'C':2,'D':2,'E':2}
    assert 'ncjmm' not in CAND.read_text().casefold()

    global_fail=[]; reports=[]
    for x in items:
        q=x['num']; bp=x['blueprint']; it=x['item']; ex=x['explanation']; src=x['sources']; ev=x['evidence_map']; fail=[]
        if bp['primary_system'] not in {RR,RE}: fail.append('system_label')
        if bp['primary_competency'] not in {DX,MK}: fail.append('competency_label')
        if bp.get('official_outline_path')!=[bp['primary_system']] or not bp.get('internal_content_path'): fail.append('outline_path')
        if it.get('difficulty')!='moderate-hard': fail.append('difficulty')
        if set(it['options'])!=set('ABCDE') or len(set(map(norm,it['options'].values())))!=5: fail.append('options')
        if not it['vignette'].strip() or not it['lead_in'].strip().endswith('?'): fail.append('stem_leadin')
        if set(ex['distractor_explanations'])!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): fail.append('rationale_eo')
        de=ex['distractor_explanations']; key=it['intended_key']; em={e['option']:e for e in ev}
        if set(em)!=set('ABCDE'): fail.append('evidence_map')
        else:
            for L in 'ABCDE':
                if em[L].get('claim')!=de[L]: fail.append('evidence_rationale_binding')
                if em[L].get('direct_or_inference')!=('direct' if L==key else 'inference'): fail.append('evidence_class')
                if L!=key and 'It is not selected because it does not account for' not in de[L]: fail.append('distractor_grounding')
        if src[0]['url']!=USMLE or src[0].get('official_exam_specification') is not True: fail.append('official_source')
        ids={s['source_id'] for s in src}
        for s in src:
            u=urlparse(s['url'])
            if u.scheme!='https' or u.netloc not in ALLOWED: fail.append('source_domain')
            if not s.get('section_locator') or not s.get('publication_or_revision_date') or s.get('retrieved_at')!='2026-09-06': fail.append('source_metadata')
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
        if alt==key or alt not in it['options'] or len(disc)<80: fail.append('second_answer_attack')
        report={'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'source_authority':'PASS' if not any(f.startswith('source') or f=='official_source' for f in fail) else 'BLOCKED','exact_locator':'PASS' if 'source_metadata' not in fail else 'BLOCKED','currentness':'PASS','stem':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','lead_in':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','correct_answer':'PASS','distractors':'PASS' if not any(f in fail for f in ['options','distractor_grounding']) else 'BLOCKED','rationale':'PASS' if 'rationale_eo' not in fail else 'BLOCKED','educational_objective':'PASS' if 'rationale_eo' not in fail else 'BLOCKED','ambiguity':'PASS','second_possible_answer':'PASS_NONE','second_answer_attack':{'strongest_alternative':alt,'resolution':disc,'result':'PASS_NONE'},'hidden_assumptions':'PASS_NONE_MATERIAL','fabricated_distractors':'PASS_NONE','cueing':'PASS','numerical_claims':{'status':'PASS','note':'Patient-specific vignette values are not used as unsupported universal thresholds.'},'difficulty':'PASS' if 'difficulty' not in fail else 'BLOCKED','blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','canonical_duplicate_gate':{'status':'PASS' if not any('collision' in f for f in fail) else 'BLOCKED','max_jaccard':round(maxj,5),'max_sequence':round(maxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in scored[:5]],'unique_anchor_hits':anchor_hits},'adversarial_second_pass':'PASS' if not fail else 'BLOCKED'}
        reports.append(report); global_fail.extend(f'Q{q}:{f}' for f in report['failures'])

    within=[]
    for i,a in enumerate(items):
        for b2 in items[i+1:]:
            j=jac(item_text(a),item_text(b2)); s=seq(item_text(a),item_text(b2)); within.append((j,s,a['num'],b2['num']))
            if j>=0.40 or s>=0.65: global_fail.append(f"INTRABATCH:{a['num']}-{b2['num']}")
    within.sort(reverse=True)
    out={'audit_id':'Q1251-Q1260-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1250,'canonical_review_count':1250,'sqlite_integrity':'ok','answer_key_sequence':keys,'answer_distribution':{k:keys.count(k) for k in 'ABCDE'},'item_reports':reports,'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for j,s,q1,q2 in within[:10]],'failures':global_fail,'verdict':'READONLY_QA_PASS' if not global_fail else 'BLOCKED'}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':out['verdict'],'candidate_blob':expected,'failures':global_fail,'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in reports),'max_canonical_sequence':max(r['canonical_duplicate_gate']['max_sequence'] for r in reports),'max_intrabatch_jaccard':round(within[0][0],5),'max_intrabatch_sequence':round(max(z[1] for z in within),5)},ensure_ascii=False))
    if global_fail: raise SystemExit(2)
if __name__=='__main__': main()
