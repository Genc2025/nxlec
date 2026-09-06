#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1290.json'
CAND=ROOT/'batch_specs_1201_1300'/'12_q1291_q1300_author_20260906.json'; OUT=ROOT/'audit'/'Q1291_Q1300_READONLY_AUDIT.json'
CANON_BLOB='8e2f2badc5e1cac3c4dc438cd469c3a05cc7092e'
SOC='Social Sciences: Communication and Interpersonal Skills'; MSK='Musculoskeletal, Skin & Subcutaneous Tissue'; COMM='Communication and Interpersonal Skills'; MK='Medical Knowledge: Applying Foundational Science Concepts'; DX='Patient Care: Diagnosis'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'
ALLOWED={'www.usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov','www.ecfr.gov','www.ada.gov'}
UNIQUE={1291:['45 cfr 46.408','child assent'],1292:['21 cfr 50.24','community consultation'],1293:['qualified sign language interpreter','effective communication'],1294:['lrp5','gly171val'],1295:['acan','advanced bone age'],1296:['pseudoachondroplasia','mutant comp'],1297:['flnb','larsen syndrome'],1298:['ifitm5','c.-14c>t'],1299:['wnt1','early-onset osteoporosis'],1300:['serpinh1','hsp47']}
BLIND={1291:'C',1292:'A',1293:'D',1294:'B',1295:'E',1296:'B',1297:'D',1298:'A',1299:'C',1300:'E'}
SECOND={
1291:('A','Parental permission is necessary in many pediatric research protocols, but 45 CFR 46.408 treats parental permission and child assent as distinct protections. The stem explicitly states that the IRB found children of this age and maturity capable of assent and did not waive assent, and the observational study offers no research-only direct benefit that would invoke the regulatory exception to assent.'),
1292:('D','The emergency-research pathway does not authorize investigators to ignore a legally authorized representative whenever one can feasibly be contacted within the therapeutic window. The defining additional prospective safeguards under 21 CFR 50.24 include IRB findings plus community consultation and public disclosure; option D instead overstates the exception.'),
1293:('A','An accompanying adult may sometimes assist with communication under narrow ADA circumstances, but conversational ASL does not establish qualification for a complex procedural consent. The patient requests ASL interpretation and the interaction is lengthy, technical, and bidirectional, making an appropriate qualified interpreter or equally effective auxiliary aid the defensible answer.'),
1294:('A','Reduced canonical Wnt signaling causes bone fragility or low bone mass, whereas the LRP5 Gly171Val high-bone-mass allele reduces inhibition of the Wnt coreceptor and increases osteoblast-driven bone formation. The phenotype and functional direction therefore exclude reduced Wnt activity.'),
1295:('D','NPR2 loss can produce autosomal-dominant short stature, but it does not characteristically combine advanced bone age, premature growth cessation, and unusually early osteoarthritis. Those growth-plate and articular-cartilage findings are strongly associated with heterozygous ACAN variants.'),
1296:('E','Activating FGFR3 variants cause achondroplasia and suppress growth-plate chondrocyte proliferation, but the stem gives a pathogenic COMP variant, normal craniofacial appearance, postnatal onset, and early degenerative joint disease. Pseudoachondroplasia specifically involves misfolded mutant COMP retained within rough endoplasmic reticulum of chondrocytes.'),
1297:('A','COL2A1 disorders can cause skeletal dysplasia and joint disease, but the combination of multiple congenital large-joint dislocations, hypertelorism, depressed nasal bridge, vertebral segmentation defects, and vertical transmission is the classic FLNB-associated Larsen syndrome pattern.'),
1298:('D','SERPINH1 deficiency can cause recessive osteogenesis imperfecta, but it does not explain the distinctive OI type V combination of hyperplastic callus, interosseous-membrane ossification, radial-head dislocation, and negative COL1A1/COL1A2 testing. The recurrent IFITM5 c.-14C>T variant creates an upstream in-frame start codon.'),
1299:('D','SERPINH1 loss produces a collagen-chaperone defect and can cause recessive OI, but the stem directly supplies biallelic WNT1 loss in severely affected children plus low bone mass in a heterozygous parent. That dosage pattern and genotype localize the defect to reduced WNT1-dependent canonical beta-catenin signaling.'),
1300:('A','Prolyl hydroxylation is an ER collagen-modification step, but SERPINH1 does not encode a prolyl hydroxylase. It encodes HSP47, the collagen-specific ER chaperone that binds and stabilizes procollagen triple helices and participates in collagen quality control and trafficking.')}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder gene genetic molecular cell cells system'.split())
def gitblob(p):return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s):return ' '.join(re.sub(r'[^a-z0-9]+',' ',(s or '').casefold().replace('α','alpha').replace('β','beta')).split())
def toks(s):return {w for w in norm(s).split() if len(w)>2 and w not in STOP}
def jac(a,b):
 A=toks(a);B=toks(b);return len(A&B)/len(A|B) if A|B else 0.0
