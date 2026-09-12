#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/10_q1546_q1550_author_20260912.json')
DB_BLOB='673f63f6945dde4268efe347d7ad3e9b1977c3b5'
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
        1546,'suzetrigine','Nervous System & Special Senses',['Pharmacology','Neurophysiology'],
        'A dorsal-root-ganglion neuron is exposed to suzetrigine. Propagation of nociceptive action potentials decreases, while voltage-gated sodium currents in cardiac and central neurons are relatively preserved.',
        'Which ion-channel subtype is most directly inhibited?',
        {'A':'NaV1.8','B':'NaV1.5','C':'NaV1.2','D':'CaV2.2','E':'HCN4'},
        'A','Selective blockade of the NaV1.8 voltage-gated sodium channel in peripheral sensory neurons',
        'Suzetrigine selectively blocks NaV1.8 voltage-gated sodium channels. NaV1.8 is expressed in peripheral sensory neurons, including dorsal root ganglion neurons, where it contributes to propagation of pain-related action potentials.',
        {'A':'Correct. Suzetrigine selectively inhibits NaV1.8 channels in peripheral sensory neurons.','B':'NaV1.5 is the predominant cardiac sodium-channel isoform and is not the selective target of suzetrigine.','C':'NaV1.2 is primarily a central neuronal sodium-channel isoform and is not the labeled selective target.','D':'CaV2.2 is a voltage-gated calcium channel involved in neurotransmitter release, not the direct target of suzetrigine.','E':'HCN4 contributes to cardiac pacemaker current and does not explain the selective peripheral analgesic mechanism.'},
        'Distinguish selective peripheral NaV1.8 blockade from cardiac, central-neuronal, calcium-channel, and pacemaker-channel mechanisms.',
        'JOURNAVX- suzetrigine tablet, film coated','f0976da4-1d20-4517-945c-b60ed2f41c12','B',
        'NaV1.5 is a sodium channel and therefore superficially plausible, but the dorsal-root-ganglion localization and relative preservation of cardiac sodium current identify NaV1.8.'
    ))

    items.append(make(
        1547,'acoramidis','Cardiovascular System',['Pharmacology','Biochemistry'],
        'A patient with transthyretin amyloid cardiomyopathy receives acoramidis. In vitro studies show increased kinetic stability of circulating transthyretin without decreasing hepatic synthesis of the protein.',
        'Which molecular event is most directly slowed by this drug?',
        {'A':'Proteasomal degradation of transthyretin monomers','B':'Dissociation of the transthyretin tetramer into monomers','C':'Translation of transthyretin mRNA','D':'Endocytosis of transthyretin by hepatocytes','E':'Cleavage of transthyretin by lysosomal proteases'},
        'B','Slowing dissociation of the transthyretin tetramer, the rate-limiting step in amyloidogenesis',
        'Acoramidis is a selective transthyretin stabilizer. It binds transthyretin at thyroxine-binding sites and slows dissociation of the native tetramer into monomers, which is the rate-limiting step in transthyretin amyloid formation.',
        {'A':'Acoramidis stabilizes the native tetramer rather than accelerating proteasomal degradation of monomers.','B':'Correct. By binding TTR at thyroxine-binding sites, acoramidis slows tetramer dissociation into amyloidogenic monomers.','C':'The drug does not reduce hepatic TTR synthesis or directly inhibit translation.','D':'Hepatocyte endocytosis is not the molecular step targeted by acoramidis.','E':'Lysosomal proteolysis is not the rate-limiting amyloidogenic step stabilized by this drug.'},
        'Recognize transthyretin tetramer dissociation as the rate-limiting amyloidogenic step targeted by TTR stabilizers.',
        'ATTRUBY- acoramidis hydrochloride tablet, film coated','913552ef-875d-4cb7-bf05-a7d20a394c38','C',
        'Inhibition of TTR synthesis is a valid therapeutic strategy for transthyretin amyloidosis, but the vignette explicitly shows preserved synthesis and kinetic stabilization of circulating tetramer.'
    ))

    items.append(make(
        1548,'revumenib','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Molecular Biology'],
        'Leukemia cells harboring a KMT2A rearrangement are exposed to revumenib. Expression of leukemogenic transcriptional programs falls and markers of cellular differentiation increase.',
        'Which protein-protein interaction is directly disrupted?',
        {'A':'BCL2 with BAX','B':'FLT3 with its ligand','C':'Menin with KMT2A/KMT2A-fusion proteins','D':'PML with RAR-alpha','E':'JAK2 with STAT5'},
        'C','Disruption of the menin-KMT2A interaction that sustains a leukemogenic transcriptional program',
        'Revumenib is a menin inhibitor. It blocks interaction of menin with wild-type KMT2A and KMT2A fusion proteins, thereby altering transcriptional programs that maintain susceptible acute leukemias and promoting differentiation.',
        {'A':'BCL2-BAX interactions regulate mitochondrial apoptosis but are not the direct target of revumenib.','B':'FLT3 signaling can drive acute leukemia, but revumenib does not act by blocking FLT3-ligand binding.','C':'Correct. Revumenib directly inhibits the menin-KMT2A/KMT2A-fusion interaction.','D':'PML-RAR-alpha is the characteristic fusion of acute promyelocytic leukemia and is not the target described here.','E':'JAK2-STAT5 signaling is a distinct kinase pathway and is not the direct molecular interaction blocked by revumenib.'},
        'Link menin inhibition to disruption of KMT2A-dependent leukemogenic transcription and restoration of differentiation.',
        'REVUFORJ- revumenib tablet, film coated','6eb3cdbc-0e74-477d-82d6-3bb172d3f63f','A',
        'BCL2 inhibition can also trigger antileukemic effects, but the KMT2A rearrangement and differentiation response specifically identify menin-KMT2A disruption.'
    ))

    items.append(make(
        1549,'delgocitinib','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Immunology'],
        'Keratinocytes from chronic hand eczema are exposed to delgocitinib. Cytokine receptor signaling that normally recruits STAT proteins is broadly reduced across pathways that use JAK1, JAK2, JAK3, and TYK2.',
        'Which downstream event is most directly reduced by this drug?',
        {'A':'RAS-mediated activation of RAF','B':'PLC-gamma-mediated generation of IP3','C':'NF-kappaB release after I-kappaB degradation','D':'Phosphorylation and nuclear translocation of STAT proteins','E':'SMAD2/3 nuclear translocation after TGF-beta receptor activation'},
        'D','Reduced JAK-dependent STAT activation and nuclear translocation',
        'Delgocitinib inhibits JAK1, JAK2, JAK3, and TYK2. JAK activation normally promotes phosphorylation of STAT proteins, followed by STAT dimerization and nuclear localization to regulate cytokine-responsive gene expression.',
        {'A':'RAS-RAF signaling is primarily linked to receptor tyrosine kinases rather than direct JAK inhibition.','B':'PLC-gamma/IP3 signaling is a separate receptor-proximal pathway and is not the principal downstream event of JAK blockade.','C':'NF-kappaB activation is not the direct canonical downstream consequence of JAK1/2/3/TYK2 activity.','D':'Correct. Broad JAK inhibition reduces STAT phosphorylation and subsequent nuclear translocation.','E':'SMAD2/3 signaling is downstream of TGF-beta receptors rather than JAK-family kinases.'},
        'Connect pan-JAK inhibition with impaired STAT phosphorylation and nuclear translocation downstream of cytokine receptors.',
        'ANZUPGO- delgocitinib cream','a59bf36e-6f04-4b47-b385-8040c95f040c','E',
        'SMAD nuclear translocation is another cytokine-related transcriptional mechanism, but TGF-beta receptors signal through receptor serine/threonine kinases, not the JAK-STAT pathway specified in the stem.'
    ))

    items.append(make(
        1550,'zanidatamab-hrii','Multisystem Processes & Disorders',['Pharmacology','Immunology'],
        'HER2-overexpressing tumor cells are treated with zanidatamab-hrii. The antibody simultaneously occupies two extracellular regions on HER2, surface HER2 density falls, and immune-effector-mediated tumor-cell killing increases.',
        'Which direct action best explains the initial receptor-level effect?',
        {'A':'Covalent inhibition of the intracellular HER2 kinase domain','B':'Blockade of HER3 ligand binding without HER2 engagement','C':'Degradation of HER2 mRNA by RNA interference','D':'Binding of HER2 to a soluble decoy receptor','E':'Bispecific binding to two extracellular HER2 sites followed by receptor internalization'},
        'E','Dual-site extracellular HER2 binding that promotes receptor internalization and reduced surface HER2',
        'Zanidatamab-hrii is a bispecific HER2-directed antibody that binds two extracellular sites on HER2. This binding promotes internalization and reduces HER2 on the tumor-cell surface; the antibody also mediates immune-effector mechanisms including CDC, ADCC, and ADCP.',
        {'A':'An intracellular covalent kinase inhibitor is a small-molecule mechanism and does not explain dual extracellular antibody binding.','B':'Zanidatamab-hrii directly binds HER2 rather than acting only at HER3.','C':'The drug is an antibody and does not reduce HER2 expression through RNA interference.','D':'A soluble decoy-receptor mechanism is not the documented action of zanidatamab-hrii.','E':'Correct. Zanidatamab-hrii binds two extracellular HER2 sites, causing receptor internalization and decreased surface HER2.'},
        'Differentiate dual-epitope HER2 antibody binding with receptor internalization from intracellular kinase inhibition, HER3 blockade, RNA interference, and decoy-receptor mechanisms.',
        'ZIIHERA- zanidatamab-hrii injection, powder, lyophilized, for solution','ae5d9425-fae5-4541-a158-150998343348','A',
        'A HER2 kinase inhibitor also reduces HER2 signaling, but an antibody occupying two extracellular HER2 sites with reduced surface receptor density identifies zanidatamab-hrii-mediated internalization.'
    ))

    b={
        'batch_id':'Q1546-Q1550-20260912',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1545,
        'canonical_count_after':1545,
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
    assert [x['num'] for x in items]==list(range(1546,1551))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
