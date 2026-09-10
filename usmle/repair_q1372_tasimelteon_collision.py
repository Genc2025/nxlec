#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
P=Path('usmle/batch_specs_1301_1400/04_q1356_q1380_author_20260908.json')

def main():
    b=json.loads(P.read_text())
    xs={x['num']:x for x in b['items']}
    x=xs[1372]
    assert x['drug']=='daridorexant'
    assert x['item']['intended_key']=='B'
    x.clear()
    x.update({
      'num':1372,'drug':'tasimelteon','country_scope':'United States','status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
      'blueprint':{'primary_system':'Behavioral Health & Nervous Systems/Special Senses','primary_competency':'Medical Knowledge: Applying Foundational Science Concepts','disciplines':['Pharmacology','Physiology'],'official_outline_path':['Behavioral Health & Nervous Systems/Special Senses'],'specification_source_id':'USMLE-SPEC'},
      'item':{
        'vignette':'A cultured suprachiasmatic-nucleus preparation is exposed to tasimelteon. Receptor assays show activation of two G-protein-coupled melatonin receptor subtypes involved in circadian timing. The preparation shows no enhancement of GABA-A receptor currents and no antagonism of orexin receptors.',
        'lead_in':'Which direct receptor action best explains these findings?',
        'options':{'A':'Antagonism of orexin OX1 and OX2 receptors','B':'Agonism of melatonin MT1 and MT2 receptors','C':'Positive allosteric modulation of GABA-A receptors','D':'Antagonism of histamine H1 receptors','E':'Agonism of serotonin 5-HT1A receptors'},
        'intended_key':'B','tested_construct':'Melatonin MT1/MT2 receptor agonism in circadian signaling','difficulty':'moderate','difficulty_basis':'Author estimate; requires distinguishing circadian melatonin-receptor agonism from orexin and GABAergic hypnotic mechanisms.'},
      'explanation':{
        'key_explanation':'Tasimelteon is an agonist at melatonin MT1 and MT2 receptors, which participate in control of circadian rhythms. Labeling also describes greater affinity for MT2 than MT1, but activation of both receptor subtypes is the relevant direct action.',
        'distractor_explanations':{
          'A':'Dual orexin-receptor antagonism is a different hypnotic mechanism and is explicitly excluded by the assay.',
          'B':'Correct. Tasimelteon directly agonizes melatonin MT1 and MT2 receptors involved in circadian signaling.',
          'C':'GABA-A positive allosteric modulation is not tasimelteon’s documented receptor mechanism and is excluded by the current assay.',
          'D':'Histamine H1 antagonism does not account for the observed activation of melatonin receptors.',
          'E':'5-HT1A agonism is serotonergic pharmacology and does not match tasimelteon’s documented MT1/MT2 receptor action.'},
        'educational_objective':'Differentiate melatonin-receptor agonism that modulates circadian signaling from orexin antagonism and GABAergic sedation.'},
      'sources':[{'source_id':'Q1372-LABEL','title':'HETLIOZ- tasimelteon capsule; HETLIOZ LQ- tasimelteon suspension','agency':'Manufacturer prescribing information hosted by NLM DailyMed','url':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ca4a9b63-708e-49e9-8f9b-010625443b90','setid':'ca4a9b63-708e-49e9-8f9b-010625443b90','source_section_date':None,'date_basis':'Current DailyMed SetID page and sections 12.1/12.2 reverified 2026-09-10; no revision date inferred.','retrieved_at':'2026-09-10','section_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics','source_page_sha256':None,'cited_section_sha256':None,'hash_status':'PENDING_DETERMINISTIC_REFETCH_AND_HASH'}],
      'evidence_map':[
        {'claim_id':'Q1372-A','option':'A','claim_locator':'explanation.distractor_explanations.A','source_ids':['Q1372-LABEL'],'direct_or_inference':'inference','source_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics'},
        {'claim_id':'Q1372-B','option':'B','claim_locator':'explanation.distractor_explanations.B','source_ids':['Q1372-LABEL'],'direct_or_inference':'direct','source_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics'},
        {'claim_id':'Q1372-C','option':'C','claim_locator':'explanation.distractor_explanations.C','source_ids':['Q1372-LABEL'],'direct_or_inference':'inference','source_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics'},
        {'claim_id':'Q1372-D','option':'D','claim_locator':'explanation.distractor_explanations.D','source_ids':['Q1372-LABEL'],'direct_or_inference':'inference','source_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics'},
        {'claim_id':'Q1372-E','option':'E','claim_locator':'explanation.distractor_explanations.E','source_ids':['Q1372-LABEL'],'direct_or_inference':'inference','source_locator':'12.1 Mechanism of Action; 12.2 Pharmacodynamics'}],
      'author_qa':{'status':'AUTHOR_QA_PASS','independent_audit':False,'key_correctness':'PASS','all_options_review':'PASS','single_best_answer':'PASS','second_answer_attack':{'option':'A','resolution':'Both are sleep-related receptor mechanisms, but the experiment directly shows MT1/MT2 activation and explicitly excludes orexin antagonism.','status':'PASS'},'hidden_assumptions':'PASS','numerical_claims':'PASS — no invented dose, threshold, response percentage, or trial result.','fabricated_distractors':'PASS','source_identity_setid_url_locator':'PASS','currentness':'PASS — current SetID page reverified 2026-09-10; uncertain revision date not asserted.','blueprint':'PASS','difficulty':'Author estimate only','rationale':'PASS A-E','educational_objective':'PASS','adversarial_second_pass':'PASS','technical_hash_gate':'PENDING','unresolved_content_defects':[]}
    })
    assert ''.join(z['item']['intended_key'] for z in b['items'])==b['answer_key_sequence']
    P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print('Q1372_COLLISION_REPLACEMENT=PASS')
if __name__=='__main__': main()
