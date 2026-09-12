#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/08_q1536_q1540_author_20260912.json')
DB_BLOB='a3f28fcfd0a89161ed003e60d0d797c5fa103f1a'
TODAY='2026-09-12'

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
    return x

def main():
    items=[]

    items.append(make(
        1536,'vimseltinib','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Cell Biology'],
        'Synovial tumor cells and macrophage-lineage cells from a tenosynovial giant cell tumor are exposed to vimseltinib. CSF1-induced receptor autophosphorylation and downstream signaling decrease, and proliferation of cells expressing the receptor is reduced.',
        'Which receptor is directly inhibited by this drug?',
        {'A':'Colony-stimulating factor 1 receptor','B':'Platelet-derived growth factor receptor beta','C':'KIT receptor tyrosine kinase','D':'Vascular endothelial growth factor receptor 2','E':'Fibroblast growth factor receptor 3'},
        'A','Direct inhibition of colony-stimulating factor 1 receptor kinase activity',
        'Vimseltinib is a kinase inhibitor that inhibits colony-stimulating factor 1 receptor (CSF1R), reducing CSF1-induced CSF1R autophosphorylation, downstream signaling, and proliferation of CSF1R-expressing cells.',
        {'A':'Correct. CSF1R inhibition directly matches the ligand-dependent autophosphorylation and proliferation findings.','B':'PDGFR-beta is a receptor tyrosine kinase but is not the documented direct target of vimseltinib.','C':'KIT inhibition is characteristic of other kinase inhibitors and does not explain the CSF1-specific receptor assay.','D':'VEGFR2 regulates angiogenic signaling rather than the CSF1-dependent pathway described.','E':'FGFR3 signaling is unrelated to the selective CSF1-induced receptor autophosphorylation in this experiment.'},
        'Identify CSF1R as the direct kinase target of vimseltinib and connect receptor inhibition with reduced CSF1-driven signaling.',
        'ROMVIMZA- vimseltinib capsule','f73c7a62-9601-4df0-810f-100f515d79ea','B',
        'PDGFR-beta is a plausible receptor-tyrosine-kinase alternative, but the CSF1-dependent autophosphorylation assay specifically identifies CSF1R.'
    ))

    items.append(make(
        1537,'mirdametinib','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Cell Biology'],
        'Cells from an NF1-associated plexiform neurofibroma have excessive RAS-pathway signaling. After exposure to mirdametinib, phosphorylation of ERK falls despite unchanged abundance of the upstream RAS protein.',
        'Which pair of kinases is directly inhibited?',
        {'A':'RAF1 and BRAF','B':'MEK1 and MEK2','C':'ERK1 and ERK2','D':'PI3K and AKT','E':'JAK1 and JAK2'},
        'B','Direct inhibition of MEK1 and MEK2 with reduced downstream ERK phosphorylation',
        'Mirdametinib inhibits mitogen-activated protein kinase kinases 1 and 2 (MEK1/2), which are upstream regulators of ERK. In vitro, it inhibits MEK1/2 kinase activity and downstream ERK phosphorylation.',
        {'A':'RAF proteins lie upstream of MEK, but mirdametinib is not a direct RAF inhibitor.','B':'Correct. Direct MEK1/2 inhibition reduces downstream ERK phosphorylation in the RAS-RAF-MEK-ERK pathway.','C':'ERK phosphorylation falls downstream, but ERK1/2 are not the documented direct kinase targets.','D':'PI3K-AKT is a parallel signaling branch and does not directly explain selective suppression of ERK phosphorylation by this drug.','E':'JAK-STAT signaling is a distinct cytokine-signaling pathway.'},
        'Localize mirdametinib action to MEK1/2 within the RAS-RAF-MEK-ERK signaling cascade.',
        'GOMEKLI- mirdametinib capsule GOMEKLI- mirdametinib tablet, for suspension','4c41bf90-5fa7-4935-a95c-e047ea6bbf8e','C',
        'ERK1/2 are the immediate downstream kinases whose phosphorylation decreases, but mirdametinib directly inhibits MEK1/2 rather than ERK.'
    ))

    items.append(make(
        1538,'gepotidacin','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
        'A susceptible Escherichia coli isolate is exposed to gepotidacin. DNA replication stops after inhibition of enzymes required for control of DNA topology and chromosome separation. Beta-lactam target proteins remain unaffected.',
        'Which bacterial enzymes are directly inhibited?',
        {'A':'DNA-dependent RNA polymerase and primase','B':'Dihydrofolate reductase and dihydropteroate synthase','C':'DNA gyrase and topoisomerase IV','D':'Penicillin-binding proteins 1 and 3','E':'The 30S and 50S ribosomal subunits'},
        'C','Inhibition of bacterial type II topoisomerases DNA gyrase and topoisomerase IV',
        'Gepotidacin inhibits bacterial type II topoisomerases, including DNA gyrase and topoisomerase IV, thereby inhibiting DNA replication.',
        {'A':'RNA polymerase inhibition blocks transcription, whereas gepotidacin targets bacterial type II topoisomerases.','B':'Sequential folate-pathway blockade is the mechanism of trimethoprim-sulfamethoxazole, not gepotidacin.','C':'Correct. Gepotidacin inhibits DNA gyrase and topoisomerase IV, preventing bacterial DNA replication.','D':'Penicillin-binding proteins are beta-lactam targets and are explicitly unaffected in the vignette.','E':'Ribosomal inhibition impairs translation rather than DNA topology and chromosome separation.'},
        'Recognize DNA gyrase and topoisomerase IV as the bacterial type II topoisomerase targets of gepotidacin.',
        'BLUJEPA- gepotidacin tablet, film coated','80b57cfe-7819-4d95-a57d-014af42f118d','D',
        'Penicillin-binding proteins are common antibacterial targets, but the described interruption of DNA topology and replication identifies type II topoisomerase inhibition.'
    ))
    items[-1]['sources'][0]['section_locator']='12.4 Microbiology; Mechanism of Action'
    for e in items[-1]['evidence_map']:
        e['source_locator']='12.4 Microbiology; Mechanism of Action'

    items.append(make(
        1539,'zongertinib','Respiratory System',['Pharmacology','Cell Biology'],
        'Non-small cell lung cancer cells harboring an activating HER2 tyrosine-kinase-domain mutation are exposed to zongertinib. HER2 phosphorylation decreases, followed by reduced ERK phosphorylation and reduced cellular proliferation.',
        'Which protein is the direct kinase target of this drug?',
        {'A':'EGFR','B':'ALK','C':'MET','D':'HER2','E':'KRAS G12C'},
        'D','Direct inhibition of HER2 kinase activity',
        'Zongertinib is a kinase inhibitor of human epidermal growth factor receptor 2 (HER2). It inhibits HER2 phosphorylation, downstream HER2 signaling including ERK phosphorylation, and proliferation of cells with activating HER2 kinase-domain mutations.',
        {'A':'EGFR is a related receptor tyrosine kinase but is not the direct target identified for zongertinib.','B':'ALK inhibition is used for ALK-rearranged tumors and does not explain selective suppression of mutant HER2 phosphorylation.','C':'MET is another oncogenic receptor tyrosine kinase but is not the zongertinib target.','D':'Correct. Zongertinib directly inhibits HER2 kinase activity, reducing HER2 and downstream ERK phosphorylation.','E':'KRAS G12C inhibition acts downstream of receptor tyrosine kinases and would not directly reduce HER2 phosphorylation.'},
        'Identify HER2 as the direct kinase target of zongertinib in HER2-mutant non-small cell lung cancer.',
        'HERNEXEOS- zongertinib tablet, film coated','d3fabf12-354e-4e5c-b5de-20fdb579b783','A',
        'EGFR is the closest receptor-family alternative, but the activating HER2 mutation and direct loss of HER2 phosphorylation identify HER2 as the target.'
    ))

    items.append(make(
        1540,'zenocutuzumab-zbco','Respiratory System',['Pharmacology','Cell Biology'],
        'NRG1 fusion-positive tumor cells depend on ligand-driven HER3 signaling through HER2-HER3 heterodimers. A bispecific IgG1 antibody reduces PI3K-AKT-mTOR signaling and tumor-cell proliferation without inhibiting an intracellular kinase domain.',
        'Which direct extracellular action best explains this effect?',
        {'A':'Binding EGFR and blocking EGF-induced homodimerization','B':'Binding MET and preventing HGF-dependent activation','C':'Binding PD-L1 and preventing PD-1 engagement','D':'Binding HER2 alone and inducing receptor internalization','E':'Binding both HER2 and HER3, inhibiting HER2-HER3 dimerization and preventing NRG1 binding to HER3'},
        'E','Bispecific extracellular binding to HER2 and HER3 that blocks NRG1-driven HER2-HER3 signaling',
        'Zenocutuzumab-zbco is a bispecific antibody that binds extracellular domains of HER2 and HER3, inhibits HER2-HER3 dimerization, and prevents NRG1 binding to HER3, reducing downstream PI3K-AKT-mTOR signaling.',
        {'A':'EGFR blockade does not directly interrupt the NRG1-HER3/HER2 signaling unit described.','B':'MET-HGF signaling is a distinct receptor-ligand pathway.','C':'PD-L1 blockade alters immune-checkpoint signaling rather than tumor-cell HER2-HER3 dimerization.','D':'Binding HER2 alone omits the defining bispecific HER2/HER3 interaction and prevention of NRG1 binding to HER3.','E':'Correct. Dual extracellular binding to HER2 and HER3 blocks receptor dimerization and NRG1-HER3 engagement.'},
        'Connect NRG1 fusion signaling with HER2-HER3 heterodimerization and recognize dual HER2/HER3 extracellular blockade by zenocutuzumab.',
        'BIZENGRI- zenocutuzumab injection','203daea4-fc87-40a4-a92f-ba2351b16de1','D',
        'HER2-only blockade is plausible because HER2 participates in the heterodimer, but zenocutuzumab is bispecific and directly binds both HER2 and HER3 while preventing NRG1 binding to HER3.'
    ))

    b={
        'batch_id':'Q1536-Q1540-20260912',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1535,
        'canonical_count_after':1535,
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
    assert [x['num'] for x in items]==list(range(1536,1541))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
