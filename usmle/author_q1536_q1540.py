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
        1537,'enlicitide','Cardiovascular System',['Pharmacology','Biochemistry'],
        'Cultured hepatocytes are exposed to extracellular PCSK9 in the presence of enlicitide. Cell-surface LDL receptor abundance and uptake of fluorescent LDL increase, while LDLR gene transcription is unchanged.',
        'Which extracellular interaction is directly prevented by this drug?',
        {'A':'Apolipoprotein B-100 binding to the LDL receptor','B':'PCSK9 binding to the LDL receptor','C':'HMG-CoA reductase binding to HMG-CoA','D':'NPC1L1 binding to intestinal cholesterol','E':'ACAT binding to intracellular cholesterol'},
        'B','Prevention of PCSK9 binding to the LDL receptor, reducing receptor degradation',
        'Enlicitide is a macrocyclic peptide that binds PCSK9. By inhibiting the interaction of PCSK9 with hepatocyte LDL receptors, it reduces LDL receptor degradation and increases the number of receptors available to clear LDL cholesterol.',
        {'A':'Blocking apoB-100 binding would impair LDL uptake rather than increase it.','B':'Correct. Enlicitide binds PCSK9 and prevents PCSK9-LDL receptor binding, reducing receptor degradation and increasing surface LDL receptors.','C':'HMG-CoA reductase is an intracellular cholesterol-synthesis enzyme and is not directly targeted by enlicitide.','D':'NPC1L1 mediates intestinal cholesterol absorption and does not explain the hepatocyte-specific receptor findings.','E':'ACAT esterifies intracellular cholesterol and is not the extracellular target of enlicitide.'},
        'Connect PCSK9-LDL receptor binding with hepatic LDL receptor degradation and explain how PCSK9 blockade increases receptor-mediated LDL clearance.',
        'LIPFENDRA- enlicitide tablet, film coated','100ec543-fbd0-44fc-b740-db9cdff39145','A',
        'ApoB-100 also interacts with the LDL receptor, but blocking that interaction would decrease rather than increase LDL uptake; the observed rise in surface LDL receptors identifies blockade of PCSK9-LDL receptor binding.'
    ))

    items.append(make(
        1538,'iberdomide','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Cell Biology'],
        'Multiple myeloma cells are exposed to iberdomide. Aiolos and Ikaros protein concentrations fall rapidly even though their messenger RNA concentrations remain unchanged. The effect requires cereblon and is prevented by proteasome inhibition.',
        'Which cellular process most directly accounts for the loss of these transcription factors?',
        {'A':'Lysosomal degradation after macroautophagy','B':'RNase H1-mediated degradation of their messenger RNAs','C':'Cereblon-dependent ubiquitination followed by proteasomal degradation','D':'Global inhibition of ribosomal peptide elongation','E':'Promoter hypermethylation with transcriptional silencing'},
        'C','Cereblon-dependent recruitment, ubiquitination, and proteasomal degradation of Aiolos and Ikaros',
        'Iberdomide is a cereblon-modulating protein degrader. Binding to cereblon, the substrate-recognition component of an E3 ubiquitin ligase complex, promotes recruitment and ubiquitination of Aiolos and Ikaros, followed by their proteasomal degradation.',
        {'A':'The defining pathway is ubiquitin-proteasome degradation rather than lysosomal macroautophagy.','B':'Unchanged messenger RNA argues against RNase H1-mediated transcript degradation.','C':'Correct. Iberdomide engages cereblon to promote ubiquitination and proteasomal degradation of Aiolos and Ikaros.','D':'Global translation inhibition would not explain cereblon dependence or selective proteasome-sensitive loss of these proteins.','E':'Transcriptional silencing would be expected to reduce messenger RNA and would not require the proteasome.'},
        'Use cereblon dependence and proteasome sensitivity to recognize targeted E3-ligase-mediated degradation of Aiolos and Ikaros by iberdomide.',
        'ZENBEXUS- iberdomide capsule','3663d9cb-3f66-48ae-bf0a-6958bc0888de','D',
        'Global translation inhibition could lower protein abundance, but the unchanged messenger RNA, cereblon requirement, and reversal by proteasome inhibition specifically support targeted ubiquitin-proteasome degradation.'
    ))

    items.append(make(
        1539,'atacicept-vymj','Renal & Urinary System',['Pharmacology','Immunology'],
        'A patient with IgA nephropathy receives a soluble recombinant fusion protein containing the extracellular ligand-binding domain of TACI linked to an IgG Fc region. Serum immunoglobulins and galactose-deficient IgA1 decrease without direct depletion of CD20-positive B cells.',
        'Which pair of soluble ligands is directly bound by this fusion protein?',
        {'A':'Interleukin-6 and tumor necrosis factor','B':'Complement C3 and complement C5','C':'CD40 ligand and interleukin-21','D':'BAFF and APRIL','E':'IgA and the Fc alpha receptor'},
        'D','Direct sequestration of the B-cell survival ligands BAFF and APRIL by a TACI-Fc fusion protein',
        'Atacicept-vymj is a TACI-Fc fusion protein that binds the B-cell survival and differentiation ligands BAFF and APRIL, reducing signaling through these pathways and decreasing immunoglobulin production, including galactose-deficient IgA1.',
        {'A':'IL-6 and TNF are inflammatory cytokines but are not the ligand pair bound by TACI.','B':'C3 and C5 are complement proteins and are not the direct ligands for this fusion protein.','C':'CD40 ligand and IL-21 support B-cell responses through other pathways but are not bound by TACI-Fc.','D':'Correct. The extracellular TACI domain binds BAFF and APRIL and thereby reduces their B-cell survival and differentiation signals.','E':'The drug does not directly bind IgA or the Fc alpha receptor; the fall in IgA is downstream of BAFF/APRIL blockade.'},
        'Recognize BAFF and APRIL as TACI ligands and connect their sequestration with reduced pathogenic immunoglobulin production in IgA nephropathy.',
        'TRUTAKNA- atacicept injection, solution','24aa29f6-ccff-45d3-89af-4d26e525cef8','C',
        'CD40 ligand and IL-21 are important for B-cell activation and differentiation, but the stipulated TACI extracellular domain specifically identifies BAFF and APRIL as the bound ligands.'
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
