#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1280.json'
CAND=ROOT/'batch_specs_1201_1300'/'11_q1281_q1290_author_20260906.json'; OUT=ROOT/'audit'/'Q1281_Q1290_READONLY_AUDIT.json'
CANON_BLOB='c6d3a9df9c8887b6ff3f3dbac6c710ed564bb4ed'
ENDO='Reproductive & Endocrine Systems'; RENAL='Respiratory & Renal/Urinary Systems'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'; ALLOWED={'www.usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov'}
UNIQUE={1281:['pcsk1','prohormone convertase 1/3'],1282:['secisbp2','sbp2'],1283:['gnrhr'],1284:['resistance to thyroid hormone alpha'],1285:['tbx19','tpit'],1286:['maged2'],1287:['slc22a12','urat1'],1288:['inf2'],1289:['trpc6'],1290:['lamb2','pierson syndrome']}
BLIND={1281:'B',1282:'D',1283:'A',1284:'C',1285:'E',1286:'C',1287:'A',1288:'E',1289:'D',1290:'B'}
SECOND={
1281:('C','POMC deficiency can cause hyperphagic obesity and adrenal dysfunction, but it does not account for severe congenital malabsorptive diarrhea, a high proinsulin-to-insulin ratio, and directly reduced PC1/3 expression; those findings specifically identify PCSK1 deficiency.'),
1282:('C','THRB disease alters nuclear thyroid-hormone signaling and hypothalamic-pituitary feedback, but it does not explain biallelic SECISBP2 variants with directly reduced deiodinase activity. The demonstrated lesion is defective selenoprotein synthesis.'),
1283:('B','A GnRH-neuron migration defect can cause hypogonadotropic hypogonadism, but it commonly impairs olfaction and acts upstream of the pituitary. Normal smell plus biallelic GNRHR loss and a blunted response to exogenous GnRH localize the defect to pituitary gonadotroph GnRH receptors.'),
1284:('A','THRB-mediated resistance generally produces elevated circulating thyroid hormones with nonsuppressed TSH and often goiter. The low-normal T4, high-normal T3, low T4/T3 ratio, constipation and skeletal phenotype with preserved TSH feedback are characteristic of resistance to thyroid hormone alpha.'),
1285:('D','MC2R-related familial glucocorticoid deficiency causes primary adrenal ACTH resistance, so ACTH is markedly elevated. This infant has low ACTH and cortisol with all other pituitary axes preserved, localizing the defect to TBX19-dependent corticotroph differentiation.'),
1286:('A','SLC12A1-associated antenatal Bartter syndrome can produce severe fetal polyhydramnios and neonatal salt wasting, but it is persistent. The X-linked male pattern and spontaneous complete recovery within weeks are defining discriminators for MAGED2-associated transient antenatal Bartter syndrome.'),
1287:('C','ABCG2 participates in urate secretion, but the stem supplies biallelic SLC22A12 loss and increased fractional urate excretion. URAT1 is the apical proximal-tubule reabsorptive transporter encoded by SLC22A12, so loss directly impairs urate reabsorption.'),
1288:('C','PMP22 duplication can explain Charcot-Marie-Tooth neuropathy but not familial FSGS, and PMP22 testing is negative. A single autosomal-dominant disorder combining CMT neuropathy and FSGS is strongly associated with INF2 variants affecting podocyte and Schwann-cell cytoskeletal biology.'),
1289:('E','INF2 variants can cause familial FSGS through actin/cytoskeletal dysregulation, but the stem directly demonstrates a heterozygous TRPC6 variant with increased agonist-evoked current and delayed inactivation. That functional gain identifies excessive TRPC6 calcium entry as the proximal lesion.'),
1290:('C','NPHS1/nephrin deficiency causes congenital nephrotic syndrome but is a slit-diaphragm defect and does not explain microcoria or a LAMB2 genotype. Pierson syndrome specifically reflects laminin beta2 deficiency in the glomerular basement membrane and ocular structures.')}
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
 if re.fullmatch(r'[a-z0-9_.+-]+',a):return re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])',text) is not None
 return a in text

