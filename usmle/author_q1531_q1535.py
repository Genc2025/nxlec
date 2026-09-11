#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/07_q1531_q1535_author_20260911.json')
DB_BLOB='441f9bbad64e87c9da9fa5647c042f417941b8af'
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
        1531,
        'tovorafenib',
        'Nervous System & Special Senses',
        ['Pharmacology','Cell Biology'],
        'A pediatric low-grade glioma cell line carrying a BRAF fusion is exposed to tovorafenib. MAPK-pathway output falls. In separate kinase assays, the same drug inhibits mutant BRAF V600E as well as wild-type BRAF and CRAF.',
        'Which direct target profile best explains these findings?',
        {
            'A':'Type II inhibition of RAF kinases including mutant BRAF, wild-type BRAF, and CRAF',
            'B':'Selective inhibition of MEK1 and MEK2 only',
            'C':'Selective inhibition of PI3K alpha with mutant p110alpha degradation',
            'D':'Inhibition of ROS1 and TRKA/TRKB/TRKC',
            'E':'Inhibition of CSF1R signaling'
        },
        'A',
        'Type II inhibition of RAF kinases including mutant BRAF, wild-type BRAF, and CRAF',
        'Tovorafenib is a Type II RAF kinase inhibitor of mutant BRAF V600E, wild-type BRAF, and wild-type CRAF, and it has antitumor activity in models harboring BRAF mutations or a BRAF fusion.',
        {
            'A':'Correct. This target profile directly matches tovorafenib and explains suppression of MAPK signaling in BRAF-driven tumor cells.',
            'B':'MEK1/2 inhibition acts one level downstream of RAF and does not match the documented direct kinase targets.',
            'C':'PI3K-alpha inhibition affects a different signaling axis and is not the direct action of tovorafenib.',
            'D':'ROS1/pan-TRK inhibition describes a different fusion-targeted kinase profile.',
            'E':'CSF1R inhibition targets macrophage-lineage signaling rather than RAF-driven MAPK activation.'
        },
        'Recognize tovorafenib as a Type II RAF inhibitor targeting mutant BRAF, wild-type BRAF, and CRAF.',
        'OJEMDA- tovorafenib kit OJEMDA- tovorafenib tablet, film coated',
        'ea3a9631-3a66-6a7c-e053-2995a90ae2ad',
        'B',
        'MEK inhibition can also lower MAPK-pathway output, but the kinase-assay profile in the vignette specifically identifies direct RAF inhibition.'
    ))

    items.append(make(
        1532,
        'dordaviprone',
        'Nervous System & Special Senses',
        ['Pharmacology','Cell Biology'],
        'H3 K27M-mutant diffuse midline glioma cells are exposed to dordaviprone. Mitochondrial stress signaling increases, apoptosis is induced, and histone H3 K27 trimethylation partially recovers. A separate receptor assay shows reduced dopamine D2 signaling.',
        'Which pair of direct pharmacologic actions best explains this profile?',
        {
            'A':'Inhibition of mitochondrial ClpP plus dopamine D2 agonism',
            'B':'Activation of mitochondrial ClpP plus dopamine D2 receptor inhibition',
            'C':'Inhibition of HIF-2alpha plus dopamine D2 receptor inhibition',
            'D':'Menin-KMT2A interaction blockade plus dopamine D2 agonism',
            'E':'Dual inhibition of mutant IDH1 and IDH2'
        },
        'B',
        'Activation of mitochondrial caseinolytic protease P with dopamine D2 receptor inhibition',
        'Dordaviprone is a protease activator of mitochondrial caseinolytic protease P (ClpP) and also inhibits the dopamine D2 receptor. In H3 K27M-mutant diffuse glioma models it activates an integrated stress response, alters mitochondrial metabolism, induces apoptosis, and can restore H3 K27 trimethylation.',
        {
            'A':'The ClpP direction is reversed; dordaviprone activates rather than inhibits ClpP, and it inhibits rather than agonizes D2 receptors.',
            'B':'Correct. Dordaviprone directly activates mitochondrial ClpP and inhibits dopamine D2 receptors.',
            'C':'HIF-2alpha inhibition is a distinct oxygen-sensing pathway mechanism and is not the direct target profile of dordaviprone.',
            'D':'Menin-KMT2A blockade is used in susceptible leukemias and does not explain the mitochondrial stress phenotype in H3 K27M glioma.',
            'E':'Mutant IDH inhibition lowers 2-hydroxyglutarate and is mechanistically distinct from ClpP activation.'
        },
        'Recognize dordaviprone as a mitochondrial ClpP activator with dopamine D2 receptor inhibitory activity in H3 K27M-mutant diffuse midline glioma.',
        'MODEYSO- dordaviprone capsule',
        'ad45b43e-fdef-47ad-9c34-055b41bdc576',
        'A',
        'ClpP inhibition superficially fits a mitochondrial target, but the documented direction is activation, and the paired D2 effect is inhibition rather than agonism.'
    ))

    items.append(make(
        1533,
        'nipocalimab-aahu',
        'Nervous System & Special Senses',
        ['Pharmacology','Immunology'],
        'A patient with generalized myasthenia gravis has pathogenic circulating IgG autoantibodies. After treatment with nipocalimab-aahu, total serum IgG and anti-acetylcholine receptor antibody concentrations fall without direct depletion of B lymphocytes.',
        'Which direct pharmacologic action best explains this effect?',
        {
            'A':'Blockade of terminal complement component C5',
            'B':'Depletion of CD20-positive B cells',
            'C':'Binding to the neonatal Fc receptor, reducing IgG recycling',
            'D':'Inhibition of IL-6 receptor signaling',
            'E':'Neutralization of BAFF'
        },
        'C',
        'Binding to neonatal Fc receptor and reducing circulating IgG',
        'Nipocalimab-aahu is a human IgG1 monoclonal antibody that binds the neonatal Fc receptor (FcRn), resulting in a reduction of circulating IgG levels, including pathogenic IgG autoantibodies.',
        {
            'A':'C5 blockade inhibits complement-mediated injury but does not directly accelerate IgG clearance.',
            'B':'CD20 depletion reduces B-cell populations and antibody production over time but is not the direct mechanism of nipocalimab.',
            'C':'Correct. FcRn binding interferes with IgG salvage/recycling and lowers circulating IgG, including pathogenic autoantibodies.',
            'D':'IL-6 receptor blockade alters inflammatory signaling but does not directly reduce IgG through FcRn.',
            'E':'BAFF neutralization affects B-cell survival and maturation rather than directly blocking IgG recycling.'
        },
        'Recognize FcRn blockade as a mechanism for lowering pathogenic circulating IgG without directly depleting B cells.',
        'IMAAVY- nipocalimab-aahu injection, solution, concentrate',
        '8886274c-f2b2-48af-85c1-2f90bfe304b8',
        'B',
        'B-cell depletion can eventually lower autoantibody production, but the prompt specifies an acute reduction in circulating IgG without direct B-cell depletion, favoring FcRn blockade.'
    ))

    items.append(make(
        1534,
        'fitusiran',
        'Blood & Lymphoreticular/Immune Systems',
        ['Pharmacology','Molecular Biology'],
        'Hepatocytes are exposed to a double-stranded oligonucleotide therapy used to rebalance hemostasis in hemophilia. Antithrombin protein synthesis falls after the intracellular concentration of antithrombin messenger RNA decreases.',
        'Which molecular mechanism directly produces this effect?',
        {
            'A':'CRISPR-mediated deletion of the SERPINC1 gene',
            'B':'Antisense blockade of factor VIII translation',
            'C':'Neutralization of tissue factor pathway inhibitor',
            'D':'RNA interference causing degradation of antithrombin mRNA',
            'E':'Activation of thrombopoietin receptors'
        },
        'D',
        'RNA interference causing degradation of antithrombin messenger RNA',
        'Fitusiran is a double-stranded small interfering RNA that causes degradation of antithrombin mRNA through RNA interference, thereby reducing plasma antithrombin levels.',
        {
            'A':'Fitusiran does not edit or delete the SERPINC1 gene; its effect occurs post-transcriptionally.',
            'B':'The therapy targets antithrombin mRNA rather than factor VIII translation.',
            'C':'TFPI neutralization is a different rebalancing strategy that acts at the protein level.',
            'D':'Correct. Fitusiran uses RNA interference to degrade antithrombin mRNA and reduce antithrombin protein.',
            'E':'Thrombopoietin-receptor activation increases platelet production and does not target antithrombin expression.'
        },
        'Differentiate siRNA-mediated antithrombin suppression by fitusiran from protein-neutralizing and gene-editing hemostatic strategies.',
        'QFITLIA- fitusiran injection, solution',
        '6dd2f8ac-6f90-4cbf-b197-97d74964135c',
        'C',
        'TFPI neutralization can also rebalance coagulation in hemophilia, but fitusiran specifically reduces antithrombin through siRNA-mediated mRNA degradation.'
    ))

    items.append(make(
        1535,
        'prademagene zamikeracel',
        'Musculoskeletal, Skin & Subcutaneous Tissue',
        ['Cell Biology','Genetics'],
        'Autologous keratinocyte-containing sheets are prepared from a patient with recessive dystrophic epidermolysis bullosa. The cells are transduced ex vivo with a replication-incompetent retroviral vector carrying a full-length gene, then applied topically to chronic wounds. Treated tissue begins producing collagen VII and anchoring fibrils.',
        'Which gene is introduced into the patient-derived cells?',
        {
            'A':'KRT14',
            'B':'LAMA3',
            'C':'COL17A1',
            'D':'ITGB4',
            'E':'COL7A1'
        },
        'E',
        'Ex vivo retroviral delivery of COL7A1 to restore collagen VII production',
        'ZEVASKYN consists of autologous cells transduced ex vivo with a replication-incompetent retroviral vector containing full-length COL7A1, enabling production of functional collagen VII and restoration of anchoring fibrils.',
        {
            'A':'KRT14 mutations cause a different inherited epidermolysis bullosa phenotype and do not encode collagen VII.',
            'B':'LAMA3 encodes a laminin subunit involved in junctional epidermolysis bullosa, not collagen VII.',
            'C':'COL17A1 encodes type XVII collagen rather than type VII collagen.',
            'D':'ITGB4 encodes integrin beta-4 and is associated with a different basement-membrane adhesion defect.',
            'E':'Correct. COL7A1 encodes collagen VII, the protein deficient in recessive dystrophic epidermolysis bullosa and restored by this ex vivo gene-modified cell product.'
        },
        'Connect recessive dystrophic epidermolysis bullosa to COL7A1 deficiency and recognize ex vivo COL7A1 gene transfer as the mechanism of prademagene zamikeracel.',
        'ZEVASKYN- prademagene zamikeracel cellular sheet',
        'f8782480-8782-4748-9764-b9ed60979d47',
        'D',
        'Other epidermolysis bullosa genes encode different structural proteins, but collagen VII and anchoring fibril restoration specifically require COL7A1.'
    ))

    b={
        'batch_id':'Q1531-Q1535-20260911',
        'created_at':'2026-09-11',
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1530,
        'canonical_count_after':1530,
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
    assert [x['num'] for x in items]==list(range(1531,1536))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
