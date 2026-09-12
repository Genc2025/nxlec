#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/13_q1561_q1565_author_20260912.json')
DB_BLOB='4c66c4f671a46eb3b0d29cbf8f8e6d15db85b83f'
TODAY='2026-09-12'

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
    return x

def set_locator(x,loc):
    x['sources'][0]['section_locator']=loc
    for e in x['evidence_map']:
        e['source_locator']=loc

def main():
    items=[]

    items.append(make(
        1561,'lenacapavir','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Microbiology'],
        'HIV-1-infected cells are exposed to lenacapavir. Reverse transcription still produces viral DNA, but nuclear entry of the viral replication complex is impaired; in producer cells, virion assembly and capsid-core formation are also disrupted.',
        'Which viral structure is directly bound by this drug?',
        {'A':'Capsid protein','B':'Reverse transcriptase','C':'Integrase','D':'gp120 envelope glycoprotein','E':'Protease'},
        'A','Direct binding to HIV-1 capsid protein at the interface between capsid subunits',
        'Lenacapavir is a multistage HIV-1 capsid inhibitor. It binds the capsid protein and disrupts capsid-dependent processes including nuclear uptake of viral DNA, virion assembly and release, and proper capsid-core formation.',
        {'A':'Correct. Lenacapavir directly binds HIV-1 capsid protein and interferes with multiple capsid-dependent stages of replication.','B':'Reverse transcriptase inhibition would prevent formation of viral DNA, which remains intact in the vignette.','C':'Integrase inhibitors block insertion of viral DNA into host DNA but do not directly explain defects in capsid-mediated nuclear entry and virion core assembly.','D':'gp120-targeting agents interfere with attachment or entry rather than intracellular capsid-dependent processes.','E':'Protease inhibition impairs viral polyprotein processing rather than directly targeting the capsid interface described here.'},
        'Recognize HIV-1 capsid as a direct antiviral target that affects multiple replication stages distinct from reverse transcriptase, integrase, entry, and protease mechanisms.',
        'SUNLENCA- lenacapavir sodium tablet, film coated; SUNLENCA- lenacapavir sodium kit','e5652804-29c4-40d7-aeb2-0142ed2a7b5b','C',
        'Integrase inhibition is plausible because it also acts after reverse transcription, but the combined nuclear-entry and capsid-core defects specifically identify capsid inhibition.'
    ))

    items.append(make(
        1562,'baloxavir marboxil','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Microbiology'],
        'Influenza A virus infects respiratory epithelial cells. After exposure to baloxavir, viral RNA polymerase can no longer efficiently generate capped viral mRNA even though host RNA polymerase II continues to synthesize capped host transcripts.',
        'Which viral process is most directly inhibited?',
        {'A':'Neuraminidase-mediated virion release','B':'Cap-dependent endonuclease cleavage of host pre-mRNA','C':'M2 proton-channel-mediated uncoating','D':'Fusion of the viral envelope with the endosomal membrane','E':'Viral RNA-dependent RNA polymerase elongation after primer formation'},
        'B','Inhibition of the influenza PA cap-dependent endonuclease required for cap-snatching',
        'Baloxavir inhibits the cap-dependent endonuclease activity of the polymerase acidic protein of influenza virus. This prevents cleavage of capped host pre-mRNAs used as primers for viral mRNA synthesis, thereby blocking viral transcription.',
        {'A':'Neuraminidase inhibitors block release of progeny virions rather than cap-snatching during viral transcription.','B':'Correct. Baloxavir inhibits the PA cap-dependent endonuclease that cleaves capped host pre-mRNAs for use as viral transcription primers.','C':'M2 inhibition affects uncoating of influenza A virus and is mechanistically distinct from the transcription defect described.','D':'Endosomal fusion depends on hemagglutinin conformational changes rather than the PA endonuclease.','E':'Baloxavir does not primarily inhibit polymerase elongation; it prevents generation of the capped primer required to initiate viral mRNA synthesis.'},
        'Differentiate influenza cap-snatching inhibition by baloxavir from neuraminidase, M2, fusion, and polymerase-elongation mechanisms.',
        'XOFLUZA- baloxavir marboxil tablet, film coated; XOFLUZA- baloxavir marboxil for oral suspension','e49e1a61-1b7c-4be5-ac84-af6240b511e7','A',
        'A polymerase-directed mechanism is plausible, but baloxavir specifically blocks the PA cap-dependent endonuclease step that supplies capped primers rather than RNA-chain elongation.'
    ))
    set_locator(items[-1],'12.4 Microbiology')

    items.append(make(
        1563,'fezolinetant','Reproductive System & Breast',['Pharmacology','Physiology'],
        'A postmenopausal patient with frequent vasomotor symptoms receives fezolinetant. Hypothalamic thermoregulatory instability improves without estrogen-receptor agonism.',
        'Which receptor is directly antagonized?',
        {'A':'Neurokinin-1 receptor','B':'Neurokinin-2 receptor','C':'Neurokinin-3 receptor','D':'Estrogen receptor-alpha','E':'Gonadotropin-releasing hormone receptor'},
        'C','Antagonism of neurokinin-3 receptors involved in hypothalamic thermoregulation',
        'Fezolinetant is a neurokinin-3 receptor antagonist. Blocking neurokinin B signaling at NK3 receptors in hypothalamic thermoregulatory pathways reduces menopausal vasomotor symptoms without acting as estrogen replacement.',
        {'A':'NK1 receptors primarily mediate substance P signaling and are not the direct target of fezolinetant.','B':'NK2 receptors preferentially bind neurokinin A and are not the target of this drug.','C':'Correct. Fezolinetant directly antagonizes neurokinin-3 receptors.','D':'Fezolinetant is nonhormonal and does not act as an ER-alpha antagonist or agonist.','E':'GnRH-receptor antagonism suppresses gonadotropin secretion but is not the mechanism of fezolinetant.'},
        'Recognize NK3-receptor antagonism as a nonhormonal mechanism for treatment of menopausal vasomotor symptoms.',
        'VEOZAH- fezolinetant tablet, film coated','cae9f798-24f9-4580-a4fc-e6c710cbda3c','E',
        'A GnRH-receptor mechanism could alter reproductive hormone signaling, but the direct thermoregulatory target of fezolinetant is the NK3 receptor.'
    ))

    items.append(make(
        1564,'osilodrostat','Endocrine System',['Pharmacology','Biochemistry'],
        'An adult with endogenous hypercortisolemia is treated with osilodrostat. Serum cortisol falls, and a steroid precursor immediately upstream of the inhibited enzymatic step accumulates.',
        'Which substance is expected to increase most directly?',
        {'A':'Aldosterone','B':'Cortisone','C':'17-hydroxypregnenolone','D':'11-deoxycortisol','E':'Dihydrotestosterone'},
        'D','Accumulation of 11-deoxycortisol after inhibition of CYP11B1 (11-beta-hydroxylase)',
        'Osilodrostat inhibits 11-beta-hydroxylase (CYP11B1), the enzyme that catalyzes the final step of cortisol synthesis. Blocking conversion of 11-deoxycortisol to cortisol lowers cortisol and directly favors accumulation of 11-deoxycortisol.',
        {'A':'Aldosterone synthesis involves CYP11B2 and is not the direct immediate substrate-product pair tested here.','B':'Cortisone is formed from cortisol by 11-beta-hydroxysteroid dehydrogenase type 2 rather than by CYP11B1.','C':'17-hydroxypregnenolone is several steps upstream of cortisol and is not the immediate CYP11B1 substrate.','D':'Correct. CYP11B1 converts 11-deoxycortisol to cortisol, so inhibition causes 11-deoxycortisol to rise.','E':'Dihydrotestosterone is generated from testosterone by 5-alpha-reductase and is outside the inhibited cortisol-synthesis step.'},
        'Link CYP11B1 inhibition to reduced cortisol synthesis and accumulation of its immediate precursor, 11-deoxycortisol.',
        'ISTURISA- osilodrostat tablet, coated','f3a5ec24-63c3-4d83-b1c0-6c550fbe7ae2','B',
        'Other adrenal steroids may change secondarily, but the immediate substrate of the inhibited CYP11B1 reaction is 11-deoxycortisol.'
    ))

    items.append(make(
        1565,'vosoritide','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Cell Biology'],
        'Growth-plate chondrocytes from a child with achondroplasia are exposed to vosoritide. Signaling downstream of overactive FGFR3 is attenuated and endochondral bone growth increases.',
        'Which intracellular second messenger is most directly increased by the drug-receptor interaction?',
        {'A':'Cyclic AMP','B':'Inositol trisphosphate','C':'Diacylglycerol','D':'Calcium released from the endoplasmic reticulum','E':'Cyclic GMP'},
        'E','NPR-B activation with guanylyl cyclase activity and increased intracellular cGMP',
        'Vosoritide is an analog of C-type natriuretic peptide that binds natriuretic peptide receptor-B. NPR-B has guanylyl cyclase activity, increasing intracellular cyclic GMP and antagonizing downstream signaling from FGFR3 to promote endochondral bone growth.',
        {'A':'cAMP is generated by adenylyl cyclase-coupled pathways, not by NPR-B.','B':'IP3 is generated through phospholipase C signaling rather than natriuretic peptide receptor guanylyl cyclase activity.','C':'DAG is also a phospholipase C product and is not the principal second messenger generated by NPR-B.','D':'ER calcium release is downstream of IP3 and does not represent the direct signal generated by NPR-B.','E':'Correct. NPR-B activation stimulates guanylyl cyclase and increases intracellular cGMP.'},
        'Connect CNP analog signaling through NPR-B with increased cGMP and antagonism of FGFR3-mediated growth inhibition in achondroplasia.',
        'VOXZOGO- vosoritide kit','228e8560-04a4-4bb1-a81f-29531a9e4d27','A',
        'cAMP is a common cyclic-nucleotide second messenger, but NPR-B is a receptor guanylyl cyclase and therefore directly raises cGMP.'
    ))

    b={
        'batch_id':'Q1561-Q1565-20260912',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1560,
        'canonical_count_after':1560,
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
    assert [x['num'] for x in items]==list(range(1561,1566))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
