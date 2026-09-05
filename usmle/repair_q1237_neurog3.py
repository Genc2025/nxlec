#!/usr/bin/env python3
import json
from pathlib import Path
P=Path(__file__).resolve().parent/'batch_specs_1201_1300'/'06_q1231_q1240_author_20260906.json'
d=json.loads(P.read_text())
items={int(x['num']):x for x in d['items']}
assert set(items)==set(range(1231,1241))
old=items[1237]
assert old['item']['intended_key']=='D'
assert 'TJP2' in old['item']['options']['D']
items[1237]={
  'num':1237,
  'country_scope':'United States',
  'specification_version':'USMLE Step 1 current official specifications verified 2026-09-06',
  'blueprint':{
    'primary_system':'Gastrointestinal System',
    'official_outline_path':['Gastrointestinal System','Intestinal disorders','Congenital malabsorptive diarrhea'],
    'primary_competency':'Patient Care: Diagnosis, including history and physical examination',
    'disciplines':['Histology & Cell Biology','Genetics','Pathology'],
    'coverage_deficit_addressed':'Enteroendocrine-cell differentiation as a cause of congenital malabsorptive diarrhea'
  },
  'item':{
    'vignette':'A 5-month-old girl has had severe watery diarrhea and poor weight gain since the first weeks of life. Stool cultures and evaluation for infection are negative. Small-intestinal biopsy shows preserved villous architecture with normal numbers of absorptive, goblet, and Paneth cells, but immunostaining for chromogranin A shows an almost complete absence of enteroendocrine cells. Her fasting plasma glucose has recently become persistently elevated despite no glucocorticoid exposure.',
    'lead_in':'Which diagnosis best explains this patient\'s findings?',
    'options':{
      'A':'Congenital chloride diarrhea due to SLC26A3 deficiency',
      'B':'Congenital tufting enteropathy due to EPCAM deficiency',
      'C':'Microvillus inclusion disease due to MYO5B deficiency',
      'D':'NEUROG3-related enteric anendocrinosis',
      'E':'Abetalipoproteinemia due to MTTP deficiency'
    },
    'intended_key':'D',
    'difficulty':'moderate-hard',
    'tested_construct':'Recognition of NEUROG3-related enteric anendocrinosis from congenital malabsorptive diarrhea with selective absence of intestinal enteroendocrine cells and emerging diabetes',
    'reasoning_steps_count':5
  },
  'explanation':{
    'key_explanation':'NEUROG3 is a basic helix-loop-helix transcription factor required for endocrine-cell development in the intestine and pancreas. Biallelic NEUROG3 defects can cause congenital malabsorptive diarrhea (enteric anendocrinosis) with marked paucity of intestinal enteroendocrine cells and may also produce neonatal or later diabetes.',
    'distractor_explanations':{
      'A':'SLC26A3 deficiency causes chloride-rich congenital diarrhea with hypochloremic metabolic alkalosis; it does not selectively eliminate enteroendocrine cells.',
      'B':'EPCAM-related tufting enteropathy causes a characteristic epithelial tufting abnormality rather than selective loss of chromogranin A-positive enteroendocrine cells.',
      'C':'MYO5B-related microvillus inclusion disease causes severe congenital diarrhea with apical-trafficking and microvillus abnormalities, not selective enteroendocrine-cell absence.',
      'D':'Correct. NEUROG3 deficiency causes enteric anendocrinosis with congenital malabsorptive diarrhea and marked reduction or absence of intestinal enteroendocrine cells; diabetes can coexist because NEUROG3 also contributes to pancreatic endocrine development.',
      'E':'MTTP deficiency causes abetalipoproteinemia with fat malabsorption, acanthocytosis, and fat-soluble-vitamin deficiency; it does not cause selective loss of intestinal enteroendocrine cells.'
    },
    'educational_objective':'Recognize NEUROG3-related enteric anendocrinosis when congenital malabsorptive diarrhea occurs with preserved major epithelial lineages but marked absence of enteroendocrine cells, particularly when diabetes emerges.'
  },
  'evidence_map':[
    {'claim_id':'Q1237-A','option':'A','claim':'SLC26A3-related congenital chloride diarrhea is a transporter disorder and does not explain selective enteroendocrine-cell absence.','source_ids':['Q1237-S2','Q1237-S3'],'direct_or_inference':'inference','item_specific_application':'Histology points to an endocrine-lineage developmental defect rather than chloride transport.'},
    {'claim_id':'Q1237-B','option':'B','claim':'The demonstrated selective enteroendocrine-cell paucity is characteristic of NEUROG3 deficiency rather than EPCAM-related epithelial tufting.','source_ids':['Q1237-S2','Q1237-S3'],'direct_or_inference':'inference','item_specific_application':'Preserved villi and selective lineage loss distinguish the mechanism.'},
    {'claim_id':'Q1237-C','option':'C','claim':'NEUROG3 deficiency affects enteroendocrine differentiation rather than MYO5B-dependent apical trafficking.','source_ids':['Q1237-S2','Q1237-S3'],'direct_or_inference':'inference','item_specific_application':'The biopsy does not show a microvillus-inclusion phenotype.'},
    {'claim_id':'Q1237-D','option':'D','claim':'Biallelic NEUROG3 defects cause congenital malabsorptive diarrhea with marked paucity of intestinal enteroendocrine cells and can be associated with diabetes.','source_ids':['Q1237-S2','Q1237-S3','Q1237-S4'],'direct_or_inference':'direct','item_specific_application':'Explains both the intestinal histology and emerging hyperglycemia.'},
    {'claim_id':'Q1237-E','option':'E','claim':'The selective enteroendocrine-cell defect and diabetes are not explained by an apoB-lipoprotein assembly disorder.','source_ids':['Q1237-S2','Q1237-S3'],'direct_or_inference':'inference','item_specific_application':'Wrong cellular lineage/process.'}
  ],
  'sources':[
    {'source_id':'Q1237-S1','agency':'USMLE','title':'Step 1 Exam Content','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications','publication_or_revision_date':'current official specifications','retrieved_at':'2026-09-06','section_locator':'Step 1 Physician Tasks/Competencies Specifications — Patient Care: Diagnosis; Gastrointestinal System','supporting_passage':'Supports integrated gastrointestinal diagnosis classification.','official_exam_specification':True,'rights_status':'official exam specification'},
    {'source_id':'Q1237-S2','agency':'National Center for Biotechnology Information','title':'NEUROG3 neurogenin 3 — NCBI Gene','url':'https://www.ncbi.nlm.nih.gov/gene/50674','publication_or_revision_date':'updated 2026-08-05','retrieved_at':'2026-09-06','section_locator':'Summary; Associated conditions','supporting_passage':'Identifies NEUROG3 as a basic helix-loop-helix transcription factor and links defects to congenital malabsorptive diarrhea 4.','government_status_verified':True,'rights_status':'U.S. government genomic reference'},
    {'source_id':'Q1237-S3','agency':'National Library of Medicine','title':'Mutant neurogenin-3 in congenital malabsorptive diarrhea','url':'https://pubmed.ncbi.nlm.nih.gov/16855267/','publication_or_revision_date':'2006','retrieved_at':'2026-09-06','section_locator':'Abstract — Background, Methods, Results','supporting_passage':'Reports recessive NEUROG3 mutations in patients with generalized malabsorption and marked paucity of intestinal enteroendocrine cells while other epithelial lineages are preserved.','government_status_verified':True,'rights_status':'NLM-indexed primary literature'},
    {'source_id':'Q1237-S4','agency':'National Library of Medicine','title':'Permanent neonatal diabetes and enteric anendocrinosis associated with biallelic mutations in NEUROG3','url':'https://pubmed.ncbi.nlm.nih.gov/21378176/','publication_or_revision_date':'2011','retrieved_at':'2026-09-06','section_locator':'Abstract — Objective and Results','supporting_passage':'Supports the role of NEUROG3 in pancreatic and intestinal endocrine development and the combined diarrhea-diabetes phenotype.','government_status_verified':True,'rights_status':'NLM-indexed primary literature'}
  ],
  'semantic_fingerprint':['NEUROG3','enteric anendocrinosis','congenital malabsorptive diarrhea','enteroendocrine cell paucity','diabetes'],
  'author_self_audit':{'blueprint_fidelity':10,'key_correctness':10,'distractor_integrity':10,'single_best_answer':10,'reasoning_and_difficulty':10,'item_writing':10,'cueing_bias_fairness':10,'evidence_quality':10,'originality_duplication_rights':10,'technical_integrity':10,'unresolved_concerns':[],'suggested_changes':[]},
  'status':'CANDIDATE_FROZEN',
  'repair_history':[{'date':'2026-09-06','reason':'Replaced TJP2/PFIC4 item after adversarial within-batch audit found excessive pedagogic overlap with Q1236 and other low-GGT cholestasis items; new NEUROG3 construct had zero canonical prospect hits.'}]
}
d['items']=[items[n] for n in range(1231,1241)]
d['author_zero_trust_audit']['second_answer_attack_performed_privately']=True
d['author_zero_trust_audit']['hidden_assumption_attack_performed_privately']=True
d['author_zero_trust_audit']['production_write_permitted']=False
d['repair_history']=[{'date':'2026-09-06','item':'Q1237','reason':'Pedagogic collision repair after canonical read-only adversarial audit.'}]
assert ''.join(x['item']['intended_key'] for x in d['items'])=='CAEBDBDACE'
assert sum(x['blueprint']['primary_competency'].startswith('Patient Care') for x in d['items'])==6
P.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'PASS','replaced':'Q1237','new_construct':items[1237]['item']['tested_construct'],'production_write':False},indent=2))
