#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'batch_specs_1401_1500' / '03_q1451_q1475_author_20260908.json'
MK = 'Medical Knowledge: Applying Foundational Science Concepts'
RETRIEVED = '2026-09-08'


def src(q, sid, title, url, setid, locator, section_date=None, date_basis=None):
    return {
        'source_id': f'Q{q}-{sid}',
        'title': title,
        'agency': 'Manufacturer prescribing information hosted by NLM DailyMed',
        'url': url,
        'setid': setid,
        'source_section_date': section_date,
        'date_basis': date_basis or 'Current DailyMed label and cited section checked 2026-09-08; section date recorded only when explicitly represented by the current source.',
        'retrieved_at': RETRIEVED,
        'section_locator': locator,
        'verification': 'Current label identity, SetID, cited locator, and mechanism claim checked before author-QA.',
        'rights_note': 'Original educational item; prescribing-information facts paraphrased.'
    }


def mk(q, drug, system, disciplines, vignette, lead, options, key, construct, difficulty, keyexp, rationales, objective, sources, strongest_alt, resolution):
    assert set(options) == set('ABCDE') and set(rationales) == set('ABCDE') and key in options
    assert rationales[key] == keyexp
    source_ids = [s['source_id'] for s in sources]
    primary_locator = sources[0]['section_locator']
    evidence = []
    for L in 'ABCDE':
        evidence.append({
            'claim_id': f'Q{q}-{L}',
            'option': L,
            'claim_locator': f'explanation.distractor_explanations.{L}',
            'claim': rationales[L],
            'source_ids': source_ids,
            'direct_or_inference': 'direct' if L == key else 'inference',
            'source_locator': primary_locator,
            'scope': 'Direct labeled mechanism/target claim for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions.'
        })
    return {
        'num': q,
        'drug': drug,
        'country_scope': 'United States',
        'status': 'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT',
        'blueprint': {
            'primary_system': system,
            'primary_competency': MK,
            'disciplines': disciplines,
            'official_outline_path': [system],
            'specification_source_id': 'USMLE-SPEC'
        },
        'item': {
            'vignette': vignette,
            'lead_in': lead,
            'options': options,
            'intended_key': key,
            'tested_construct': construct,
            'difficulty': difficulty,
            'difficulty_basis': 'Author estimate based on mechanistic application and distractor discrimination; no empirical item statistics are claimed.'
        },
        'explanation': {
            'key_explanation': keyexp,
            'distractor_explanations': rationales,
            'educational_objective': objective
        },
        'sources': sources,
        'evidence_map': evidence,
        'author_qa': {
            'status': 'AUTHOR_QA_PASS',
            'independent_audit': False,
            'key_correctness': 'PASS',
            'all_options_review': 'PASS',
            'single_best_answer': 'PASS',
            'second_answer_attack': {'option': strongest_alt, 'resolution': resolution, 'status': 'PASS'},
            'hidden_assumptions': 'PASS — experimental findings are stipulated teaching conditions; no treatment superiority, universal response, cure, or unsupported clinical efficacy claim is inferred.',
            'numerical_claims': 'PASS — no invented dose, cutoff, response percentage, trial result, or empirical item statistic is used.',
            'fabricated_distractors': 'PASS — distractors are established biological/pharmacologic mechanisms and are not presented as invented clinical facts.',
            'source_identity_setid_url_locator': 'PASS',
            'currentness': 'PASS — current source instance checked 2026-09-08; SPL effective/update dates are not mislabeled as PI Revised dates.',
            'blueprint': 'PASS against current Step 1 system/competency/discipline vocabulary.',
            'difficulty': 'Author estimate only; not psychometrically calibrated.',
            'rationale': 'PASS — keyed explanation plus A-E rationales present.',
            'educational_objective': 'PASS',
            'adversarial_second_pass': 'PASS',
            'unresolved_content_defects': []
        }
    }


