"""Apply reviewed Q0004 corrections without carrying forward a FINAL verdict."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CID='S1-DIRECT-0004-20260827T020000Z'
EXPECTED='46d491155b1452a3b2e9b03b09ba2d83cd2f8a19970f0d6ec6daa4c17cac4f86'
AUDIT='Q0004_CLINICAL_FOLLOWUP_20260920'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()

def src(i,title,url,date,locator,summary,sha,record='audit/live_20260919/SOURCE_AVAILABILITY.json',bytes_=None):
 d={'source_id':i,'title':title,'url':url,'agency':'National Library of Medicine (NIH) — MedlinePlus Genetics' if 'medlineplus' in url else 'National Heart, Lung, and Blood Institute (NIH)','government_status_verified':True,'publication_or_revision_date':date,'retrieved_at':'2026-09-20','section_locator':locator,'supporting_passage':summary,'passage_type':'Reviewer paraphrase, not a verbatim quotation','raw_source_sha256':sha,'raw_capture_record':record,'set_id_applicability':'NOT_APPLICABLE_NON_DRUG_SOURCE','rights_status':'Official U.S. federal health-information source; facts used for original synthesis.'}
 if bytes_ is not None:d['raw_capture_bytes']=bytes_
 return d

def main():
 db=sqlite3.connect(ROOT/'data/usmle-step1.db');db.row_factory=sqlite3.Row
 ap=ROOT/'remediation'/(AUDIT+'_BEFORE_ROWS.json')
 with db:
  db.execute('BEGIN IMMEDIATE')
  old=dict(db.execute('select * from step2_final_items where candidate_id=?',(CID,)).fetchone());rev=dict(db.execute('select * from step2_final_reviews where candidate_id=?',(CID,)).fetchone());p=json.loads(old['payload_json'])
  if p.get('current_reaudit',{}).get('audit_id')==AUDIT:
   assert digest(p)==old['payload_sha256'] and ap.exists();print('Already applied; no rows changed');return
  assert old['payload_sha256']==EXPECTED==digest(p)
  p['blueprint'].update(coverage_deficit_addressed='Sickle cell disease: deoxygenation-dependent hemoglobin S polymerization and acute erythrocyte deformation.',disciplines=['Biochemistry','Genetics'],primary_system='Blood & Lymphoreticular System',official_outline_path=['Blood & Lymphoreticular System','Anemia, cytopenias, and polycythemia anemias','Disorders of hemoglobin, heme, or membrane','Sickle cell disease'])
  p['item'].update(difficulty='easy',reasoning_steps_count=2,difficulty_basis='Author estimate, not psychometrically calibrated: the diagnosis and sickled cells are given; the examinee must connect deoxygenation during exertion/dehydration with HbS polymerization. No calculation or differential diagnosis is required.',options={'A':'Reduced synthesis of alpha-globin chains','B':'Loss of red-cell membrane structural proteins','C':'Reduced G6PD-dependent NADPH production with oxidant injury','D':'Impaired ALAS2-dependent heme synthesis','E':'Polymerization of deoxygenated hemoglobin S'},tested_construct='Low-oxygen conditions promote hemoglobin S assembly into rigid intracellular strands, acutely deforming erythrocytes and promoting vaso-occlusion.')
  r={
   'A':'Incorrect. Reduced alpha-globin synthesis causes alpha thalassemia, with decreased alpha-globin production and abnormal tetramers; it does not cause deoxygenation-triggered HbS polymerization.',
   'B':'Incorrect. Hereditary spherocytosis results from red-cell membrane-protein defects that reduce membrane stability and produce spherical cells removed by the spleen, not acute sickling during deoxygenation.',
   'C':'Incorrect. G6PD deficiency reduces NADPH-dependent protection from reactive oxygen species and causes oxidant hemolysis. It does not create HbS strands or the deoxygenation-dependent shape change shown here.',
   'D':'Incorrect. ALAS2 dysfunction impairs heme production and causes X-linked sideroblastic anemia with microcytosis and iron-loaded ring sideroblasts, not acute erythrocyte sickling.',
   'E':'Correct. Under low-oxygen conditions, hemoglobin S forms stiff intracellular strands. These assemblies distort erythrocytes into rigid sickle shapes that can obstruct small vessels and cause acute pain.'}
  p['explanation']={'key_explanation':r['E'],'distractor_explanations':r,'educational_objective':'Distinguish deoxygenation-dependent HbS polymerization from alpha-globin underproduction, membrane-protein defects, oxidant injury, and impaired heme synthesis as mechanisms of red-cell disease.'}
  ids={'A':['S4'],'B':['S5'],'C':['S6'],'D':['S7'],'E':['S1','S2','S3']};dx={'A':'Alpha thalassemia','B':'Hereditary spherocytosis','C':'G6PD deficiency','D':'X-linked sideroblastic anemia','E':'Sickle cell disease'}
  p['evidence_map']=[{'option':o,'claim':t,'rationale':r[o],'source_ids':ids[o],'evidence_basis':'LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION','audit_record':'audit/'+AUDIT+'.md','target_diagnosis_or_process':dx[o],'target_mechanism':t} for o,t in p['item']['options'].items()]
  p['sources']=[
   src('S1','Sickle cell disease','https://medlineplus.gov/genetics/condition/sickle-cell-disease/','Last updated March 14, 2024','Description; Causes','HbS distorts red cells; sickled cells are rigid, obstruct small vessels, and cause pain.','7ae0662873da2af18d2714ee9ea953b3b8a4b1008d58d11882d268bc345b833c'),
   src('S2','HBB gene','https://medlineplus.gov/genetics/gene/hbb/','Last updated March 14, 2024','Normal Function; Health Conditions Related to Genetic Changes — Sickle cell disease','The HBB Glu6Val variant makes HbS subunits adhere into long rigid molecules that bend red cells and obstruct vessels.','fbae7ccefbc91b9263dbe4b3bd067f32ca29a162afb1e7afa99192b2fb60aa2b'),
   src('S3','Sickle Cell Disease Causes and Risk Factors','https://www.nhlbi.nih.gov/health/sickle-cell-disease/causes','Last updated August 20, 2024','What is a “sickled” cell?','Under low oxygen, HbS forms stiff strands that change red-cell shape and impair blood flow.','1cd09db6bc36ce18706f73a1a1cce108179956a90bdd0fcf6c65f3b5cbc0ba46','audit/'+AUDIT+'.md',85872),
   src('S4','Alpha thalassemia','https://medlineplus.gov/genetics/condition/alpha-thalassemia/','Last updated December 2, 2022','Description; Causes','HBA1/HBA2 loss or alteration reduces alpha-globin production and can produce Hb Bart or HbH.','2b6f3fe4e9431046daa2b4fba236cb4226cf36a0f1a7bdf119fac69264530611'),
   src('S5','Hereditary spherocytosis','https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/','Last updated September 1, 2013','Description; Causes','Red-cell membrane-protein defects produce rigid spherical cells removed by the spleen.','78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b'),
   src('S6','G6PD gene','https://medlineplus.gov/genetics/gene/g6pd/','Last updated April 12, 2023','Normal Function; Glucose-6-phosphate dehydrogenase deficiency','G6PD generates NADPH that protects red cells from reactive oxygen species; deficiency permits oxidant hemolysis.','b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655'),
   src('S7','X-linked sideroblastic anemia','https://medlineplus.gov/genetics/condition/x-linked-sideroblastic-anemia/','Last updated September 19, 2025','Description; Causes','ALAS2 dysfunction disrupts heme production, lowers hemoglobin, and produces iron-loaded ring sideroblasts.','d54d5c90d3a0c3fd149c3e9e7c405cc121fcd671d2079661aa36f9e5ddce7501','audit/'+AUDIT+'.md',37889)]
  p['semantic_fingerprint'].update(correct_answer_concept=p['item']['options']['E'],mechanism=p['item']['tested_construct'],tested_construct=p['item']['tested_construct'],reasoning_chain=['Recognize an acute sickling episode under conditions favoring deoxygenation.','Identify deoxygenated HbS polymerization as the direct cause of erythrocyte deformation.'],distractor_misconceptions=['confusing globin-chain underproduction with polymerization','confusing membrane instability with HbS sickling','confusing oxidant hemolysis with deoxygenation-dependent deformation','confusing impaired heme synthesis with HbS polymerization'])
  hist=p.setdefault('historical_audit_metadata',{})
  for f in ('author_self_audit','step2_final_audit','hashes'):
   if f in p:hist[f]=p.pop(f)
  p['current_reaudit']={'audit_id':AUDIT,'status':'BLOCKED_PENDING_FULL_REAUDIT','full_clinical_certification':False,'same_reviewer_content_passes':2,'independent_blind_passes':0,'corrections':['Replace noncanonical blueprint hierarchy with exact USMLE 2026 path','Bind each distractor to its own inspected source rather than irrelevant SCD citations','Make distractor mechanisms specific and verifiable','Add direct low-oxygen HbS-strand evidence','Replace generic moderate difficulty with item-specific easy author estimate','Isolate obsolete PASS metadata as historical'],'remaining_gates':['Independent isolated author/auditor workflow required by README','Exhaustive semantic comparison beyond targeted candidate screening']}
  assert p['item']['intended_key']=='E' and set(p['item']['options'])==set('ABCDE')
  rh={'candidate_id':CID,'verdict':'BLOCKED_PENDING_FULL_REAUDIT','payload_sha256':digest(p),'prior_review_sha256':rev['review_sha256'],'reviewed_at':'2026-09-20','audit_record':'audit/'+AUDIT+'.md','review_scope':'Live claim review, evidence repair and same-reviewer adversarial reread; not independent certification','defects':p['current_reaudit']['remaining_gates']}
  arc={'item_row':old,'review_row':rev}
  if ap.exists():assert json.loads(ap.read_text())==arc
  else:ap.write_text(json.dumps(arc,indent=2)+'\n')
  db.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(rh),rh['verdict'],'2026-09-20',CID));db.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(rh),digest(rh),rh['verdict'],'2026-09-20',CID));assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
 result={'candidate_id':CID,'before_sha256':EXPECTED,'after_sha256':digest(p),'status':rh['verdict'],'new_final_passes':0,'item_count':1635};(ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