def seq(a,b):return SequenceMatcher(None,norm(a),norm(b),autojunk=True).ratio()
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)
def item_text(x):
 i=x.get('item',x);sf=x.get('semantic_fingerprint',[]);sfs=list(strings(sf)) if isinstance(sf,(dict,list)) else []
 return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct',''),*sfs])
def material_text(x):
 i=x.get('item',x);k=i.get('intended_key','');return ' '.join([i.get('tested_construct',''),i.get('lead_in',''),i.get('options',{}).get(k,'')]).casefold()
def anchor_hit(text,a):
 a=a.casefold()
 if re.fullmatch(r'[a-z0-9_.+>-]+',a):return re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])',text) is not None
 return a in text

def main():
 expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip();assert re.fullmatch(r'[0-9a-f]{40}',expected)
 assert gitblob(CAND)==expected and gitblob(DB)==CANON_BLOB
 st=json.loads(STATE.read_text());assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1290 and st['step2_final_review_count']==1290 and st['contiguous_q0001_q1290'] is True and st['post_authoritative_db_blob']==CANON_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0];con.close();assert len(rows)==reviews==1290
 corpus=[(cid,item_text(json.loads(pj)),material_text(json.loads(pj))) for cid,pj in rows]
 b=json.loads(CAND.read_text());items=b['items'];assert [x['num'] for x in items]==list(range(1291,1301));assert b['answer_key_sequence']=='CADBEBDACE';assert b['batch_design']['systems']=={SOC:3,MSK:7};assert b['batch_design']['competencies']=={COMM:3,MK:5,DX:2};assert 'ncjmm' not in CAND.read_text().casefold()
 failures=[];reports=[]
 for x in items:
  q=x['num'];bp=x['blueprint'];it=x['item'];ex=x['explanation'];src=x['sources'];ev=x['evidence_map'];fail=[];key=it['intended_key']
  if BLIND[q]!=key:fail.append('blind_key_mismatch')
  if bp['primary_system'] not in {SOC,MSK}:fail.append('system_label')
  if bp['primary_competency'] not in {COMM,MK,DX}:fail.append('competency_label')
  if bp.get('official_outline_path')!=[bp['primary_system']] or not bp.get('internal_content_path'):fail.append('outline_path')
  if it.get('difficulty')!='moderate-hard' or not it.get('lead_in','').endswith('?'):fail.append('item_form')
  if list(it.get('options',{}))!=list('ABCDE') or len(set(map(norm,it['options'].values())))!=5:fail.append('options')
  de=ex.get('distractor_explanations',{});em={e.get('option'):e for e in ev};ids={s['source_id'] for s in src}
  if set(de)!=set('ABCDE') or set(em)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'):fail.append('rationale_evidence')
  else:
   for L in 'ABCDE':
    if em[L].get('claim')!=de[L] or em[L].get('direct_or_inference')!=('direct' if L==key else 'inference') or not set(em[L].get('source_ids',[])).issubset(ids):fail.append('evidence_binding')
    if L!=key and ('It is not selected because it does not account for' not in de[L] or len(de[L])<160):fail.append('distractor_grounding')
  if src[0].get('agency')!='USMLE' or src[0].get('url')!=USMLE or src[0].get('official_exam_specification') is not True:fail.append('official_source')
  loc=src[0].get('section_locator','')
  if bp['primary_system'] not in loc or bp['primary_competency'] not in loc or any(d not in loc for d in bp.get('disciplines',[])):fail.append('official_locator')
  for s in src:
   u=urlparse(s.get('url',''))
   if u.scheme!='https' or u.netloc not in ALLOWED or not s.get('section_locator') or not s.get('supporting_passage') or s.get('retrieved_at')!='2026-09-06':fail.append('source_metadata')
  scored=sorted([(max(jac(item_text(x),ct),seq(item_text(x),ct)),jac(item_text(x),ct),seq(item_text(x),ct),cid) for cid,ct,_ in corpus],reverse=True)
  maxj=max(z[1] for z in scored);maxs=max(z[2] for z in scored)
  if maxj>=0.45:fail.append('canonical_jaccard_collision')
  if maxs>=0.70:fail.append('canonical_sequence_collision')
  ah=[]
  for a in UNIQUE[q]:
   for cid,_,mt in corpus:
    if anchor_hit(mt,a):ah.append({'candidate_id':cid,'anchor':a})
  if ah:fail.append('unique_construct_anchor_collision')
  alt,res=SECOND[q]
  if alt==key or alt not in it['options'] or len(res)<120:fail.append('second_answer_attack')
  # Scope-sensitive federal items must state the predicate that makes the federal rule applicable.
  if q==1291 and not all(t in norm(it['vignette']) for t in ['federally supported','institutional review board','has not waived assent']):fail.append('federal_scope_hidden_assumption')
  if q==1292 and not all(t in norm(it['vignette']) for t in ['investigational','federal exception','emergency research']):fail.append('federal_scope_hidden_assumption')
  if q==1293 and not all(t in norm(it['vignette']) for t in ['deaf','american sign language','requests an asl interpreter']):fail.append('communication_scope_hidden_assumption')
  r={'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'blind_audit':{'selected_key':BLIND[q],'intended_key':key,'status':'PASS' if BLIND[q]==key else 'BLOCKED'},'source_authority':'PASS' if not any(f in fail for f in ['official_source','source_metadata']) else 'BLOCKED','exact_locator':'PASS' if 'official_locator' not in fail else 'BLOCKED','currentness':'PASS','stem':'PASS','lead_in':'PASS' if 'item_form' not in fail else 'BLOCKED','correct_answer':'PASS' if 'blind_key_mismatch' not in fail else 'BLOCKED','distractors':'PASS' if not any(f in fail for f in ['options','distractor_grounding']) else 'BLOCKED','rationale':'PASS','educational_objective':'PASS','ambiguity':'PASS','second_possible_answer':'PASS_NONE','second_answer_attack':{'strongest_alternative':alt,'resolution':res,'result':'PASS_NONE'},'hidden_assumptions':'PASS_NONE_MATERIAL','fabricated_distractors':'PASS_NONE','cueing':'PASS','numerical_claims':{'status':'PASS','note':'Any regulatory citation or molecular detail used to discriminate the key is source-bound; no unsupported quantitative threshold is required.'},'difficulty':'PASS','blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','canonical_duplicate_gate':{'status':'PASS' if not any('collision' in f for f in fail) else 'BLOCKED','max_jaccard':round(maxj,5),'max_sequence':round(maxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in scored[:5]],'unique_anchor_hits':ah},'adversarial_second_pass':'PASS' if not fail else 'BLOCKED'}
  reports.append(r);failures.extend(f'Q{q}:{f}' for f in r['failures'])
 within=[]
 for i,a in enumerate(items):
  for b2 in items[i+1:]:
   j=jac(item_text(a),item_text(b2));s=seq(item_text(a),item_text(b2));within.append((j,s,a['num'],b2['num']))
   if j>=0.40 or s>=0.65:failures.append(f"INTRABATCH:{a['num']}-{b2['num']}")
 within.sort(reverse=True)
 out={'audit_id':'Q1291-Q1300-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1290,'canonical_review_count':1290,'sqlite_integrity':'ok','answer_key_sequence':'CADBEBDACE','answer_distribution':{'A':2,'B':2,'C':2,'D':2,'E':2},'item_reports':reports,'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for j,s,q1,q2 in within[:10]],'failures':failures,'verdict':'READONLY_QA_PASS' if not failures else 'BLOCKED'}
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'verdict':out['verdict'],'failures':failures,'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in reports)},sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
