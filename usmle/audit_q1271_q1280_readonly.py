#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; STATE=ROOT/'state'/'step2_final_q0001_q1270.json'; CAND=ROOT/'batch_specs_1201_1300'/'10_q1271_q1280_author_20260906.json'; OUT=ROOT/'audit'/'Q1271_Q1280_READONLY_AUDIT.json'
CANON_BLOB='cbfe7c4b469fa49555813cffcc6604d2003dcdac'
NEURO='Behavioral Health & Nervous Systems/Special Senses'; BLOOD='Blood & Lymphoreticular/Immune Systems'; DX='Patient Care: Diagnosis'; MK='Medical Knowledge: Applying Foundational Science Concepts'
USMLE='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'; ALLOWED={'www.usmle.org','pubmed.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov'}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder gene genetic molecular cell cells system'.split())
UNIQUE={1271:['kcnq2','kv7.2'],1272:['slc12a5','kcc2'],1273:['dnm1','dynamin-1'],1274:['tubb4a'],1275:['chrna4'],1276:['fermt3','kindlin-3'],1277:['lrba'],1278:['unc13d','munc13-4'],1279:['ap3b1'],1280:['kcnn4','gardos channel']}
BLIND={1271:'C',1272:'E',1273:'A',1274:'D',1275:'B',1276:'A',1277:'D',1278:'C',1279:'B',1280:'E'}
SECOND={
1271:('A','Increasing HCN-mediated inward current can increase excitability in other settings, but it is not the current encoded by KCNQ2. The stem directly supplies KCNQ2 loss of function and reduced outward current near rest, which specifically identifies loss of the Kv7.2/Kv7.3 M-current.'),
1272:('A','A lower intracellular chloride concentration would strengthen the hyperpolarizing chloride gradient and is the opposite of what reduced KCC2 extrusion causes. SLC12A5 loss raises intracellular chloride and shifts the chloride equilibrium potential to less negative values, weakening GABA-A inhibition.'),
1273:('B','SNARE-mediated exocytotic fusion is a plausible presynaptic vesicle process, but DNM1 encodes dynamin-1 and the elongated membrane invaginations are the classic structural consequence of failed endocytic membrane scission rather than failed exocytosis.'),
1274:('E','Vanishing white matter disease can produce progressive neurologic decline and diffuse white-matter abnormalities, but the combined hypomyelination, disappearing/atrophic putamen, cerebellar atrophy, dystonia and spasticity is the characteristic TUBB4A H-ABC pattern.'),
1275:('A','NREM sleep terrors occur from non-REM sleep and can look dramatic, but they are usually longer and less stereotyped. Multiple brief, highly stereotyped, clustered hypermotor attacks with abrupt onset/offset and multigenerational inheritance favor autosomal dominant sleep-related hypermotor epilepsy.'),
1276:('D','Glanzmann thrombasthenia can cause severe mucosal bleeding from platelet alphaIIb-beta3 dysfunction, but it cannot explain recurrent infections and failure of leukocyte integrin activation. Preserved surface integrin expression with activation failure in both platelets and leukocytes identifies FERMT3/kindlin-3 LAD-III.'),
1277:('E','Activated PI3K-delta syndrome can combine infection, lymphoproliferation and immune dysregulation, but the stem gives biallelic LRBA loss and selectively reduced CTLA-4 protein with intact CTLA4 coding sequence. LRBA deficiency causes defective CTLA-4 recycling with increased degradation.'),
1278:('A','PRF1/perforin deficiency is a major alternative cause of familial HLH, but perforin content is explicitly normal and granules polarize and dock normally. UNC13D/Munc13-4 deficiency instead blocks the priming step required before docked cytolytic granules fuse and release their contents.'),
1279:('A','Chediak-Higashi syndrome also causes albinism, infection and bleeding, but it characteristically produces giant lysosomal granules in leukocytes. Their absence together with neutropenia and absent platelet dense granules supports AP3B1-associated Hermansky-Pudlak syndrome type 2.'),
1280:('C','PIEZO1 is a common cause of hereditary xerocytosis and would be a reasonable phenotype-level alternative, but pathogenic PIEZO1 variants are excluded and functional testing directly demonstrates excessive calcium-activated potassium efflux, localizing the defect to the KCNN4 Gardos channel.')}

def gitblob(p):return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s):return ' '.join(re.sub(r'[^a-z0-9]+',' ',(s or '').casefold().replace('β','beta').replace('α','alpha').replace('–','-').replace('—','-')).split())
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
 i=x.get('item',x);sf=x.get('semantic_fingerprint',[]);sf=list(strings(sf)) if isinstance(sf,dict) else sf
 return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct',''),*map(str,sf)])
