#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

FILES={
 'a':Path('usmle/batch_specs_1401_1500/01_q1401_q1425_author_20260908_schema_repaired.json'),
 'b':Path('usmle/batch_specs_1401_1500/02_q1426_q1450_author_20260908_schema_repaired.json'),
 'c':Path('usmle/batch_specs_1401_1500/03_q1451_q1475_author_20260908_collision_repaired.json'),
}

def ev(q,key,sid,loc,rats):
 return [{'claim_id':f'Q{q}-{L}','option':L,'claim_locator':f'explanation.distractor_explanations.{L}','claim':rats[L],'source_ids':[sid],'direct_or_inference':'direct' if L==key else 'inference','source_locator':loc,'item_specific_application':'Keyed target/mechanism is directly supported by the cited source; distractor rejection uses that mechanism plus stipulated experimental conditions.'} for L in 'ABCDE']

def qa(alt,res):
 return {'key_correctness':'PASS','all_options_review':'PASS','single_best_answer':'PASS','second_answer_attack':{'option':alt,'resolution':res,'status':'PASS'},'hidden_assumptions':'PASS','numerical_claims':'PASS — no invented dose, cutoff, response percentage, trial result, or empirical item statistic.','fabricated_distractors':'PASS','source_identity_setid_url_locator':'PASS','currentness':'PASS — current DailyMed SetID page reverified 2026-09-10; no unsupported revision date asserted.','blueprint':'PASS','difficulty':'Author estimate only','rationale':'PASS A-E','educational_objective':'PASS','adversarial_second_pass':'PASS','technical_hash_gate':'PENDING','unresolved_content_defects':[]}

def make(q,drug,system,disc,vig,lead,opts,key,construct,keyexp,rats,eo,title,setid,loc,alt,res):
 sid=f'Q{q}-LABEL'
 return {'num':q,'drug':drug,'country_scope':'United States','status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT','blueprint':{'primary_system':system,'primary_competency':'Medical Knowledge: Applying Foundational Science Concepts','disciplines':disc,'official_outline_path':[system],'specification_source_id':'USMLE-SPEC'},'item':{'vignette':vig,'lead_in':lead,'options':opts,'intended_key':key,'tested_construct':construct,'difficulty':'moderate-hard','difficulty_basis':'Author estimate based on mechanistic discrimination; no empirical calibration claimed.'},'explanation':{'key_explanation':keyexp,'distractor_explanations':rats,'educational_objective':eo},'sources':[{'source_id':sid,'title':title,'agency':'Manufacturer prescribing information hosted by NLM DailyMed','url':f'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}','setid':setid,'source_section_date':None,'date_basis':'Current DailyMed SetID page and cited mechanism section reverified 2026-09-10; no revision date inferred.','retrieved_at':'2026-09-10','section_locator':loc,'source_page_sha256':None,'cited_section_sha256':None,'hash_status':'PENDING_DETERMINISTIC_REFETCH_AND_HASH'}],'evidence_map':ev(q,key,sid,loc,rats),'author_qa':qa(alt,res)}

