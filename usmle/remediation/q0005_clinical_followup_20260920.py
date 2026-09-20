"""Apply reviewed Q0005 corrections without carrying forward a FINAL verdict."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CID='S1-DIRECT-0005-20260827T020000Z'
EXPECTED='70b44381cb254e368f8366c0720e18ed8df2382bed45999cf099489aab0a2d38'
AUDIT='Q0005_CLINICAL_FOLLOWUP_20260920'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()

def src(i,title,url,date,locator,summary,sha):
 return {'source_id':i,'title':title,'url':url,'agency':'National Library of Medicine (NIH) — MedlinePlus Genetics','government_status_verified':True,'publication_or_revision_date':date,'retrieved_at':'2026-09-20','section_locator':locator,'supporting_passage':summary,'passage_type':'Reviewer paraphrase, not a verbatim quotation','raw_source_sha256':sha,'raw_capture_record':'audit/'+AUDIT+'.md','set_id_applicability':'NOT_APPLICABLE_NON_DRUG_SOURCE','rights_status':'Official U.S. federal health-information source; facts used for original synthesis.'}

def main():
 db=sqlite3.connect(ROOT/'data/usmle-step1.db');db.row_factory=sqlite3.Row
 ap=ROOT/'remediation'/(AUDIT+'_BEFORE_ROWS.json')
 with db:
  db.execute('BEGIN IMMEDIATE')
  old=dict(db.execute('select * from step2_final_items where candidate_id=?',(CID,)).fetchone());rev=dict(db.execute('select * from step2_final_reviews where candidate_id=?',(CID,)).fetchone());p=json.loads(old['payload_json'])
  if p.get('current_reaudit',{}).get('audit_id')==AUDIT:
   assert digest(p)==old['payload_sha256'] and ap.exists();print('Already applied; no rows changed');return
  assert old['payload_sha256']==EXPECTED==digest(p)
  p['blueprint'].update(coverage_deficit_addressed='Glucose-6-phosphate dehydrogenase deficiency: oxidant-triggered hemolysis caused by inadequate red-cell NADPH defense.',disciplines=['Biochemistry','Pathology'],primary_system='Blood & Lymphoreticular System',official_outline_path=['Blood & Lymphoreticular System','Anemia, cytopenias, and polycythemia anemias','Hemolysis','Glucose 6-phosphate dehydrogenase deficiency'])
  p['item'].update(vignette='A 22-year-old man develops jaundice and dark urine 2 days after receiving an oxidant medication. Peripheral blood smear shows bite cells; supravital staining reveals Heinz bodies.',lead_in="Which cellular defect most directly explains this patient's hemolysis?",difficulty='easy',reasoning_steps_count=2,difficulty_basis='Author estimate, not psychometrically calibrated: the oxidant exposure, bite cells, and Heinz bodies directly identify G6PD deficiency; the examinee must distinguish its NADPH-defense defect from other genuine red-cell disorders. No calculation is required.',intended_key='B',options={'A':'Reduced pyruvate kinase activity and erythrocyte ATP depletion','B':'Reduced glucose-6-phosphate dehydrogenase activity and NADPH production','C':'Loss of erythrocyte membrane structural proteins','D':'Reduced beta-globin chain synthesis','E':'Polymerization of deoxygenated hemoglobin S'},tested_construct='G6PD deficiency reduces pentose-phosphate-pathway NADPH production, leaving erythrocytes unable to withstand an oxidant challenge and causing Heinz-body injury, bite cells, and hemolysis.')
  r={
   'A':'Incorrect. Pyruvate kinase deficiency lowers ATP production in erythrocytes and causes inherited chronic nonspherocytic hemolytic anemia. It does not specifically explain an acute oxidant-triggered episode with Heinz bodies and bite cells.',
   'B':'Correct. G6PD performs the first step of the pentose phosphate pathway and generates NADPH. Because erythrocytes depend on this source of reducing power, deficient G6PD activity permits reactive oxygen species to damage hemoglobin and trigger hemolysis after an oxidant exposure.',
   'C':'Incorrect. Red-cell membrane-protein defects cause hereditary spherocytosis, producing rigid spherical erythrocytes that are removed in the spleen rather than oxidant-induced Heinz bodies and bite cells.',
   'D':'Incorrect. Reduced beta-globin synthesis causes beta thalassemia, with deficient hemoglobin production and ineffective erythropoiesis. It does not produce this acute oxidant-triggered Heinz-body pattern.',
   'E':'Incorrect. Deoxygenated HbS polymerization causes sickling and vaso-occlusive or hemolytic manifestations in sickle cell disease, not oxidant-induced Heinz bodies with bite cells.'}
  p['explanation']={'key_explanation':r['B'],'distractor_explanations':r,'educational_objective':'Distinguish G6PD-dependent NADPH failure and oxidant hemolysis from ATP depletion, membrane instability, beta-globin underproduction, and HbS polymerization.'}
  ids={'A':['S3'],'B':['S1','S2'],'C':['S4'],'D':['S5'],'E':['S6']};dx={'A':'Pyruvate kinase deficiency','B':'Glucose-6-phosphate dehydrogenase deficiency','C':'Hereditary spherocytosis','D':'Beta thalassemia','E':'Sickle cell disease'}
  p['evidence_map']=[{'option':o,'claim':t,'rationale':r[o],'source_ids':ids[o],'evidence_basis':'LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION','audit_record':'audit/'+AUDIT+'.md','target_diagnosis_or_process':dx[o],'target_mechanism':t} for o,t in p['item']['options'].items()]
  p['sources']=[
   src('S1','Glucose-6-phosphate dehydrogenase deficiency','https://medlineplus.gov/genetics/condition/glucose-6-phosphate-dehydrogenase-deficiency/','Last updated April 12, 2023','Description; Causes','G6PD deficiency causes hemolysis after infections, selected drugs, or fava exposure because reactive oxygen species accumulate and damage erythrocytes.','0e9d6665f1a7172dd61d74c8b149bb71a3ea7928aa500caf203f8b2df5fa3167'),
   src('S2','G6PD gene','https://medlineplus.gov/genetics/gene/g6pd/','Last updated April 12, 2023','Normal Function; Glucose-6-phosphate dehydrogenase deficiency','The first pentose-phosphate-pathway reaction produces NADPH; erythrocytes depend on G6PD-derived NADPH for protection from reactive oxygen species.','b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655'),
   src('S3','Pyruvate kinase deficiency','https://medlineplus.gov/genetics/condition/pyruvate-kinase-deficiency/','Last updated April 1, 2012','Description; Causes','Reduced red-cell pyruvate kinase function causes ATP shortage and chronic hereditary nonspherocytic hemolytic anemia.','0b2756033de6150735f3d74d6fc00fafdb2242ba1ff4dd4e547a38dd29df8f4d'),
   src('S4','Hereditary spherocytosis','https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/','Last updated September 1, 2013','Description; Causes','Red-cell membrane-protein variants make erythrocytes rigid and spherical, leading to splenic destruction.','78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b'),
   src('S5','Beta thalassemia','https://medlineplus.gov/genetics/condition/beta-thalassemia/','Last updated May 1, 2023','Description; Causes','HBB variants abolish or reduce beta-globin production, impairing functional hemoglobin formation and normal erythrocyte development.','fec84384950309227187bb141987dbde036646c10cbf1e0462d44bd17ff78ec9'),
   src('S6','Sickle cell disease','https://medlineplus.gov/genetics/condition/sickle-cell-disease/','Last updated March 14, 2024','Description; Causes','Hemoglobin S forms rigid assemblies that distort erythrocytes and obstruct small vessels.','7ae0662873da2af18d2714ee9ea953b3b8a4b1008d58d11882d268bc345b833c')]
  p['semantic_fingerprint'].update(correct_answer_concept=p['item']['options']['B'],diagnosis_or_process='Glucose-6-phosphate dehydrogenase deficiency',essential_clues=['oxidant medication exposure','acute jaundice and dark urine','bite cells','Heinz bodies on supravital stain'],lead_in_task=p['item']['lead_in'],mechanism=p['item']['tested_construct'],tested_construct=p['item']['tested_construct'],reasoning_chain=['Recognize oxidant-triggered hemolysis with Heinz bodies and bite cells.','Identify deficient G6PD-derived NADPH defense as the direct cellular defect.'],distractor_misconceptions=['confusing ATP-depletion hemolysis with oxidant injury','confusing membrane instability with oxidative hemoglobin damage','confusing globin-chain underproduction with acute oxidant hemolysis','confusing HbS polymerization with Heinz-body injury'])
  hist=p.setdefault('historical_audit_metadata',{})
  for f in ('author_self_audit','step2_final_audit','hashes'):
   if f in p:hist[f]=p.pop(f)
  p['current_reaudit']={'audit_id':AUDIT,'status':'BLOCKED_PENDING_FULL_REAUDIT','full_clinical_certification':False,'same_reviewer_content_passes':2,'independent_blind_passes':0,'corrections':['Replace remote metabolite distractors with genuine red-cell disease mechanisms','Bind each alternative to its own inspected source','Clarify Heinz-body visualization by supravital staining','Use exact USMLE 2026 hemolysis hierarchy','Replace generic moderate difficulty with item-specific easy author estimate','Isolate obsolete PASS metadata as historical'],'remaining_gates':['Independent isolated author/auditor workflow required by README','Exhaustive semantic comparison beyond targeted candidate screening']}
  assert p['item']['intended_key']=='B' and set(p['item']['options'])==set('ABCDE')
  rh={'candidate_id':CID,'verdict':'BLOCKED_PENDING_FULL_REAUDIT','payload_sha256':digest(p),'prior_review_sha256':rev['review_sha256'],'reviewed_at':'2026-09-20','audit_record':'audit/'+AUDIT+'.md','review_scope':'Live claim review, evidence repair and same-reviewer adversarial reread; not independent certification','defects':p['current_reaudit']['remaining_gates']}
  arc={'item_row':old,'review_row':rev}
  if ap.exists():assert json.loads(ap.read_text())==arc
  else:ap.write_text(json.dumps(arc,indent=2)+'\n')
  db.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(rh),rh['verdict'],'2026-09-20',CID));db.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(rh),digest(rh),rh['verdict'],'2026-09-20',CID));assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
 result={'candidate_id':CID,'before_sha256':EXPECTED,'after_sha256':digest(p),'status':rh['verdict'],'new_final_passes':0,'item_count':1635};(ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