def build():
    I = []
    I.append(mk(1451,'elamipretide','Cardiovascular System',['Pharmacology','Biochemistry'],
        'Cardiomyocytes from a patient with Barth syndrome are exposed to elamipretide. The drug rapidly concentrates at the inner mitochondrial membrane, where mitochondrial ultrastructure and respiratory function improve without a change in mitochondrial DNA sequence.',
        'Which direct interaction best explains this localization and effect?',
        {'A':'Binding to cardiolipin in the inner mitochondrial membrane','B':'Inhibition of cardiolipin synthase','C':'Blockade of the complex I ubiquinone-binding site','D':'Opening of the mitochondrial permeability transition pore','E':'Inhibition of mitochondrial ribosomal translation'},'A',
        'Mitochondrial cardiolipin binding at the inner mitochondrial membrane','moderate',
        'Elamipretide binds mitochondrial cardiolipin and localizes to the inner mitochondrial membrane, where it improves mitochondrial morphology and function.',
        {'A':'Elamipretide binds mitochondrial cardiolipin and localizes to the inner mitochondrial membrane, where it improves mitochondrial morphology and function.','B':'Inhibiting cardiolipin synthesis would reduce the target phospholipid rather than explain direct drug localization to it.','C':'The label identifies cardiolipin binding rather than direct complex I blockade.','D':'Opening the permeability transition pore would not explain the documented cardiolipin-binding mechanism and would generally destabilize mitochondria.','E':'Mitochondrial translation inhibition does not account for rapid inner-membrane cardiolipin localization.'},
        'Recognize cardiolipin as a pharmacologic binding target within the inner mitochondrial membrane.',
        [src(1451,'LABEL','FORZINITY- elamipretide hydrochloride injection','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=146bf34c-76f2-48db-ac07-fb29cce2cd75','146bf34c-76f2-48db-ac07-fb29cce2cd75','12.1 Mechanism of Action','2025-09-23')],
        'C','Respiratory-chain inhibition can alter mitochondrial function, but the current label directly identifies cardiolipin binding and inner-membrane localization.'))

    I.append(mk(1452,'nerandomilast','Respiratory & Renal/Urinary Systems',['Pharmacology','Biochemistry'],
        'Lung fibroblasts and inflammatory cells are exposed to nerandomilast. Intracellular cyclic AMP rises despite unchanged adenylyl cyclase activity. In vitro enzyme assays show substantially greater inhibition of one PDE4 isoenzyme than of PDE4A, PDE4C, or PDE4D.',
        'Which action most directly produces the increase in intracellular cyclic AMP?',
        {'A':'Inhibition of phosphodiesterase 5','B':'Preferential inhibition of phosphodiesterase 4B','C':'Inhibition of adenylyl cyclase','D':'Inhibition of protein kinase A','E':'Activation of soluble guanylate cyclase'},'B',
        'Preferential PDE4B inhibition and reduced cAMP hydrolysis','moderate',
        'Nerandomilast inhibits PDE4 with preferential inhibition of PDE4B; reducing PDE4-mediated cAMP hydrolysis increases intracellular cAMP.',
        {'A':'PDE5 primarily hydrolyzes cGMP rather than explaining the observed cAMP increase.','B':'Nerandomilast inhibits PDE4 with preferential inhibition of PDE4B; reducing PDE4-mediated cAMP hydrolysis increases intracellular cAMP.','C':'Adenylyl cyclase inhibition would decrease, not increase, cAMP generation.','D':'Protein kinase A is downstream of cAMP and does not directly hydrolyze the nucleotide.','E':'Soluble guanylate cyclase generates cGMP rather than cAMP.'},
        'Connect PDE4B inhibition with reduced cAMP degradation and increased intracellular cAMP.',
        [src(1452,'LABEL','JASCAYD- nerandomilast tablet','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=fa1b14c6-957f-d326-5099-911bfe33e391','fa1b14c6-957f-d326-5099-911bfe33e391','12.1 Mechanism of Action',None,'Current DailyMed prescribing-information PDF/SetID and 12.1 mechanism text checked 2026-09-08; no unsupported PI revision date is inferred.')],
        'A','Another phosphodiesterase inhibitor could raise a cyclic nucleotide, but the substrate and labeled PDE4B preference identify PDE4B rather than PDE5.'))

    I.append(mk(1453,'brensocatib','Respiratory & Renal/Urinary Systems',['Pharmacology','Immunology'],
        'Neutrophil precursors are matured ex vivo in the presence of brensocatib. The resulting neutrophils have reduced activities of neutrophil elastase, cathepsin G, and proteinase 3 even though transcription of these serine-protease genes is unchanged.',
        'Inhibition of which enzyme during neutrophil maturation best explains the finding?',
        {'A':'Dipeptidyl peptidase 4','B':'Myeloperoxidase','C':'Dipeptidyl peptidase 1','D':'Peptidylarginine deiminase 4','E':'NADPH oxidase'},'C',
        'DPP1 inhibition prevents activation of neutrophil serine proteases','moderate-hard',
        'Brensocatib competitively and reversibly inhibits DPP1, the enzyme that activates neutrophil serine proteases during neutrophil maturation in bone marrow.',
        {'A':'DPP4 is a distinct peptidase and is not the labeled target that activates the neutrophil serine-protease zymogens.','B':'Myeloperoxidase contributes to oxidative antimicrobial activity but does not activate the three serine proteases specified.','C':'Brensocatib competitively and reversibly inhibits DPP1, the enzyme that activates neutrophil serine proteases during neutrophil maturation in bone marrow.','D':'PAD4 catalyzes protein citrullination and participates in NET biology but is not the documented brensocatib target.','E':'NADPH oxidase generates reactive oxygen species and does not account for coordinate loss of these protease activities.'},
        'Recognize DPP1 as the maturation protease required for activation of multiple neutrophil serine proteases.',
        [src(1453,'LABEL','BRINSUPRI- brensocatib tablet','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b56986ae-e7db-421e-b622-a7f41e321f3d','b56986ae-e7db-421e-b622-a7f41e321f3d','12.1 Mechanism of Action','2026-03-16')],
        'B','Myeloperoxidase is a neutrophil granule enzyme, but the coordinated reduction of elastase, cathepsin G, and proteinase 3 activity reflects blocked DPP1-dependent zymogen activation.'))

    I.append(mk(1454,'mavorixafor','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology','Genetics'],
        'Leukocytes from a patient with WHIM syndrome have a gain-of-function CXCR4 variant and show excessive retention in a CXCL12-rich bone-marrow model. Mavorixafor increases movement of these cells out of the marrow compartment without altering the CXCL12 concentration.',
        'Which direct action best explains the leukocyte mobilization?',
        {'A':'CXCR4 agonism','B':'Granulocyte colony-stimulating factor receptor blockade','C':'Neutralization of CXCL12','D':'Antagonism of CXCR4','E':'Antagonism of CXCR2'},'D',
        'CXCR4 antagonism reverses CXCL12-mediated marrow retention in WHIM syndrome','moderate',
        'Mavorixafor antagonizes CXCR4 and blocks CXCL12/SDF-1 binding, reducing the excessive marrow-retention signal and mobilizing leukocytes into the peripheral circulation.',
        {'A':'CXCR4 agonism would reinforce the gain-of-function retention signal.','B':'Blocking the G-CSF receptor would not explain interruption of the explicitly CXCL12-CXCR4 retention axis.','C':'The experiment holds CXCL12 concentration unchanged; the labeled drug directly targets CXCR4 rather than neutralizing the ligand.','D':'Mavorixafor antagonizes CXCR4 and blocks CXCL12/SDF-1 binding, reducing the excessive marrow-retention signal and mobilizing leukocytes into the peripheral circulation.','E':'CXCR2 is a different chemokine receptor and does not mediate the WHIM-associated CXCL12 retention phenotype.'},
        'Use a fixed-ligand chemokine model to distinguish receptor antagonism from ligand depletion.',
        [src(1454,'LABEL','XOLREMDI- mavorixafor capsule, gelatin coated','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7f3a5ee3-ca73-4876-85a0-ed1e108a2237','7f3a5ee3-ca73-4876-85a0-ed1e108a2237','12.1 Mechanism of Action','2024-09-10')],
        'C','CXCL12 neutralization could also weaken retention, but ligand concentration is fixed and the current label identifies CXCR4 as the direct drug target.'))

    I.append(mk(1455,'axatilimab-csfr','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'Monocytes and monocyte-derived macrophages from a patient with chronic graft-versus-host disease are exposed to axatilimab-csfr. A receptor-binding assay shows occupancy of a surface receptor shared by these cells, followed by reduced nonclassical monocyte abundance and reduced pathogenic macrophage activity.',
        'Which receptor is directly bound by the antibody?',
        {'A':'Interleukin-6 receptor','B':'CCR2','C':'Tumor necrosis factor receptor 1','D':'Interleukin-34 receptor distinct from CSF-1R','E':'Colony-stimulating factor-1 receptor'},'E',
        'CSF-1R blockade on monocytes and macrophages','moderate',
        'Axatilimab-csfr binds CSF-1R on monocytes and macrophages, reducing proinflammatory and profibrotic monocyte/macrophage populations and activity.',
        {'A':'IL-6 receptor blockade is a different cytokine pathway and is not the documented axatilimab target.','B':'CCR2 participates in monocyte trafficking but is not the surface receptor bound by axatilimab-csfr.','C':'TNFR1 signaling can regulate inflammation but is not the labeled direct target.','D':'IL-34 is a ligand of CSF-1R; it does not signal through a separate receptor that is the axatilimab target.','E':'Axatilimab-csfr binds CSF-1R on monocytes and macrophages, reducing proinflammatory and profibrotic monocyte/macrophage populations and activity.'},
        'Identify CSF-1R as a therapeutic target on monocyte/macrophage populations in chronic GVHD.',
        [src(1455,'LABEL','NIKTIMVO- axatilimab-csfr injection','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=bb6dba23-e7a6-4765-a1e6-b9e277ce0381','bb6dba23-e7a6-4765-a1e6-b9e277ce0381','12.1 Mechanism of Action','2026-06-24')],
        'B','CCR2 is a plausible monocyte surface target, but the current label directly identifies CSF-1R binding and links it to reductions in monocyte/macrophage populations.'))

    I.append(mk(1456,'efanesoctocog alfa','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry'],
        'A recombinant factor VIII product for hemophilia A remains stable without binding endogenous von Willebrand factor. The engineered molecule contains factor VIII fused to Fc, XTEN polypeptides, and the D-prime-D3 region of von Willebrand factor.',
        'Which engineered feature most directly prevents factor VIII from interacting with endogenous von Willebrand factor and thereby helps overcome the von-Willebrand-factor-imposed half-life ceiling?',
        {'A':'The appended von Willebrand factor D-prime-D3 domain','B':'Removal of the factor VIII catalytic domain','C':'A polyethylene glycol chain covalently attached to the active site','D':'Replacement of factor VIII with factor IX Padua','E':'A thrombin-cleavable albumin-binding domain'},'A',
        'VWF D-prime-D3 engineering overcomes endogenous VWF half-life limitation','hard',
        'In efanesoctocog alfa, the appended VWF D-prime-D3 domain protects and stabilizes factor VIII and prevents interaction with endogenous VWF, helping overcome the half-life limitation imposed by VWF clearance.',
        {'A':'In efanesoctocog alfa, the appended VWF D-prime-D3 domain protects and stabilizes factor VIII and prevents interaction with endogenous VWF, helping overcome the half-life limitation imposed by VWF clearance.','B':'Loss of factor VIII catalytic function would defeat the replacement-therapy purpose.','C':'The labeled molecule uses Fc, VWF D-prime-D3, and XTEN engineering rather than active-site PEGylation as the feature described.','D':'Factor IX Padua is used in a hemophilia B gene-therapy strategy, not in this factor VIII fusion protein.','E':'The current label does not identify an albumin-binding domain as the feature preventing endogenous VWF interaction.'},
        'Relate protein-domain engineering to the pharmacokinetic half-life limit imposed by endogenous VWF on factor VIII.',
        [src(1456,'LABEL','ALTUVIIIO- antihemophilic factor (recombinant), Fc-VWF-XTEN fusion protein-ehtl','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=01411972-df40-4ccf-88f0-d3220e5abda9','01411972-df40-4ccf-88f0-d3220e5abda9','12.1 Mechanism of Action; Mechanism of Half-life Extension','2025-12-31')],
        'E','Other half-life-extension strategies are possible, but the stem specifically asks which feature prevents endogenous VWF interaction; the label assigns that role to the appended D-prime-D3 domain.'))

    I.append(mk(1457,'garadacimab-gxii','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Physiology'],
        'Plasma from a patient with hereditary angioedema is exposed to garadacimab-gxii. The conversion of prekallikrein to kallikrein and subsequent bradykinin generation decrease, although C1 inhibitor concentration is unchanged.',
        'Which direct molecular action produces this effect?',
        {'A':'Neutralization of bradykinin B2 receptors','B':'Binding the catalytic domain of activated factor XII and inhibiting factor XIIa activity','C':'Replacement of functional C1 inhibitor','D':'Direct irreversible inhibition of plasma kallikrein','E':'Activation of high-molecular-weight kininogen degradation'},'B',
        'Activated factor XII blockade upstream of kallikrein and bradykinin','moderate-hard',
        'Garadacimab-gxii binds the catalytic domain of activated factor XII and inhibits FXIIa activity, reducing prekallikrein activation, kallikrein generation, and bradykinin production.',
        {'A':'Bradykinin-receptor blockade acts downstream and would not explain reduced kallikrein generation itself.','B':'Garadacimab-gxii binds the catalytic domain of activated factor XII and inhibits FXIIa activity, reducing prekallikrein activation, kallikrein generation, and bradykinin production.','C':'The C1-inhibitor concentration is unchanged and the drug is not replacement C1 inhibitor.','D':'Direct plasma-kallikrein inhibition is a distinct HAE strategy; garadacimab acts one step upstream at activated factor XII.','E':'Increasing kininogen degradation would promote, not suppress, bradykinin generation.'},
        'Trace the contact-activation pathway from factor XIIa to kallikrein and bradykinin.',
        [src(1457,'LABEL','ANDEMBRY- garadacimab injection, solution','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=07b0b671-db81-49f0-a402-0c0219db7fa2','07b0b671-db81-49f0-a402-0c0219db7fa2','12.1 Mechanism of Action','2025-06-19')],
        'D','Direct kallikrein inhibition could also lower bradykinin, but the current label localizes garadacimab one step upstream to FXIIa.'))

    I.append(mk(1458,'etrasimod','Gastrointestinal System',['Pharmacology','Immunology'],
        'Lymphocytes are exposed to etrasimod before placement in a model containing lymphoid tissue and peripheral blood compartments. Fewer lymphocytes exit the lymphoid compartment, and receptor profiling shows high-affinity activity at S1P receptor subtypes 1, 4, and 5.',
        'Which process is most directly altered by this receptor modulation?',
        {'A':'Neutrophil oxidative burst','B':'B-cell immunoglobulin class switching','C':'Lymphocyte egress from lymphoid organs','D':'Complement C3 cleavage','E':'Integrin alpha4beta7 binding to MAdCAM-1'},'C',
        'S1P1/4/5 modulation reduces lymphocyte egress','moderate',
        'Etrasimod modulates S1P1, S1P4, and S1P5 and partially, reversibly blocks lymphocyte egress from lymphoid organs, reducing peripheral lymphocyte counts.',
        {'A':'The S1P-receptor mechanism described does not directly target the neutrophil respiratory burst.','B':'Class-switch recombination is not the trafficking step measured in the experiment.','C':'Etrasimod modulates S1P1, S1P4, and S1P5 and partially, reversibly blocks lymphocyte egress from lymphoid organs, reducing peripheral lymphocyte counts.','D':'Complement cleavage is unrelated to the measured S1P-dependent lymphocyte trafficking effect.','E':'Alpha4beta7-MAdCAM-1 blockade is the mechanism of vedolizumab, not etrasimod.'},
        'Connect S1P receptor modulation with lymphocyte sequestration in lymphoid tissues.',
        [src(1458,'LABEL','VELSIPITY- etrasimod tablet, film coated','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=65171e4a-d136-4abc-b08c-c40c1b486ff6','65171e4a-d136-4abc-b08c-c40c1b486ff6','12.1 Mechanism of Action','2025-08-12')],
        'E','Both mechanisms can reduce gut lymphocyte trafficking, but the receptor profile and lymphoid-egress experiment identify S1P modulation rather than alpha4beta7 blockade.'))

    I.append(mk(1459,'paltusotine','Reproductive & Endocrine Systems',['Pharmacology','Physiology'],
        'Pituitary somatotrophs are exposed to paltusotine. Growth hormone release and downstream IGF-1 production decrease. Receptor assays show more than 4000-fold selectivity for one somatostatin receptor subtype and little or no affinity for the other subtypes.',
        'Which receptor action best explains the endocrine effect?',
        {'A':'Growth hormone receptor antagonism','B':'Dopamine D2 receptor antagonism','C':'GHRH receptor antagonism','D':'Selective somatostatin receptor 2 agonism','E':'Somatostatin receptor 5 antagonism'},'D',
        'Selective SSTR2 agonism suppresses GH and IGF-1','moderate',
        'Paltusotine is a highly selective SSTR2 agonist that, like somatostatin, suppresses GH and IGF-1 secretion.',
        {'A':'GH-receptor antagonism acts in peripheral target tissues and does not directly suppress somatotroph GH release in this assay.','B':'D2 antagonism is not the labeled paltusotine mechanism and would not match the somatostatin-receptor selectivity result.','C':'GHRH-receptor blockade can reduce GH secretion, but the drug is directly characterized by selective SSTR2 agonism.','D':'Paltusotine is a highly selective SSTR2 agonist that, like somatostatin, suppresses GH and IGF-1 secretion.','E':'The drug shows little or no affinity for other somatostatin receptor subtypes and acts as an SSTR2 agonist, not SSTR5 antagonist.'},
        'Identify a selective somatostatin receptor agonist from receptor-subtype and hormone-secretion data.',
        [src(1459,'LABEL','PALSONIFY- paltusotine tablet, film coated','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8a6d2ce0-a621-4ee7-983c-977cd948ff4d','8a6d2ce0-a621-4ee7-983c-977cd948ff4d','12.1 Mechanism of Action','2025-09-16')],
        'C','GHRH antagonism could also suppress GH, but the high-selectivity receptor assay directly identifies SSTR2 agonism.'))

    I.append(mk(1460,'olipudase alfa-rpcp','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
        'Cells from a patient with acid sphingomyelinase deficiency accumulate sphingomyelin in lysosomes. After olipudase alfa-rpcp exposure, the stored substrate falls despite persistence of the pathogenic SMPD1 variants.',
        'Which lysosomal reaction is restored by the therapy?',
        {'A':'Glucosylceramide hydrolysis to glucose and ceramide','B':'Ceramide glycosylation to glucosylceramide','C':'Cholesteryl ester hydrolysis to cholesterol and fatty acid','D':'Sphingomyelin synthesis from ceramide and phosphatidylcholine','E':'Sphingomyelin hydrolysis to ceramide and phosphocholine'},'E',
        'Acid sphingomyelinase enzyme replacement','moderate',
        'Olipudase alfa provides an exogenous source of acid sphingomyelinase, restoring lysosomal hydrolysis of sphingomyelin to ceramide and phosphocholine.',
        {'A':'Glucosylceramide hydrolysis is catalyzed by beta-glucocerebrosidase, not acid sphingomyelinase.','B':'This is a synthetic direction and would not remove accumulated sphingomyelin.','C':'Cholesteryl-ester hydrolysis is a lysosomal acid lipase function.','D':'Increasing sphingomyelin synthesis would worsen substrate accumulation.','E':'Olipudase alfa provides an exogenous source of acid sphingomyelinase, restoring lysosomal hydrolysis of sphingomyelin to ceramide and phosphocholine.'},
        'Identify the substrate and products of acid sphingomyelinase in a lysosomal enzyme-replacement context.',
        [src(1460,'LABEL','XENPOZYME- olipudase alfa-rpcp injection, powder, lyophilized, for solution','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=01a910ee-a33e-4be3-ac41-322d64c34311','01a910ee-a33e-4be3-ac41-322d64c34311','12.1 Mechanism of Action','2024-12-24')],
        'A','Both are lysosomal sphingolipid reactions, but the disease and replacement enzyme specifically identify acid sphingomyelinase rather than glucocerebrosidase.'))

    I.append(mk(1461,'cipaglucosidase alfa-atga/miglustat','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Biochemistry'],
        'A patient with late-onset Pompe disease receives cipaglucosidase alfa-atga together with miglustat. In a plasma stability assay, miglustat reduces loss of cipaglucosidase activity before the enzyme reaches muscle cells. After cellular uptake, miglustat dissociates and the recombinant enzyme enters lysosomes through mannose-6-phosphate receptors.',
        'What is the principal role of miglustat in this combination?',
        {'A':'Binding and stabilizing cipaglucosidase alfa-atga in the circulation','B':'Directly hydrolyzing lysosomal glycogen','C':'Inhibiting glycogen synthase in skeletal muscle','D':'Blocking mannose-6-phosphate receptors to prolong plasma exposure','E':'Replacing the GAA gene in myocytes'},'A',
        'Miglustat stabilizes cipaglucosidase alfa-atga before lysosomal delivery','moderate-hard',
        'In this combination, miglustat binds and stabilizes cipaglucosidase alfa-atga in blood, reducing enzyme inactivation; the recombinant GAA then dissociates from miglustat after uptake and cleaves lysosomal glycogen.',
        {'A':'In this combination, miglustat binds and stabilizes cipaglucosidase alfa-atga in blood, reducing enzyme inactivation; the recombinant GAA then dissociates from miglustat after uptake and cleaves lysosomal glycogen.','B':'Miglustat itself has no pharmacologic activity in cleaving glycogen in this combination.','C':'The labeled role is stabilization of the replacement enzyme, not inhibition of glycogen synthesis.','D':'Mannose-6-phosphate receptor binding is required for cellular uptake of cipaglucosidase and is not blocked by miglustat.','E':'Neither component edits or replaces the endogenous GAA gene.'},
        'Distinguish an enzyme stabilizer/chaperone role from the catalytic function of the replacement enzyme itself.',
        [src(1461,'POMBILITI','POMBILITI ATGA- cipaglucosidase alfa-atga injection','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d77aa596-910d-516b-e053-2995a90a0839','d77aa596-910d-516b-e053-2995a90a0839','12.1 Mechanism of Action','2023-08-14'),src(1461,'OPFOLDA','OPFOLDA- miglustat capsule','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d7c38298-37db-5a80-e053-2995a90aee40','d7c38298-37db-5a80-e053-2995a90aee40','12.1 Mechanism of Action','2023-08-14')],
        'B','Miglustat is associated with other glycosphingolipid pharmacology in different contexts, but the current POMBILITI/OPFOLDA labels explicitly assign it an enzyme-stabilizing role here and state that it does not cleave glycogen.'))

    I.append(mk(1462,'eladocagene exuparvovec-tneq','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Genetics','Biochemistry'],
        'A child with biallelic DDC variants undergoes bilateral intraputaminal administration of eladocagene exuparvovec-tneq. Follow-up imaging shows increased F-DOPA uptake in the putamen, and a dopamine metabolite increases in cerebrospinal fluid.',
        'Which molecular event most directly initiates this change?',
        {'A':'CRISPR correction of both endogenous DDC alleles','B':'AAV2-mediated delivery of a functional DDC gene causing AADC expression in the putamen','C':'Inhibition of monoamine oxidase B in striatal neurons','D':'Blockade of the dopamine transporter','E':'Direct replacement of dopamine by the viral vector'},'B',
        'AAV2-mediated DDC gene delivery restores AADC expression and dopamine production','moderate',
        'KEBILIDI is an rAAV2 gene therapy that delivers a functional DDC gene to the putamen, producing AADC enzyme expression and subsequent dopamine production.',
        {'A':'The therapy delivers an additional DDC gene; it does not edit both endogenous alleles.','B':'KEBILIDI is an rAAV2 gene therapy that delivers a functional DDC gene to the putamen, producing AADC enzyme expression and subsequent dopamine production.','C':'MAO-B inhibition reduces dopamine breakdown but does not explain new AADC expression or increased F-DOPA processing.','D':'Dopamine-transporter blockade changes reuptake rather than restoring the missing decarboxylase.','E':'The vector encodes DDC; it does not contain dopamine as replacement neurotransmitter.'},
        'Connect regional gene delivery to restoration of a missing neurotransmitter-synthesis enzyme.',
        [src(1462,'LABEL','KEBILIDI- eladocagene exuparvovec-tneq suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=9d6a6401-c6b5-4f29-af11-67707d249482','9d6a6401-c6b5-4f29-af11-67707d249482','12.1 Mechanism of Action',None,'Current DailyMed full prescribing information checked 2026-09-08; current PI displays Revised 11/2024 and the cited 12.1 mechanism was reverified.')],
        'C','Both mechanisms can increase dopaminergic signaling, but only AAV2 DDC delivery explains restored AADC expression and increased F-DOPA processing.'))

    I.append(mk(1463,'prademagene zamikeracel','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Genetics','Histology & Cell Biology'],
        'Keratinocytes from a patient with recessive dystrophic epidermolysis bullosa are harvested, gene-modified ex vivo, expanded into cellular sheets, and applied to wounds. The treated tissue subsequently expresses type VII collagen and forms anchoring fibrils at the dermal-epidermal junction.',
        'Which intervention was performed on the patient’s cells?',
        {'A':'Knockout of the mutant COL7A1 alleles without gene replacement','B':'Transient delivery of purified type VII collagen protein only','C':'Retroviral-vector transduction to express a functional COL7A1 gene','D':'CRISPR disruption of a keratinocyte integrin gene','E':'Silencing of COL7A1 messenger RNA'},'C',
        'Ex vivo COL7A1 gene addition in autologous keratinocyte sheets','moderate',
        'ZEVASKYN consists of autologous cells gene-modified by retroviral-vector transduction to express COL7A1, producing type VII collagen that contributes to anchoring-fibril formation.',
        {'A':'Removing mutant alleles without supplying a functional COL7A1 copy would not explain restored type VII collagen expression.','B':'The product consists of gene-modified living cells rather than transient purified-protein replacement alone.','C':'ZEVASKYN consists of autologous cells gene-modified by retroviral-vector transduction to express COL7A1, producing type VII collagen that contributes to anchoring-fibril formation.','D':'The therapeutic modification targets COL7A1 expression, not integrin disruption.','E':'Silencing COL7A1 would reduce the protein that the therapy is intended to restore.'},
        'Differentiate ex vivo autologous gene-modified cell therapy from protein replacement and gene silencing.',
        [src(1463,'LABEL','ZEVASKYN- prademagene zamikeracel cellular sheet','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f8782480-8782-4748-9764-b9ed60979d47','f8782480-8782-4748-9764-b9ed60979d47','12.1 Mechanism of Action','2026-03-19')],
        'B','Protein replacement might transiently supply collagen VII, but the ex vivo gene modification and persistent cellular sheets identify COL7A1 gene addition.'))

    I.append(mk(1464,'etranacogene dezaparvovec-drlb','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Genetics','Biochemistry'],
        'A man with hemophilia B receives a single intravenous AAV5-based gene therapy. Hepatocytes subsequently produce a high-specific-activity variant of coagulation factor IX and circulating factor IX activity rises.',
        'Which transgene product is encoded by this therapy?',
        {'A':'Wild-type factor VIII','B':'Activated factor X','C':'Tissue factor pathway inhibitor','D':'The Padua R338L variant of human factor IX','E':'Protein C'},'D',
        'AAV5 liver-directed factor IX Padua gene delivery','moderate',
        'HEMGENIX delivers a gene encoding the gain-of-function Padua R338L variant of human factor IX, leading to hepatocyte transduction and increased circulating factor IX activity.',
        {'A':'Factor VIII replacement addresses hemophilia A rather than factor IX deficiency.','B':'The vector does not encode activated factor X.','C':'TFPI inhibits coagulation and is not the replacement transgene.','D':'HEMGENIX delivers a gene encoding the gain-of-function Padua R338L variant of human factor IX, leading to hepatocyte transduction and increased circulating factor IX activity.','E':'Protein C is an anticoagulant zymogen and is not the transgene used in HEMGENIX.'},
        'Recognize the Factor IX Padua transgene used in liver-directed gene therapy for hemophilia B.',
        [src(1464,'LABEL','HEMGENIX- etranacogene dezaparvovec-drlb suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=35b2db65-4c6c-4173-ab56-b2bca69193bd','35b2db65-4c6c-4173-ab56-b2bca69193bd','11 Description; 12.1 Mechanism of Action','2026-04-30')],
        'A','AAV factor-replacement gene therapy could conceptually encode another clotting factor, but hemophilia B and the current HEMGENIX label specifically identify hFIX-Padua.'))

    I.append(mk(1465,'sepiapterin','Multisystem Processes & Disorders',['Pharmacology','Biochemistry','Genetics'],
        'Hepatocytes from a patient with sepiapterin-responsive phenylketonuria are exposed to sepiapterin. Tetrahydrobiopterin increases and phenylalanine hydroxylase activity rises without an increase in PAH protein abundance.',
        'Which biochemical role of sepiapterin best explains the response?',
        {'A':'Direct replacement of phenylalanine hydroxylase protein','B':'Inhibition of dihydropteridine reductase','C':'Irreversible inhibition of phenylalanine transport into hepatocytes','D':'Conversion to tyrosine that bypasses phenylalanine hydroxylase','E':'Precursor supply for tetrahydrobiopterin, a cofactor that activates phenylalanine hydroxylase'},'E',
        'Sepiapterin supplies BH4 precursor to activate residual PAH','moderate',
        'Sepiapterin is a precursor of tetrahydrobiopterin (BH4); the resulting BH4 activates phenylalanine hydroxylase and can increase residual PAH activity without increasing PAH protein abundance.',
        {'A':'The therapy does not replace PAH protein; enzyme abundance is stipulated to be unchanged.','B':'Inhibiting BH4 recycling would not explain the increase in active cofactor.','C':'The labeled mechanism is cofactor precursor replacement rather than blockade of phenylalanine entry.','D':'Sepiapterin is converted to BH4, not tyrosine, and does not bypass PAH by becoming the product.','E':'Sepiapterin is a precursor of tetrahydrobiopterin (BH4); the resulting BH4 activates phenylalanine hydroxylase and can increase residual PAH activity without increasing PAH protein abundance.'},
        'Explain how cofactor precursor replacement can increase residual enzyme activity without changing enzyme quantity.',
        [src(1465,'LABEL','SEPHIENCE- sepiapterin powder','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=32ac719c-49f0-4105-9c46-18c19583a5c2','32ac719c-49f0-4105-9c46-18c19583a5c2','12.1 Mechanism of Action','2025-07-28','Current DailyMed SetID version 6/effective 2026-04-24 checked 2026-09-08; the cited 12.1 mechanism section is dated 2025-07-28.')],
        'A','Both approaches could increase phenylalanine conversion, but unchanged PAH protein and rising BH4 identify cofactor precursor therapy rather than enzyme replacement.'))

    I.append(mk(1466,'afamitresgene autoleucel','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Immunology','Genetics'],
        'Autologous T cells from a patient with synovial sarcoma are transduced ex vivo to express an affinity-enhanced receptor. The engineered cells kill tumor cells only when a MAGE-A4-derived peptide is presented by HLA-A*02.',
        'Which receptor was introduced into the T cells?',
        {'A':'A T-cell receptor specific for the HLA-A*02-restricted MAGE-A4 peptide','B':'An HLA-independent anti-CD19 chimeric antigen receptor','C':'A soluble antibody against circulating MAGE-A4','D':'A T-cell receptor specific for extracellular HER2 without peptide presentation','E':'A complement receptor that recognizes C3b-coated tumor cells'},'A',
        'Engineered MAGE-A4-specific HLA-restricted TCR therapy','moderate-hard',
        'TECELRA contains autologous T cells engineered to express an affinity-enhanced TCR that recognizes an HLA-A*02-restricted MAGE-A4 peptide, triggering T-cell activation and tumor-cell killing.',
        {'A':'TECELRA contains autologous T cells engineered to express an affinity-enhanced TCR that recognizes an HLA-A*02-restricted MAGE-A4 peptide, triggering T-cell activation and tumor-cell killing.','B':'A CAR recognizes a surface antigen without peptide-HLA presentation; the stem explicitly requires HLA-A*02 and a peptide antigen.','C':'The therapeutic product is engineered T cells rather than a soluble antibody.','D':'Conventional TCRs recognize peptide-HLA complexes rather than intact extracellular HER2.','E':'Complement-receptor recognition does not explain the defined MAGE-A4 peptide/HLA restriction.'},
        'Distinguish an engineered TCR therapy for an intracellular antigen from HLA-independent CAR therapy.',
        [src(1466,'LABEL','TECELRA- afamitresgene autoleucel suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ab24631f-3364-46e1-8074-7244863bcbab','ab24631f-3364-46e1-8074-7244863bcbab','12.1 Mechanism of Action',None,'Current DailyMed full prescribing information/SetID checked 2026-09-08; the cited 12.1 mechanism was reverified and no unsupported section revision date is asserted.')],
        'B','Both are genetically modified autologous T-cell therapies, but the requirement for a specific peptide-HLA complex identifies an engineered TCR rather than a CAR.'))

    I.append(mk(1467,'obecabtagene autoleucel','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology','Histology & Cell Biology'],
        'Autologous T cells from a patient with B-cell acute lymphoblastic leukemia are engineered to express a synthetic receptor. These cells become activated after binding CD19 on target cells even when the target cells lack the patient’s HLA molecules.',
        'Which signaling structure most directly enables this HLA-independent recognition?',
        {'A':'An affinity-enhanced alpha-beta T-cell receptor requiring peptide-HLA presentation','B':'An anti-CD19 chimeric antigen receptor coupled to intracellular CD3-zeta signaling','C':'A soluble bispecific antibody bridging CD19 and CD3','D':'An Fc-gamma receptor introduced into the T cell','E':'A B-cell receptor specific for CD19'},'B',
        'CD19 CAR-mediated HLA-independent T-cell activation','moderate',
        'AUCATZYL consists of autologous T cells expressing an anti-CD19 CAR; engagement with CD19 activates the engineered T cells through downstream signaling that includes the CD3-zeta domain.',
        {'A':'A conventional or engineered TCR remains peptide-HLA dependent, contrary to the stem.','B':'AUCATZYL consists of autologous T cells expressing an anti-CD19 CAR; engagement with CD19 activates the engineered T cells through downstream signaling that includes the CD3-zeta domain.','C':'The product is a cellular therapy with the receptor encoded in the T cells, not an administered soluble bispecific antibody.','D':'Fc-gamma receptors recognize antibody Fc regions rather than directly binding CD19 in this product.','E':'A B-cell receptor is not the synthetic T-cell receptor used in AUCATZYL.'},
        'Differentiate CAR-mediated surface-antigen recognition from HLA-restricted TCR recognition.',
        [src(1467,'LABEL','AUCATZYL- obecabtagene autoleucel suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4fef6986-b988-45e4-8c20-b14f0ef1f538','4fef6986-b988-45e4-8c20-b14f0ef1f538','12.1 Mechanism of Action',None,'Current DailyMed full prescribing information/SetID checked 2026-09-08; cited 12.1 mechanism reverified.')],
        'A','Both engineered TCR and CAR therapies can activate T cells, but HLA-independent direct CD19 recognition specifically identifies a CAR.'))

    I.append(mk(1468,'zenocutuzumab-zbco','Respiratory & Renal/Urinary Systems',['Pharmacology','Biochemistry'],
        'NRG1-fusion-positive tumor cells are exposed to zenocutuzumab-zbco. HER2-HER3 dimerization falls, NRG1 can no longer activate HER3 efficiently, and downstream PI3K-AKT-mTOR signaling decreases.',
        'Which direct binding pattern best explains these findings?',
        {'A':'Binding EGFR and MET','B':'Binding two nonoverlapping epitopes on HER2 only','C':'Binding the extracellular domains of HER2 and HER3','D':'Binding NRG1 and HER2 without contacting HER3','E':'Binding PI3K and AKT intracellularly'},'C',
        'HER2/HER3 bispecific blockade of NRG1-driven signaling','moderate',
        'Zenocutuzumab-zbco is a bispecific antibody that binds extracellular HER2 and HER3, inhibits HER2-HER3 dimerization, and prevents NRG1 binding to HER3.',
        {'A':'EGFR-MET targeting does not match the NRG1-HER3 and HER2-HER3 findings.','B':'Binding two HER2 epitopes describes a different biparatopic strategy and would not directly explain blockade of NRG1 binding to HER3.','C':'Zenocutuzumab-zbco is a bispecific antibody that binds extracellular HER2 and HER3, inhibits HER2-HER3 dimerization, and prevents NRG1 binding to HER3.','D':'The current label identifies HER3 itself as one of the antibody targets rather than direct NRG1 neutralization.','E':'The antibody acts extracellularly; reduced PI3K-AKT-mTOR signaling is downstream of receptor blockade.'},
        'Use ligand-receptor and dimerization data to identify a HER2/HER3 bispecific antibody mechanism.',
        [src(1468,'LABEL','BIZENGRI- zenocutuzumab injection','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=203daea4-fc87-40a4-a92f-ba2351b16de1','203daea4-fc87-40a4-a92f-ba2351b16de1','12.1 Mechanism of Action','2026-05-19')],
        'B','A biparatopic HER2 antibody is mechanistically plausible in HER2 biology, but the stem specifically shows blocked NRG1-HER3 engagement, requiring direct HER3 binding as well.'))

    I.append(mk(1469,'mirdametinib','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Biochemistry'],
        'NF1-deficient tumor cells have constitutive RAS-pathway signaling. After mirdametinib exposure, phosphorylation of ERK falls even though RAS remains active and ERK protein abundance is unchanged.',
        'Which kinase pair is directly inhibited?',
        {'A':'RAF1 and BRAF','B':'ERK1 and ERK2','C':'PI3K and AKT','D':'MEK1 and MEK2','E':'JAK1 and JAK2'},'D',
        'MEK1/2 inhibition reduces downstream ERK phosphorylation','moderate',
        'Mirdametinib inhibits MEK1 and MEK2 kinase activity, thereby reducing downstream ERK phosphorylation.',
        {'A':'RAF kinases are upstream of MEK; the current label identifies MEK1/2 as the direct inhibited kinases.','B':'ERK phosphorylation decreases downstream, but ERK itself is not the direct labeled kinase target.','C':'PI3K-AKT is a parallel signaling pathway and does not explain the specific MEK-ERK result.','D':'Mirdametinib inhibits MEK1 and MEK2 kinase activity, thereby reducing downstream ERK phosphorylation.','E':'JAK-STAT signaling is not the pathway localized by the RAS-MEK-ERK experiment.'},
        'Localize an inhibitor within the RAS-RAF-MEK-ERK cascade using upstream and downstream signaling measurements.',
        [src(1469,'LABEL','GOMEKLI- mirdametinib capsule/tablet for oral suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4c41bf90-5fa7-4935-a95c-e047ea6bbf8e','4c41bf90-5fa7-4935-a95c-e047ea6bbf8e','12.1 Mechanism of Action','2025-02-27')],
        'B','Direct ERK inhibition could also reduce pathway output, but unchanged ERK abundance plus the labeled target and loss of ERK phosphorylation localize the drug to MEK1/2.'))

    I.append(mk(1470,'foscarbidopa/foslevodopa','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Biochemistry'],
        'A continuous subcutaneous infusion contains foscarbidopa and foslevodopa. In subcutaneous tissue and plasma, intrinsic alkaline phosphatase converts the phosphorylated prodrugs into two familiar Parkinson disease medications.',
        'Which pair of active drugs is produced after this bioconversion?',
        {'A':'Entacapone and levodopa','B':'Carbidopa and dopamine','C':'Benserazide and levodopa','D':'Carbidopa and 3-O-methyldopa','E':'Carbidopa and levodopa'},'E',
        'Alkaline-phosphatase conversion of foscarbidopa/foslevodopa prodrugs','moderate',
        'Foscarbidopa and foslevodopa are phosphate prodrugs converted in vivo by intrinsic alkaline phosphatase to carbidopa and levodopa, respectively.',
        {'A':'Entacapone is a COMT inhibitor and is not generated from foscarbidopa.','B':'Levodopa, not dopamine, is the direct product of foslevodopa dephosphorylation; dopamine is formed later in the CNS.','C':'Benserazide is a different peripheral decarboxylase inhibitor and is not the foscarbidopa product.','D':'3-O-methyldopa is a metabolite of levodopa, not the direct phosphatase product.','E':'Foscarbidopa and foslevodopa are phosphate prodrugs converted in vivo by intrinsic alkaline phosphatase to carbidopa and levodopa, respectively.'},
        'Recognize prodrug bioconversion as distinct from the subsequent pharmacologic actions of the active carbidopa/levodopa pair.',
        [src(1470,'LABEL','VYALEV- foscarbidopa/foslevodopa injection','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=28e806e4-951c-40a9-9f0c-d0929caf054c','28e806e4-951c-40a9-9f0c-d0929caf054c','11 Description; 12.1 Mechanism of Action; 12.3 Pharmacokinetics','2026-03-19')],
        'B','Dopamine is the clinically relevant downstream neurotransmitter, but the question asks the immediate phosphatase products, which are carbidopa and levodopa.'))

    I.append(mk(1471,'evinacumab-dgnb','Cardiovascular System',['Pharmacology','Physiology'],
        'Hepatocytes and lipoprotein particles from a patient with homozygous familial hypercholesterolemia are studied after evinacumab-dgnb treatment. LDL cholesterol falls despite absent functional LDL receptors, while lipoprotein-lipase and endothelial-lipase activities increase.',
        'Which direct target best explains these findings?',
        {'A':'ANGPTL3','B':'PCSK9','C':'HMG-CoA reductase','D':'NPC1L1','E':'Apolipoprotein B100'},'A',
        'ANGPTL3 blockade lowers lipids independently of LDLR and relieves lipase inhibition','moderate-hard',
        'Evinacumab-dgnb binds and inhibits ANGPTL3, relieving inhibition of lipoprotein lipase and endothelial lipase and lowering LDL-C through mechanisms that do not require a functional LDL receptor.',
        {'A':'Evinacumab-dgnb binds and inhibits ANGPTL3, relieving inhibition of lipoprotein lipase and endothelial lipase and lowering LDL-C through mechanisms that do not require a functional LDL receptor.','B':'PCSK9 inhibition depends substantially on LDL-receptor recycling and does not fit the absent-LDLR clue.','C':'Statin-mediated HMG-CoA-reductase inhibition upregulates LDL receptors and does not directly explain rescued lipase activities.','D':'NPC1L1 inhibition reduces intestinal cholesterol absorption but does not directly release LPL/EL from inhibition.','E':'ApoB is a structural apolipoprotein, but direct ApoB blockade is not the documented mechanism and does not explain increased LPL/EL activity.'},
        'Recognize ANGPTL3 inhibition as an LDL-receptor-independent lipid-lowering mechanism that releases lipase activity.',
        [src(1471,'LABEL','EVKEEZA- evinacumab injection, solution, concentrate','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=73412138-6d8f-4ea6-bb72-a740190470ff','73412138-6d8f-4ea6-bb72-a740190470ff','12.1 Mechanism of Action','2025-09-25')],
        'B','PCSK9 is a strong lipid-lowering alternative, but its effect requires LDLR recycling and it does not explain release of LPL and endothelial lipase from ANGPTL3 inhibition.'))

    I.append(mk(1472,'sotagliflozin','Cardiovascular System',['Pharmacology','Physiology'],
        'A patient taking sotagliflozin has increased urinary glucose excretion and reduced postprandial intestinal glucose absorption. In separate renal and intestinal preparations, sodium-glucose cotransport falls in both tissues.',
        'Which transporter profile best explains the two-compartment effect?',
        {'A':'Selective SGLT1 inhibition only','B':'Inhibition of both SGLT2 and SGLT1','C':'Selective GLUT2 inhibition','D':'SGLT2 inhibition plus intestinal GLUT5 inhibition','E':'Renal NKCC2 inhibition plus intestinal SGLT1 activation'},'B',
        'Dual SGLT2/SGLT1 inhibition in kidney and intestine','moderate',
        'Sotagliflozin inhibits both SGLT2 and SGLT1: SGLT2 inhibition reduces renal glucose/sodium reabsorption, while SGLT1 inhibition reduces intestinal glucose/sodium absorption.',
        {'A':'SGLT1 inhibition explains the intestinal effect but does not account for the labeled renal SGLT2 component.','B':'Sotagliflozin inhibits both SGLT2 and SGLT1: SGLT2 inhibition reduces renal glucose/sodium reabsorption, while SGLT1 inhibition reduces intestinal glucose/sodium absorption.','C':'GLUT2 is a facilitative transporter and is not the dual sodium-glucose cotransporter target of sotagliflozin.','D':'The intestinal component is SGLT1, not GLUT5.','E':'NKCC2 and SGLT1 activation do not match either the drug target or the direction of intestinal glucose transport.'},
        'Distinguish dual SGLT1/SGLT2 inhibition from selective renal SGLT2 blockade using tissue-specific transport effects.',
        [src(1472,'LABEL','INPEFA- sotagliflozin tablet','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1a46614e-05f6-421a-b6f4-d6f8760d643a','1a46614e-05f6-421a-b6f4-d6f8760d643a','12.1 Mechanism of Action','2026-08-12')],
        'A','SGLT1 blockade explains the intestinal phenotype and some renal transport, but the current label explicitly identifies dual SGLT2/SGLT1 inhibition.'))

    I.append(mk(1473,'pegcetacoplan','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'Red cells from a patient with paroxysmal nocturnal hemoglobinuria are studied during pegcetacoplan therapy. C3b deposition on red cells decreases, and terminal complement-mediated intravascular hemolysis also falls.',
        'Which direct target allows one intervention to reduce both proximal opsonization and downstream membrane-attack-complex formation?',
        {'A':'Complement C1s','B':'Complement factor B','C':'Complement C3 and C3b','D':'Complement C5 only','E':'CD59'},'C',
        'Proximal C3/C3b blockade controls both C3 opsonization and terminal complement','moderate-hard',
        'Pegcetacoplan binds complement C3 and C3b, regulating C3 cleavage and downstream complement effectors; proximal C3 blockade can reduce both C3b-mediated extravascular hemolysis and terminal-complement-mediated intravascular hemolysis.',
        {'A':'C1s blockade is restricted to the classical pathway and does not directly explain broad proximal C3 control in PNH.','B':'Factor B inhibition targets the alternative pathway but is not pegcetacoplan’s direct binding target.','C':'Pegcetacoplan binds complement C3 and C3b, regulating C3 cleavage and downstream complement effectors; proximal C3 blockade can reduce both C3b-mediated extravascular hemolysis and terminal-complement-mediated intravascular hemolysis.','D':'C5 blockade can reduce terminal hemolysis but leaves proximal C3b opsonization relatively intact.','E':'CD59 is absent or deficient on the PNH clone; pegcetacoplan does not restore this GPI-anchored protein.'},
        'Use proximal-versus-terminal complement physiology to distinguish C3 inhibition from C5 inhibition.',
        [src(1473,'LABEL','EMPAVELI- pegcetacoplan injection, solution','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c23d89e9-b00b-4520-e053-2995a90a95af','c23d89e9-b00b-4520-e053-2995a90a95af','12.1 Mechanism of Action','2025-07-30')],
        'D','C5 blockade is highly plausible in PNH and reduces intravascular hemolysis, but it cannot directly account for the marked reduction in C3b opsonization.'))

    I.append(mk(1474,'zongertinib','Respiratory & Renal/Urinary Systems',['Pharmacology','Biochemistry'],
        'Non-small cell lung cancer cells harboring an activating ERBB2 tyrosine-kinase-domain mutation are exposed to zongertinib. HER2 phosphorylation falls, followed by reduced ERK phosphorylation and reduced proliferation.',
        'Which protein is directly inhibited by the drug?',
        {'A':'EGFR ligand','B':'ERK1/2','C':'PI3K-alpha','D':'HER2 kinase','E':'MET kinase'},'D',
        'Direct HER2 kinase inhibition in HER2-mutant NSCLC','moderate',
        'Zongertinib is a HER2 kinase inhibitor; it inhibits HER2 phosphorylation and downstream signaling such as ERK phosphorylation in cells with activating HER2 kinase-domain mutations.',
        {'A':'An extracellular EGFR ligand is not the direct kinase target identified by the current label.','B':'ERK phosphorylation decreases downstream, but ERK is not the directly inhibited kinase.','C':'PI3K-alpha is a different signaling kinase and does not explain the direct loss of HER2 phosphorylation.','D':'Zongertinib is a HER2 kinase inhibitor; it inhibits HER2 phosphorylation and downstream signaling such as ERK phosphorylation in cells with activating HER2 kinase-domain mutations.','E':'MET is not the direct zongertinib target identified in the current label.'},
        'Localize a targeted kinase inhibitor using receptor phosphorylation and downstream signaling data.',
        [src(1474,'LABEL','HERNEXEOS- zongertinib tablet, film coated','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d3fabf12-354e-4e5c-b5de-20fdb579b783','d3fabf12-354e-4e5c-b5de-20fdb579b783','12.1 Mechanism of Action','2026-07-31','Current DailyMed SetID version 7/effective 2026-08-13 checked 2026-09-08; cited mechanism section dated 2026-07-31.')],
        'B','ERK is a downstream kinase whose phosphorylation falls, but the stem and current label localize direct inhibition to HER2.'))

    I.append(mk(1475,'zolbetuximab-clzb','Gastrointestinal System',['Pharmacology','Immunology'],
        'Gastric-cancer cells expressing a tight-junction protein are incubated with zolbetuximab-clzb and then with immune effector cells and complement. Antibody-dependent cellular cytotoxicity and complement-dependent cytotoxicity selectively increase in the antigen-positive cells.',
        'Which cell-surface antigen is directly targeted?',
        {'A':'HER2','B':'PD-L1','C':'EGFR','D':'Trop-2','E':'Claudin 18.2'},'E',
        'CLDN18.2-directed ADCC and CDC','moderate',
        'Zolbetuximab-clzb is a CLDN18.2-directed cytolytic antibody that depletes CLDN18.2-positive cells through ADCC and CDC.',
        {'A':'HER2 is a gastric-cancer target for other antibodies, but it is not the antigen bound by zolbetuximab.','B':'PD-L1 blockade alters immune checkpoint signaling rather than directly producing the documented CLDN18.2-selective cytolysis.','C':'EGFR is not the direct target identified in the current label.','D':'Trop-2 is targeted by several antibody-drug conjugates but is not the zolbetuximab antigen.','E':'Zolbetuximab-clzb is a CLDN18.2-directed cytolytic antibody that depletes CLDN18.2-positive cells through ADCC and CDC.'},
        'Identify CLDN18.2 as a gastric-cancer surface antigen targeted by an antibody that recruits cellular and complement cytotoxicity.',
        [src(1475,'LABEL','VYLOY- zolbetuximab injection, powder, for suspension','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e7695a21-abb6-47ac-93f8-0ece5a9c4409','e7695a21-abb6-47ac-93f8-0ece5a9c4409','12.1 Mechanism of Action','2024-10-18','Current DailyMed page checked 2026-09-08; current clinical-pharmacology container shows 2025-06-12 and the mechanism subsection itself is dated 2024-10-18.')],
        'A','HER2 is a common gastric-cancer antigen, but the immune-effector mechanism and current VYLOY label specifically identify CLDN18.2.'))

    assert len(I) == 25 and [x['num'] for x in I] == list(range(1451,1476))
    keys = ''.join(x['item']['intended_key'] for x in I)
    assert keys == 'ABCDEABCDEABCDEABCDEABCDE'
    assert Counter(keys) == Counter({'A':5,'B':5,'C':5,'D':5,'E':5})
    text = json.dumps(I, ensure_ascii=False).casefold()
    assert 'ncjmm' not in text
    allowed = {'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology','Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'}
    assert all(set(x['blueprint']['disciplines']).issubset(allowed) for x in I)

    systems = Counter(x['blueprint']['primary_system'] for x in I)
    batch = {
        'batch_id':'Q1451-Q1475-20260908',
        'created_at':'2026-09-08',
        'status':'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':25,
        'preceding_candidate_range':'Q1301-Q1450',
        'new_workstream_candidate_count':175,
        'canonical_count_before':1300,
        'canonical_count_after':1300,
        'answer_key_sequence':keys,
        'answer_key_distribution':dict(sorted(Counter(keys).items())),
        'systems':dict(systems),
        'shared_sources':[
            {'source_id':'USMLE-SPEC','title':'Step 1 Exam Content','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications','retrieved_at':'2026-09-08','section_locator':'Step 1 Content Specifications; Physician Tasks/Competencies Specifications; Discipline Specifications'},
            {'source_id':'USMLE-FORMAT','title':'Step 1 Formats & Questions','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-test-question-formats','retrieved_at':'2026-09-08','section_locator':'Patient-centered single-best-answer format; four or more response options'}
        ],
        'technical_integrity':{
            'evidence_map_contract':'A-E list materialized at authoring; claim text is programmatically bound to the matching A-E rationale; key=direct and distractors=inference.',
            'per_source_page_hashes_required_by_current_legacy_importer':False,
            'candidate_git_blob_binding_required_before_finalization':True,
            'deterministic_live_source_preflight_complete':False,
            'independent_auditor_a_complete':False,
            'independent_auditor_b_complete':False,
            'trusted_importer_complete':False
        },
        'scope':'Original USMLE Step 1 pharmacology/foundational-science supplement emphasizing target localization, pathway reasoning, protein engineering, gene/cell therapy, biochemical replacement, transport physiology, and single-best-answer discrimination. Same-author QA is not independent audit evidence.',
        'items':I
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(batch, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT','path':str(OUT.relative_to(ROOT.parent)),'count':25,'keys':keys,'systems':dict(systems)},ensure_ascii=False,sort_keys=True))


if __name__ == '__main__':
    build()