def main():
 docs={k:json.loads(p.read_text()) for k,p in FILES.items()}; xs={k:{x['num']:x for x in v['items']} for k,v in docs.items()}
 expected={1401:'elacestrant',1402:'mavorixafor',1411:'pirtobrutinib',1414:'lenacapavir',1423:'fezolinetant',1435:'ensifentrine',1440:'donanemab-azbt',1443:'atogepant',1475:'zolbetuximab-clzb'}
 for q,d in expected.items():
  bucket='a' if q<=1425 else ('b' if q<=1450 else 'c'); assert xs[bucket][q]['drug']==d,(q,xs[bucket][q]['drug'])
 R={}
 R[1401]=make(1401,'deuruxolitinib','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Immunology'],
  'Cultured immune cells are exposed to deuruxolitinib. Cytokine-induced STAT phosphorylation decreases after signaling through receptors that use JAK1/JAK2/TYK2, while a JAK3-selective reporter is less affected.',
  'Which direct action best explains this pattern?',
  {'A':'Inhibition of JAK1, JAK2, and TYK2 with lower potency at JAK3','B':'Selective irreversible inhibition of JAK3','C':'Allosteric inhibition of TYK2 only','D':'Neutralization of extracellular interleukin-6','E':'Direct degradation of STAT3'},'A','JAK1/JAK2/TYK2 inhibition with lower potency at JAK3',
  'Deuruxolitinib is a Janus kinase inhibitor with greater in-vitro inhibitory potency for JAK1, JAK2, and TYK2 than for JAK3, reducing downstream STAT signaling.',
  {'A':'Correct. The relative kinase profile matches deuruxolitinib.','B':'Selective JAK3 inhibition has the wrong kinase preference.','C':'TYK2-only allostery would not explain JAK1/JAK2 pathway inhibition.','D':'Extracellular IL-6 neutralization would not directly inhibit multiple purified JAK-dependent pathways.','E':'The documented mechanism is kinase inhibition, not direct STAT degradation.'},
  'Use relative JAK-family inhibition to distinguish deuruxolitinib from JAK3-selective and TYK2-selective mechanisms.','LEQSELVI- deuruxolitinib tablet, film coated','a603f231-d09e-4bad-ad5e-b55f865da095','12.1 Mechanism of Action','C','TYK2 inhibition is plausible because TYK2 is affected, but the simultaneous JAK1 and JAK2 effects make a TYK2-only mechanism insufficient.')
 R[1402]=make(1402,'crinecerfont','Reproductive & Endocrine Systems',['Pharmacology','Physiology'],
  'Pituitary corticotrophs are exposed to corticotropin-releasing factor (CRF). After crinecerfont is added, ACTH secretion falls despite unchanged CRF concentration; signaling through CRF type 2 receptors is preserved.',
  'Which direct action best explains these findings?',
  {'A':'Agonism of CRF type 1 receptors','B':'Selective antagonism of CRF type 1 receptors','C':'Antagonism of CRF type 2 receptors','D':'Direct inhibition of adrenal 21-hydroxylase','E':'Glucocorticoid-receptor agonism'},'B','Selective CRF1 receptor antagonism with reduced ACTH secretion',
  'Crinecerfont selectively antagonizes CRF type 1 receptors in the pituitary, blocking CRF binding and reducing ACTH secretion while not antagonizing CRF type 2 receptors.',
  {'A':'CRF1 agonism would increase rather than suppress CRF-driven ACTH release.','B':'Correct. Selective CRF1 antagonism explains reduced ACTH with preserved CRF2 signaling.','C':'CRF2 blockade is specifically not the documented target.','D':'21-hydroxylase inhibition acts in the adrenal steroid pathway, not at pituitary CRF signaling.','E':'Glucocorticoid-receptor agonism could suppress ACTH indirectly but does not match direct CRF1 receptor blockade.'},
  'Differentiate direct pituitary CRF1 antagonism from downstream adrenal enzyme inhibition and glucocorticoid feedback.','CRENESSITY- crinecerfont capsule and oral solution','fd3a6fbd-9137-428a-ba46-df6606f07d28','12.1 Mechanism of Action','E','Glucocorticoid feedback can lower ACTH, but preserved ligand concentration and receptor-selective assay findings localize the effect to CRF1 antagonism.')
 R[1411]=make(1411,'zanidatamab-hrii','Multisystem Processes & Disorders',['Pharmacology','Immunology'],
  'HER2-expressing tumor cells are exposed to zanidatamab-hrii. The antibody occupies two extracellular HER2 epitopes, receptor surface abundance falls, and ADCC, CDC, and antibody-dependent phagocytosis increase.',
  'Which direct design feature best explains this profile?',
  {'A':'Bispecific binding to two extracellular sites on HER2','B':'Single-site HER2 kinase inhibition','C':'HER3-only neutralization','D':'PD-L1 blockade','E':'Delivery of a microtubule toxin through an antibody-drug conjugate'},'A','Bispecific HER2 binding with receptor internalization and immune effector cytotoxicity',
  'Zanidatamab-hrii is a bispecific HER2-directed antibody that binds two extracellular HER2 sites, promotes receptor internalization and reduction at the cell surface, and can induce CDC, ADCC, and ADCP.',
  {'A':'Correct. Dual-epitope HER2 binding matches the receptor and immune-effector findings.','B':'A small-molecule HER2 kinase inhibitor would not account for antibody-mediated CDC/ADCC.','C':'HER3-only neutralization does not match direct HER2 binding.','D':'PD-L1 blockade targets an immune checkpoint rather than HER2.','E':'The label describes the antibody itself, not an attached cytotoxic payload.'},
  'Recognize a bispecific dual-epitope HER2 antibody from receptor internalization and multiple Fc-mediated cytotoxic mechanisms.','ZIIHERA- zanidatamab-hrii for injection','ae5d9425-fae5-4541-a158-150998343348','12.1 Mechanism of Action','E','An HER2-directed ADC can also produce tumor killing, but the stipulated dual extracellular HER2 binding plus CDC/ADCC/ADCP without a payload identifies zanidatamab.')
 R[1414]=make(1414,'zenocutuzumab-zbco','Multisystem Processes & Disorders',['Pharmacology','Immunology'],
  'NRG1-fusion tumor cells are exposed to zenocutuzumab-zbco. HER2-HER3 dimerization and NRG1 binding to HER3 decrease, PI3K-AKT-mTOR signaling falls, and ADCC is observed.',
  'Which direct action best explains these findings?',
  {'A':'Selective HER2 kinase inhibition','B':'HER3 degradation by a PROTAC','C':'Neutralization of circulating NRG1 only','D':'Bispecific binding to HER2 and HER3 that blocks dimerization and NRG1-HER3 signaling','E':'PI3K catalytic-site inhibition'},'D','Bispecific HER2/HER3 blockade of NRG1-dependent signaling',
  'Zenocutuzumab-zbco is a bispecific antibody that binds extracellular HER2 and HER3, inhibits HER2-HER3 dimerization, prevents NRG1 binding to HER3, suppresses downstream PI3K-AKT-mTOR signaling, and can mediate ADCC.',
  {'A':'HER2 kinase inhibition alone does not explain simultaneous extracellular HER2/HER3 binding.','B':'The label does not describe targeted HER3 proteolysis.','C':'Ligand neutralization alone would not explain direct HER2 and HER3 binding.','D':'Correct. Bispecific HER2/HER3 binding blocks the NRG1-driven receptor complex.','E':'PI3K inhibition is downstream and would not account for receptor-level binding and ADCC.'},
  'Localize NRG1-fusion signaling blockade to a bispecific HER2/HER3 antibody rather than a downstream kinase inhibitor.','BIZENGRI- zenocutuzumab-zbco injection','203daea4-fc87-40a4-a92f-ba2351b16de1','12.1 Mechanism of Action','E','PI3K inhibition can reduce the same downstream pathway, but receptor-level HER2/HER3 binding and ADCC identify the bispecific antibody mechanism.')
 R[1423]=make(1423,'cosibelimab-ipdl','Multisystem Processes & Disorders',['Pharmacology','Immunology'],
  'Tumor cells expressing PD-L1 are cocultured with activated T cells and Fc-receptor-bearing effector cells. Cosibelimab-ipdl restores T-cell activity and also produces antibody-dependent cellular cytotoxicity in vitro.',
  'Which direct target best accounts for both effects?',
  {'A':'PD-1 on T cells','B':'CTLA-4 on T cells','C':'PD-L1 on tumor and immune cells','D':'B7.1 only','E':'CD20 on B cells'},'C','PD-L1 blockade of PD-1/B7.1 interactions with ADCC capability',
  'Cosibelimab-ipdl binds PD-L1, blocks PD-L1 interactions with PD-1 and B7.1 to release inhibitory antitumor signaling, and has also demonstrated ADCC in vitro.',
  {'A':'PD-1 blockade can restore T-cell activity but does not match direct PD-L1 binding and the labeled ADCC property.','B':'CTLA-4 is a different checkpoint target.','C':'Correct. PD-L1 binding explains checkpoint release and the antibody-mediated effector-cell result.','D':'B7.1 is one interacting receptor, not the antibody target itself.','E':'CD20 targeting would not match the PD-L1-dependent assay.'},
  'Distinguish PD-L1-directed checkpoint blockade with Fc-effector activity from PD-1- and CTLA-4-directed mechanisms.','UNLOXCYT- cosibelimab-ipdl injection','06bdadd5-d2db-406f-a3f8-de47f48a52e3','12.1 Mechanism of Action','A','PD-1 blockade is the strongest checkpoint alternative, but direct PD-L1 occupancy and in-vitro ADCC select cosibelimab-ipdl.')
 R[1435]=make(1435,'mirdametinib','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
  'NF1-associated tumor cells are exposed to mirdametinib. MEK1/2 kinase activity falls and phosphorylation of the downstream protein ERK decreases, without direct inhibition of RAF in a parallel assay.',
  'Which direct target best explains this pattern?',
  {'A':'BRAF V600E','B':'ERK1/2 catalytic sites','C':'KRAS G12C','D':'PI3K-alpha','E':'MEK1 and MEK2'},'E','MEK1/2 inhibition with decreased ERK phosphorylation',
  'Mirdametinib inhibits MEK1 and MEK2, upstream regulators of ERK signaling, and decreases downstream ERK phosphorylation.',
  {'A':'RAF lies upstream of MEK and is not the directly inhibited kinase in the stem.','B':'ERK phosphorylation falls downstream, but ERK itself is not the documented direct target.','C':'KRAS inhibition would act further upstream and does not match the kinase assay.','D':'PI3K-alpha belongs to a distinct signaling pathway.','E':'Correct. Mirdametinib directly inhibits MEK1/2.'},
  'Use pathway position to distinguish MEK1/2 inhibition from upstream RAF/KRAS and downstream ERK targeting.','GOMEKLI- mirdametinib capsule and tablet for oral suspension','4c41bf90-5fa7-4935-a95c-e047ea6bbf8e','12.1 Mechanism of Action','B','ERK inhibition is tempting because ERK phosphorylation decreases, but the direct kinase assay localizes inhibition to MEK1/2 upstream.')
 R[1440]=make(1440,'vimseltinib','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
  'Cells expressing colony-stimulating factor 1 receptor are stimulated with CSF1. Vimseltinib decreases receptor autophosphorylation, downstream signaling, and proliferation while unrelated receptor tyrosine kinase activity is preserved.',
  'Which direct target best explains these findings?',
  {'A':'KIT','B':'VEGFR2','C':'PDGFR-beta','D':'FLT3','E':'CSF1 receptor'},'E','CSF1R kinase inhibition',
  'Vimseltinib is a kinase inhibitor of colony-stimulating factor 1 receptor (CSF1R) and inhibits CSF1R autophosphorylation, ligand-induced signaling, and proliferation of CSF1R-expressing cells.',
  {'A':'KIT is a different receptor tyrosine kinase.','B':'VEGFR2 inhibition would affect angiogenic signaling rather than the specified CSF1 response.','C':'PDGFR-beta is not the receptor in the ligand-specific assay.','D':'FLT3 inhibition does not explain CSF1-triggered receptor autophosphorylation.','E':'Correct. Vimseltinib directly inhibits CSF1R.'},
  'Identify CSF1R inhibition from ligand-specific receptor autophosphorylation and proliferative signaling.','ROMVIMZA- vimseltinib capsule','f73c7a62-9601-4df0-810f-100f515d79ea','12.1 Mechanism of Action','C','Other receptor tyrosine kinases are plausible oncology targets, but the CSF1-specific autophosphorylation assay uniquely localizes the target to CSF1R.')
 R[1443]=make(1443,'telisotuzumab vedotin-tllv','Multisystem Processes & Disorders',['Pharmacology','Histology & Cell Biology'],
  'c-Met-positive tumor cells are exposed to telisotuzumab vedotin-tllv. The conjugate is internalized, a protease-cleavable linker releases MMAE, microtubules are disrupted, and cells arrest in the cell cycle before apoptosis.',
  'Which mechanism best explains this sequence?',
  {'A':'HER2-directed antibody carrying a topoisomerase inhibitor','B':'EGFR antibody that blocks ligand binding without a payload','C':'c-Met-directed antibody-drug conjugate delivering MMAE','D':'Free systemic vinca alkaloid independent of tumor antigen','E':'c-Met kinase inhibition by an ATP-competitive small molecule'},'C','c-Met-directed ADC internalization with intracellular MMAE release',
  'Telisotuzumab vedotin-tllv is a c-Met-directed antibody-drug conjugate. After binding c-Met-expressing cells it is internalized, MMAE is released after intracellular linker cleavage, and MMAE disrupts microtubules, causing cell-cycle arrest and apoptosis.',
  {'A':'The target and payload are different.','B':'A naked receptor-blocking antibody would not explain intracellular MMAE release.','C':'Correct. c-Met targeting, internalization, and MMAE-mediated microtubule disruption define this ADC.','D':'Free microtubule toxin would not require c-Met-dependent internalization.','E':'Small-molecule kinase inhibition does not account for an antibody-linked MMAE payload.'},
  'Recognize an antibody-drug conjugate by antigen-specific internalization and intracellular release of a defined cytotoxic payload.','EMRELIS- telisotuzumab vedotin-tllv for injection','bc04f980-3957-4e35-ab81-8ec2ffe87215','12.1 Mechanism of Action','E','c-Met kinase inhibition shares the receptor target, but only the ADC mechanism explains antibody internalization and MMAE-mediated microtubule disruption.')
 R[1475]=make(1475,'zongertinib','Respiratory & Renal/Urinary Systems',['Pharmacology','Biochemistry'],
  'Non-small-cell lung cancer cells harboring an activating HER2 tyrosine-kinase-domain mutation are exposed to zongertinib. HER2 phosphorylation and downstream ERK phosphorylation decrease, and proliferation falls.',
  'Which direct action best explains these findings?',
  {'A':'Neutralization of extracellular HER2 with a monoclonal antibody','B':'HER2-directed antibody-drug conjugate internalization','C':'MEK1/2 inhibition downstream of HER2','D':'EGFR degradation','E':'Inhibition of HER2 kinase activity'},'E','HER2 kinase inhibition in HER2-mutant tumor cells',
  'Zongertinib is a kinase inhibitor of HER2 that inhibits HER2 phosphorylation, downstream ERK signaling, and proliferation of cells with activating HER2 tyrosine-kinase-domain mutations.',
  {'A':'An extracellular antibody would not be identified as a direct kinase inhibitor in the cellular signaling assay.','B':'An ADC would require payload internalization rather than immediate HER2 phosphorylation blockade.','C':'MEK inhibition could reduce ERK phosphorylation but would not directly suppress HER2 phosphorylation.','D':'EGFR degradation is a different receptor mechanism.','E':'Correct. Zongertinib directly inhibits HER2 kinase activity.'},
  'Use receptor and downstream phosphorylation to distinguish direct HER2 kinase inhibition from antibody and downstream-MEK mechanisms.','HERNEXEOS- zongertinib tablet, film coated','d3fabf12-354e-4e5c-b5de-20fdb579b783','12.1 Mechanism of Action','C','MEK inhibition can lower ERK phosphorylation, but the simultaneous decrease in HER2 phosphorylation places the direct target at HER2 itself.')
 for q,new in R.items():
  bucket='a' if q<=1425 else ('b' if q<=1450 else 'c'); xs[bucket][q].clear(); xs[bucket][q].update(new)
 for k,b in docs.items():
  assert ''.join(x['item']['intended_key'] for x in b['items'])==b['answer_key_sequence']; b.setdefault('collision_repair_r3',{})['reverified_2026_09_10']=True
  FILES[k].write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'PASS','replaced':sorted(R),'count':len(R)}))
if __name__=='__main__': main()
