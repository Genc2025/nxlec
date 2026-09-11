#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/05_q1521_q1525_author_20260911.json')
DB_BLOB='9c5d4b80cffe94bd408076f4c6956c62db51d7a6'
TODAY='2026-09-11'

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
    return x

def main():
    items=[]
    items.append(make(
        1521,
        'donanemab-azbt',
        'Nervous System & Special Senses',
        ['Pharmacology','Pathology'],
        'A monoclonal antibody is added to brain tissue from a patient with early symptomatic Alzheimer disease. The antibody binds an insoluble amyloid species enriched within established plaques, and serial amyloid PET studies after treatment show a marked reduction in plaque burden. It does not inhibit beta- or gamma-secretase activity.',
        'Which molecular species is the direct target of this antibody?',
        {
            'A':'Insoluble N-truncated pyroglutamate amyloid beta',
            'B':'Soluble monomeric amyloid beta exclusively',
            'C':'Hyperphosphorylated tau in neurofibrillary tangles',
            'D':'Beta-site amyloid precursor protein cleaving enzyme 1',
            'E':'Presenilin-containing gamma-secretase complex'
        },
        'A',
        'Binding of insoluble N-truncated pyroglutamate amyloid beta within plaques',
        'Donanemab-azbt is a humanized IgG1 monoclonal antibody directed against insoluble N-truncated pyroglutamate amyloid beta and reduces amyloid beta plaques.',
        {
            'A':'Correct. Donanemab-azbt directly recognizes insoluble N-truncated pyroglutamate amyloid beta enriched in established plaques.',
            'B':'The labeled target is an insoluble N-truncated pyroglutamate amyloid species rather than soluble monomeric amyloid beta exclusively.',
            'C':'Tau-directed therapies target a different Alzheimer disease proteinopathy; donanemab is directed against amyloid beta.',
            'D':'BACE1 inhibition would reduce amyloid-beta production upstream rather than bind an existing insoluble plaque-associated amyloid species.',
            'E':'Gamma-secretase inhibition alters amyloid precursor protein processing and is not the direct mechanism of this monoclonal antibody.'
        },
        'Differentiate plaque-directed anti-amyloid antibodies from therapies that alter amyloid production or target tau.',
        'KISUNLA- donanemab-azbt injection, solution',
        '190352d4-ef62-4679-b4fa-e846e2766afa',
        'B',
        'Other anti-amyloid antibodies may recognize soluble aggregated species, but the stipulated insoluble plaque-associated N-truncated pyroglutamate epitope identifies the labeled donanemab target.'
    ))

    items.append(make(
        1522,
        'suzetrigine',
        'Nervous System & Special Senses',
        ['Pharmacology','Physiology'],
        'A peripheral sensory neuron is exposed to suzetrigine during a patch-clamp experiment. Repetitive action-potential firing triggered by a painful stimulus decreases, but sodium currents mediated by most other voltage-gated sodium-channel subtypes are relatively preserved. The affected channel is highly expressed in dorsal root ganglion neurons.',
        'Which direct pharmacologic action best explains these findings?',
        {
            'A':'Blockade of voltage-gated calcium channel alpha-2-delta subunits',
            'B':'Selective blockade of the NaV1.8 voltage-gated sodium channel',
            'C':'Agonism of mu-opioid receptors',
            'D':'Blockade of NMDA receptors',
            'E':'Inhibition of cyclooxygenase-2'
        },
        'B',
        'Selective NaV1.8 blockade in peripheral sensory neurons',
        'Suzetrigine selectively blocks the NaV1.8 voltage-gated sodium channel relative to other known voltage-gated sodium channels. NaV1.8 is expressed in peripheral sensory neurons, including dorsal root ganglion neurons, where it contributes to action-potential transmission of pain signals.',
        {
            'A':'Alpha-2-delta ligands modulate voltage-gated calcium channels rather than selectively suppress NaV1.8 sodium current.',
            'B':'Correct. Suzetrigine selectively inhibits NaV1.8 in peripheral sensory neurons and thereby reduces propagation of pain signals.',
            'C':'Mu-opioid receptor agonism decreases nociceptive transmission through G-protein signaling but does not selectively block a peripheral sodium-channel subtype.',
            'D':'NMDA-receptor blockade targets glutamatergic signaling rather than NaV1.8-dependent action-potential conduction.',
            'E':'COX-2 inhibition reduces prostaglandin synthesis and peripheral sensitization but does not directly block voltage-gated sodium current.'
        },
        'Recognize selective NaV1.8 blockade as a nonopioid analgesic mechanism that reduces pain-signal transmission in peripheral sensory neurons.',
        'JOURNAVX- suzetrigine tablet, film coated',
        'f0976da4-1d20-4517-945c-b60ed2f41c12',
        'A',
        'Alpha-2-delta ligands are also nonopioid agents that reduce neuronal excitability, but the patch-clamp finding of selective suppression of a dorsal-root-ganglion sodium-channel current identifies NaV1.8 blockade.'
    ))

    items.append(make(
        1523,
        'ensifentrine',
        'Respiratory System',
        ['Pharmacology','Physiology'],
        'Airway cells are exposed to ensifentrine. Intracellular cyclic AMP increases, cyclic GMP can also increase, and downstream signaling changes occur without direct stimulation of a beta-2 adrenergic receptor. The drug inhibits one phosphodiesterase that hydrolyzes cAMP and cGMP and another that hydrolyzes cAMP only.',
        'Which pair of enzymes is directly inhibited?',
        {
            'A':'PDE1 and PDE2',
            'B':'PDE2 and PDE5',
            'C':'PDE3 and PDE4',
            'D':'PDE4 and PDE5',
            'E':'PDE5 and PDE6'
        },
        'C',
        'Dual inhibition of PDE3 and PDE4',
        'Ensifentrine is a small-molecule inhibitor of PDE3 and PDE4. PDE3 hydrolyzes cAMP and can hydrolyze cGMP, whereas PDE4 hydrolyzes cAMP; inhibition increases intracellular cyclic nucleotide levels.',
        {
            'A':'PDE1 and PDE2 are not the labeled enzyme targets of ensifentrine.',
            'B':'PDE5 principally hydrolyzes cGMP and is not part of the labeled ensifentrine target pair.',
            'C':'Correct. Ensifentrine directly inhibits PDE3 and PDE4, increasing intracellular cyclic nucleotide signaling.',
            'D':'PDE4 is a target, but PDE5 is not; the second labeled target is PDE3.',
            'E':'PDE5/PDE6 inhibition is characteristic of other phosphodiesterase inhibitor profiles and does not fit ensifentrine.'
        },
        'Recognize ensifentrine as a dual PDE3/PDE4 inhibitor and connect phosphodiesterase substrate specificity with intracellular cyclic-nucleotide accumulation.',
        'OHTUVAYRE- ensifentrine suspension',
        'e6433c98-41a0-4f99-8f7f-d0e9db6e3f40',
        'D',
        'PDE4 inhibition can account for increased cAMP, but the simultaneous involvement of an enzyme capable of hydrolyzing both cAMP and cGMP identifies PDE3 as the second target rather than PDE5.'
    ))

    items.append(make(
        1524,
        'zolbetuximab-clzb',
        'Gastrointestinal System',
        ['Pharmacology','Immunology'],
        'A gastric adenocarcinoma cell line expresses high levels of a tight-junction protein normally restricted to differentiated gastric mucosa. Exposure to zolbetuximab-clzb results in antibody-dependent cellular cytotoxicity and complement-dependent cytotoxicity against the tumor cells.',
        'Which tumor-associated antigen is directly bound by this antibody?',
        {
            'A':'HER2',
            'B':'PD-L1',
            'C':'VEGF-A',
            'D':'Claudin 18.2',
            'E':'EGFR'
        },
        'D',
        'CLDN18.2-directed cytolytic antibody activity',
        'Zolbetuximab-clzb is a claudin 18.2-directed cytolytic antibody. Binding to CLDN18.2-positive cells promotes antibody-dependent cellular cytotoxicity and complement-dependent cytotoxicity.',
        {
            'A':'HER2-directed antibodies act on a receptor tyrosine kinase and do not define the CLDN18.2-directed cytotoxic mechanism described.',
            'B':'PD-L1 blockade modifies immune checkpoint signaling rather than directly producing the labeled CLDN18.2-directed ADCC/CDC mechanism.',
            'C':'VEGF-A neutralization is antiangiogenic and does not target a gastric epithelial tight-junction antigen.',
            'D':'Correct. Zolbetuximab-clzb directly binds claudin 18.2 and can deplete antigen-positive cells through ADCC and CDC.',
            'E':'EGFR is a receptor tyrosine kinase target of other antibodies and is not the direct antigen bound by zolbetuximab-clzb.'
        },
        'Associate zolbetuximab-clzb with CLDN18.2 and distinguish antigen-directed ADCC/CDC from growth-factor and checkpoint-targeted therapies.',
        'VYLOY- zolbetuximab injection, powder, for suspension',
        'e7695a21-abb6-47ac-93f8-0ece5a9c4409',
        'A',
        'HER2 is a clinically relevant gastric-cancer target, but the tight-junction antigen plus ADCC/CDC profile in the vignette identifies CLDN18.2 rather than HER2.'
    ))

    items.append(make(
        1525,
        'mavorixafor',
        'Blood & Lymphoreticular/Immune Systems',
        ['Pharmacology','Immunology'],
        'A patient with WHIM syndrome has a gain-of-function mutation causing excessive responsiveness of a chemokine receptor to CXCL12 and retention of mature leukocytes in the bone marrow. After treatment with mavorixafor, circulating neutrophil and lymphocyte counts increase.',
        'Which direct action best explains the change in leukocyte distribution?',
        {
            'A':'Agonism of granulocyte colony-stimulating factor receptor',
            'B':'Neutralization of CXCL8',
            'C':'Inhibition of complement factor B',
            'D':'Antagonism of CCR5',
            'E':'Antagonism of CXCR4 that blocks CXCL12 binding'
        },
        'E',
        'CXCR4 antagonism that blocks CXCL12-dependent marrow retention',
        'Mavorixafor is an orally bioavailable CXCR4 antagonist that blocks binding of CXCL12/SDF-1α. In WHIM syndrome, excessive CXCR4 signaling promotes leukocyte retention in bone marrow; antagonism increases leukocyte mobilization into peripheral blood.',
        {
            'A':'G-CSF receptor stimulation can increase neutrophil production and mobilization, but it does not directly correct CXCL12-hypersensitive CXCR4 signaling.',
            'B':'CXCL8 is a neutrophil chemokine but is not the ligand-receptor axis responsible for WHIM-associated marrow retention.',
            'C':'Factor B inhibition acts in the alternative complement pathway and does not explain leukocyte trafficking from marrow.',
            'D':'CCR5 antagonism alters a different chemokine-receptor pathway and does not block CXCL12-mediated CXCR4 signaling.',
            'E':'Correct. CXCR4 antagonism blocks CXCL12 binding and reduces abnormal marrow retention, increasing circulating mature leukocytes.'
        },
        'Connect WHIM syndrome to gain-of-function CXCR4 signaling and recognize CXCR4 antagonism as a mechanism for releasing retained leukocytes from bone marrow.',
        'XOLREMDI- mavorixafor capsule, gelatin coated',
        '7f3a5ee3-ca73-4876-85a0-ed1e108a2237',
        'A',
        'G-CSF can also raise circulating neutrophils, but the vignette specifies the pathogenic CXCL12-CXCR4 retention axis and mavorixafor directly antagonizes CXCR4.'
    ))

    b={
        'batch_id':'Q1521-Q1525-20260911',
        'created_at':'2026-09-11',
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1520,
        'canonical_count_after':1520,
        'canonical_db_blob':DB_BLOB,
        'answer_key_sequence':'ABCDE',
        'answer_key_distribution':{L:1 for L in 'ABCDE'},
        'technical_integrity':{
            'source_hashes_fabricated':False,
            'source_hashes_complete':False,
            'independent_audit_complete':False,
            'trusted_importer_complete':False
        },
        'items':items
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    assert [x['num'] for x in items]==list(range(1521,1526))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