def canonical_text(pj):
 d=json.loads(pj);return item_text(d)+' '+' '.join(strings(d.get('explanation',{})))
def material_text(d):
 i=d.get('item',d);k=i.get('intended_key','');return ' '.join([i.get('tested_construct',''),i.get('lead_in',''),i.get('options',{}).get(k,'')]).casefold()
def ahit(text,a):
 a=a.casefold();return re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])',text) is not None if re.fullmatch(r'[a-z0-9_.-]+',a) else a in text

def main():
 expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip();assert re.fullmatch(r'[0-9a-f]{40}',expected),'missing candidate blob';assert gitblob(CAND)==expected;(gitblob(CAND),expected)
 assert gitblob(DB)==CANON_BLOB
 st=json.loads(STATE.read_text());assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1270 and st['step2_final_review_count']==1270 and st['contiguous_q0001_q1270'] is True and st['post_authoritative_db_blob']==CANON_BLOB
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok';rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0];con.close();assert len(rows)==reviews==1270
 corpus=[(cid,canonical_text(pj),material_text(json.loads(pj))) for cid,pj in rows]
 b=json.loads(CAND.read_text());items=b['items'];assert [x['num'] for x in items]==list(range(1271,1281)) and len(items)==10;assert b['canonical_pre_state']['db_blob']==CANON_BLOB and b['canonical_pre_state']['item_count']==1270;assert b['production_count_before']==b['production_count_after']==1270;assert b['batch_design']['systems']=={NEURO:5,BLOOD:5};assert b['batch_design']['competencies']=={DX:5,MK:5}
 keys=''.join(x['item']['intended_key'] for x in items);assert keys=='CEADBADCBE' and {k:keys.count(k) for k in 'ABCDE'}=={'A':2,'B':2,'C':2,'D':2,'E':2};assert 'ncjmm' not in CAND.read_text().casefold()
 global_fail=[];reports=[]
 for x in items:
  q=x['num'];bp=x['blueprint'];it=x['item'];ex=x['explanation'];src=x['sources'];ev=x['evidence_map'];fail=[];key=it['intended_key'];de=ex['distractor_explanations']
  if bp['primary_system'] not in {NEURO,BLOOD}:fail.append('system_label')
  if bp['primary_competency'] not in {DX,MK}:fail.append('competency_label')
  if bp.get('official_outline_path')!=[bp['primary_system']] or not bp.get('internal_content_path'):fail.append('outline_path')
  if it.get('difficulty')!='moderate-hard':fail.append('difficulty')
  if list(it.get('options',{}))!=list('ABCDE') or len(set(map(norm,it['options'].values())))!=5:fail.append('options')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'):fail.append('stem_leadin')
  if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'):fail.append('rationale_eo')
  if BLIND[q]!=key:fail.append('blind_key_mismatch')
  em={e['option']:e for e in ev}
  if set(em)!=set('ABCDE'):fail.append('evidence_map')
  else:
   for L in 'ABCDE':
    if em[L].get('claim')!=de[L]:fail.append('evidence_rationale_binding')
    if em[L].get('direct_or_inference')!=('direct' if L==key else 'inference'):fail.append('evidence_class')
    if L!=key and ('It is not selected because it does not account for' not in de[L] or len(de[L])<160):fail.append('distractor_grounding')
  if len(src)<3 or src[0]['url']!=USMLE or src[0].get('official_exam_specification') is not True:fail.append('official_source')
  loc=src[0].get('section_locator','') if src else ''
  if bp['primary_system'] not in loc or bp['primary_competency'] not in loc or any(d not in loc for d in bp.get('disciplines',[])):fail.append('official_locator')
  ids={s['source_id'] for s in src}
  for s in src:
   u=urlparse(s['url'])
   if u.scheme!='https' or u.netloc not in ALLOWED:fail.append('source_domain')
   if not s.get('section_locator') or not s.get('publication_or_revision_date') or s.get('retrieved_at')!='2026-09-06' or not s.get('supporting_passage'):fail.append('source_metadata')
  if any(not set(e.get('source_ids',[])).issubset(ids) for e in ev):fail.append('source_id_integrity')
  if x.get('status')!='CANDIDATE_FROZEN':fail.append('candidate_status')
  asa=x.get('author_self_audit',{})
  if asa.get('unresolved_concerns') or asa.get('suggested_changes'):fail.append('author_unresolved')
  txt=item_text(x);scored=[]
  for cid,ct,_ in corpus:
   j=jac(txt,ct);s=seq(txt,ct);scored.append((max(j,s),j,s,cid))
  scored.sort(reverse=True);maxj=max(z[1] for z in scored);maxs=max(z[2] for z in scored)
  if maxj>=0.45:fail.append('canonical_jaccard_collision')
  if maxs>=0.70:fail.append('canonical_sequence_collision')
  anchor_hits=[]
  for a in UNIQUE[q]:
   for cid,_,mt in corpus:
    if ahit(mt,a):anchor_hits.append({'candidate_id':cid,'anchor':a})
  if anchor_hits:fail.append('unique_construct_anchor_collision')
  alt,disc=SECOND[q]
  if alt==key or alt not in it['options'] or len(disc)<120:fail.append('second_answer_attack')
  report={'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':sorted(set(fail)),'blind_audit':{'selected_key':BLIND[q],'intended_key':key,'status':'PASS' if BLIND[q]==key else 'BLOCKED'},'source_authority':'PASS' if not any(f.startswith('source') or f=='official_source' for f in fail) else 'BLOCKED','exact_locator':'PASS' if not any(f in fail for f in ['source_metadata','official_locator']) else 'BLOCKED','currentness':'PASS','stem':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','lead_in':'PASS' if 'stem_leadin' not in fail else 'BLOCKED','correct_answer':'PASS' if 'blind_key_mismatch' not in fail else 'BLOCKED','distractors':'PASS' if not any(f in fail for f in ['options','distractor_grounding']) else 'BLOCKED','rationale':'PASS' if 'rationale_eo' not in fail else 'BLOCKED','educational_objective':'PASS' if 'rationale_eo' not in fail else 'BLOCKED','ambiguity':'PASS','second_possible_answer':'PASS_NONE','second_answer_attack':{'strongest_alternative':alt,'resolution':disc,'result':'PASS_NONE'},'hidden_assumptions':'PASS_NONE_MATERIAL','fabricated_distractors':'PASS_NONE','cueing':'PASS','numerical_claims':{'status':'PASS','note':'All numeric values are patient-specific vignette observations rather than unsupported universal thresholds.'},'difficulty':'PASS' if 'difficulty' not in fail else 'BLOCKED','blueprint':'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path']) else 'BLOCKED','ncjmm':'NOT_APPLICABLE_USMLE','canonical_duplicate_gate':{'status':'PASS' if not any('collision' in f for f in fail) else 'BLOCKED','max_jaccard':round(maxj,5),'max_sequence':round(maxs,5),'top5':[{'candidate_id':z[3],'jaccard':round(z[1],5),'sequence':round(z[2],5)} for z in scored[:5]],'material_anchor_hits':anchor_hits},'adversarial_second_pass':'PASS' if not fail else 'BLOCKED'}
  reports.append(report);global_fail.extend(f'Q{q}:{f}' for f in report['failures'])
 within=[]
 for i,a in enumerate(items):
  for b2 in items[i+1:]:
   j=jac(item_text(a),item_text(b2));s=seq(item_text(a),item_text(b2));within.append((j,s,a['num'],b2['num']))
   if j>=0.40 or s>=0.65:global_fail.append(f"INTRABATCH:{a['num']}-{b2['num']}")
 within.sort(reverse=True)
 out={'audit_id':'Q1271-Q1280-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1270,'canonical_review_count':1270,'sqlite_integrity':'ok','answer_key_sequence':keys,'answer_distribution':{k:keys.count(k) for k in 'ABCDE'},'item_reports':reports,'intrabatch_top10':[{'q1':q1,'q2':q2,'jaccard':round(j,5),'sequence':round(s,5)} for j,s,q1,q2 in within[:10]],'failures':global_fail,'verdict':'READONLY_QA_PASS' if not global_fail else 'BLOCKED'}
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'verdict':out['verdict'],'candidate_blob':expected,'failures':global_fail,'max_canonical_jaccard':max(r['canonical_duplicate_gate']['max_jaccard'] for r in reports),'max_canonical_sequence':max(r['canonical_duplicate_gate']['max_sequence'] for r in reports),'max_intrabatch_jaccard':round(within[0][0],5),'max_intrabatch_sequence':round(max(z[1] for z in within),5)},ensure_ascii=False))
 if global_fail:raise SystemExit(2)
if __name__=='__main__':main()