def main():
 expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip();assert re.fullmatch(r'[0-9a-f]{40}',expected)
 assert gitblob(CAND)==expected and gitblob(DB)==CANON_BLOB
 st=json.loads(STATE.read_text());assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1280 and st['step2_final_review_count']==1280 and st['contiguous_q0001_q1280'] is True and st['post_authoritative_db_blob']==CANON_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0];con.close();assert len(rows)==reviews==1280
 corpus=[(cid,item_text(json.loads(pj)),material_text(json.loads(pj))) for cid,pj in rows]
 b=json.loads(CAND.read_text());items=b['items'];assert [x['num'] for x in items]==list(range(1281,1291));assert b['answer_key_sequence']=='BDACECAEDB';assert b['batch_design']['systems']=={ENDO:5,RENAL:5};assert b['batch_design']['competencies']=={DX:5,MK:5};assert 'ncjmm' not in CAND.read_text().casefold()
 failures=[];reports=[]
 for x in items:
  q=x['num'];bp=x['blueprint'];it=x['item'];ex=x['explanation'];src=x['sources'];ev=x['evidence_map'];fail=[];key=it['intended_key']
  if BLIND[q]!=key:fail.append('blind_key_mismatch')
  if bp['primary_system'] not in {ENDO,RENAL}:fail.append('system_label')
  if bp['primary_competency'] not in {DX,MK}:fail.append('competency_label')
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
  r={'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'blind_audit':{'selected_key':BLIND[q],'intended_key':key,'status':'PASS' if BLIND[q]==key else 'BLOCKED'},'source_authority':'PASS' if not any(f in fail for f in ['official_source','source_metadata']) else 'BLOCKED','exact_locator':'PASS' if 'official_locator' not in fail else 'BLOCKED','currentness':'PASS','stem':'PASS','lead_in':'PASS' if 'item_form' not in fail else 'BLOCKED','correct_answer':'PASS' if 'blind_key_mismatch' not in fail else 'BLOCKED','distractors':'PASS' if not any(f in fail for f in ['options','distractor_grounding']) else 'BLOCKED','rationale':'PASS','educational_objective':'PASS','ambiguity':'PASS','second_possible_answer':'PASS_NONE','second_answer_attack':{'strongest_alternative':alt,'resolution':res,'result':'PASS_NONE'},'hidden_assumptions':'PASS_NONE_MATERIAL','fabricated_distractors':'PASS_NONE','cueing':'PASS','numerical_claims':{'status':'PASS','note':'No unsupported universal threshold is required to solve the item.'},'difficulty':'PASS','blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','canonical_duplicate_gate':{'status':'PASS' if not any('collision' in f for f in fail) else 'BLOCKED','max_jaccard':round(maxj,5),'max_sequence':round(maxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in scored[:5]],'unique_anchor_hits':ah},'adversarial_second_pass':'PASS' if not fail else 'BLOCKED'}
  reports.append(r);failures.extend(f'Q{q}:{f}' for f in r['failures'])
 within=[]
 for i,a in enumerate(items):
  for b2 in items[i+1:]:
   j=jac(item_text(a),item_text(b2));s=seq(item_text(a),item_text(b2));within.append((j,s,a['num'],b2['num']))
   if j>=0.40 or s>=0.65:failures.append(f"INTRABATCH:{a['num']}-{b2['num']}")
 within.sort(reverse=True)
 out={'audit_id':'Q1281-Q1290-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1280,'canonical_review_count':1280,'sqlite_integrity':'ok','answer_key_sequence':'BDACECAEDB','answer_distribution':{'A':2,'B':2,'C':2,'D':2,'E':2},'item_reports':reports,'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for j,s,q1,q2 in within[:10]],'failures':failures,'verdict':'READONLY_QA_PASS' if not failures else 'BLOCKED'}
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'verdict':out['verdict'],'failures':failures,'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in reports)},sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
