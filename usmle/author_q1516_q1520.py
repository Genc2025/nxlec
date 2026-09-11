#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/04_q1516_q1520_author_20260911.json')
DB_BLOB='d1d532f97f9cb43b6b376916a0d41cada277e911'
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
        1516,
        'acoramidis',
        'Cardiovascular System',
        ['Pharmacology','Biochemistry'],
        'Purified transthyretin tetramers are incubated with acoramidis. The drug occupies thyroxine-binding sites, and dissociation of the tetramer into monomers decreases. Formation of downstream amyloidogenic species is reduced.',
        'Which direct pharmacologic action best explains these findings?',
        {
            'A':'Kinetic stabilization of the transthyretin tetramer',
            'B':'Proteolytic degradation of preformed transthyretin amyloid fibrils',
            'C':'Inhibition of hepatic transthyretin gene transcription',
            'D':'Agonism of nuclear thyroid hormone receptors',
            'E':'RNA interference targeting transthyretin messenger RNA'
        },
        'A',
        'TTR tetramer stabilization that slows rate-limiting dissociation into monomers',
        'Acoramidis is a selective transthyretin stabilizer. It binds TTR at thyroxine-binding sites and slows dissociation of the tetramer into monomers, the rate-limiting step in amyloidogenesis.',
        {
            'A':'Correct. Binding and stabilization of the TTR tetramer directly reduce its dissociation into amyloidogenic monomers.',
            'B':'The labeled mechanism is prevention of tetramer dissociation, not enzymatic clearance of existing amyloid fibrils.',
            'C':'Acoramidis does not act by suppressing TTR transcription.',
            'D':'Occupancy of TTR thyroxine-binding sites is not thyroid-hormone-receptor agonism.',
            'E':'RNA interference lowers TTR synthesis through mRNA silencing, a distinct mechanism from tetramer stabilization.'
        },
        'Recognize pharmacologic stabilization of the transthyretin tetramer as a strategy that reduces amyloidogenesis by slowing the rate-limiting dissociation step.',
        'ATTRUBY- acoramidis hydrochloride tablet, film coated',
        '913552ef-875d-4cb7-bf05-a7d20a394c38',
        'E',
        'TTR-targeted RNA interference can also reduce amyloid precursor availability, but the experiment directly demonstrates preserved tetrameric TTR through thyroxine-site binding rather than reduced TTR synthesis.'
    ))
    items.append(make(
        1517,
        'iptacopan',
        'Blood & Lymphoreticular/Immune Systems',
        ['Pharmacology','Immunology'],
        'Serum is exposed to iptacopan before activation of the alternative complement pathway. Cleavage of C3 and generation of downstream complement effectors decrease, while the drug is shown to bind a component required for the alternative-pathway C3 convertase.',
        'Which direct molecular target best explains this effect?',
        {
            'A':'Complement component C5',
            'B':'Complement factor B',
            'C':'Complement factor D',
            'D':'Complement component C1s',
            'E':'Complement component C3'
        },
        'B',
        'Factor B inhibition in the alternative complement pathway',
        'Iptacopan binds complement Factor B, regulating cleavage of C3, generation of downstream effectors, and amplification of the terminal complement pathway.',
        {
            'A':'C5 inhibition acts downstream and does not directly explain the stated binding to a component of the alternative-pathway C3 convertase.',
            'B':'Correct. Factor B is the labeled direct target of iptacopan and is required for alternative-pathway C3 convertase activity.',
            'C':'Factor D cleaves factor B but is not the direct labeled target of iptacopan.',
            'D':'C1s is part of the classical complement pathway rather than the alternative-pathway C3 convertase.',
            'E':'The drug regulates C3 cleavage indirectly through Factor B rather than by binding C3 itself.'
        },
        'Identify Factor B as the direct target of iptacopan and distinguish alternative-pathway inhibition from downstream terminal-complement blockade.',
        'FABHALTA- iptacopan capsule',
        'a76b5845-6e21-4d3b-ad07-cd8df1b60bee',
        'C',
        'Factor D inhibition is mechanistically adjacent because Factor D activates Factor B, but iptacopan is directly bound to Factor B in the labeled mechanism.'
    ))
    items.append(make(
        1518,
        'revumenib',
        'Blood & Lymphoreticular/Immune Systems',
        ['Pharmacology','Genetics'],
        'Leukemia cells harboring a KMT2A fusion are treated with revumenib. Expression of genes involved in the leukemogenic transcriptional program changes, differentiation markers increase, and proliferation falls without direct DNA damage.',
        'Which direct interaction is inhibited by this drug?',
        {
            'A':'BCL2 binding to proapoptotic BH3-only proteins',
            'B':'FLT3 autophosphorylation',
            'C':'Binding of menin to KMT2A and KMT2A fusion proteins',
            'D':'Mutant IDH2 production of 2-hydroxyglutarate',
            'E':'DNA topoisomerase II religation'
        },
        'C',
        'Menin inhibition that disrupts menin-KMT2A/KMT2A-fusion interactions',
        'Revumenib is a menin inhibitor that blocks the interaction of wild-type KMT2A and KMT2A fusion proteins with menin, thereby disrupting a leukemogenic transcriptional program.',
        {
            'A':'BCL2 inhibition promotes apoptosis through the intrinsic mitochondrial pathway but does not directly disrupt the menin-KMT2A transcriptional complex.',
            'B':'FLT3 kinase inhibition targets signaling from activated FLT3, a different AML mechanism.',
            'C':'Correct. Revumenib directly inhibits menin and blocks its interaction with KMT2A and KMT2A fusion proteins.',
            'D':'IDH2 inhibition lowers 2-hydroxyglutarate production and is mechanistically distinct from menin inhibition.',
            'E':'Topoisomerase II inhibition causes DNA strand damage rather than selective disruption of a leukemogenic protein-protein interaction.'
        },
        'Recognize menin-KMT2A interaction blockade as the direct mechanism of revumenib in susceptible acute leukemias.',
        'REVUFORJ- revumenib tablet, film coated',
        '6eb3cdbc-0e74-477d-82d6-3bb172d3f63f',
        'B',
        'FLT3 inhibition is a common targeted AML strategy, but the KMT2A-fusion context plus differentiation-associated transcriptional changes specifically support menin-KMT2A disruption.'
    ))
    items.append(make(
        1519,
        'nemolizumab-ilto',
        'Musculoskeletal, Skin & Subcutaneous Tissue',
        ['Pharmacology','Immunology'],
        'Human skin cells are exposed to IL-31, producing a pruritus-associated inflammatory response. Addition of nemolizumab-ilto suppresses IL-31-induced cytokine and chemokine release without neutralizing circulating IgE.',
        'Which direct receptor interaction best explains this effect?',
        {
            'A':'Blockade of the IL-4 receptor alpha chain',
            'B':'Neutralization of soluble IL-13',
            'C':'Inhibition of JAK1 catalytic activity',
            'D':'Selective binding to IL-31 receptor alpha',
            'E':'Binding to the Fc region of IgE'
        },
        'D',
        'Selective IL-31 receptor alpha blockade',
        'Nemolizumab-ilto is a humanized monoclonal antibody that inhibits IL-31 signaling by selectively binding IL-31 receptor alpha, thereby suppressing IL-31-induced inflammatory responses.',
        {
            'A':'IL-4 receptor alpha blockade inhibits IL-4/IL-13 signaling but does not directly block the IL-31 receptor.',
            'B':'IL-13 neutralization targets a different cytokine pathway.',
            'C':'JAK1 inhibition is an intracellular kinase mechanism rather than selective antibody binding to IL-31 receptor alpha.',
            'D':'Correct. Nemolizumab-ilto selectively binds IL-31 receptor alpha and inhibits IL-31 signaling.',
            'E':'IgE binding is the mechanism of anti-IgE therapy and is explicitly excluded by the experiment.'
        },
        'Identify IL-31 receptor alpha as the direct target of nemolizumab-ilto and distinguish this mechanism from other antipruritic cytokine and IgE pathways.',
        'NEMLUVIO- nemolizumab-ilto injection, powder, lyophilized, for solution',
        'e9229ef1-ac60-4c24-afb6-009d3c781687',
        'C',
        'JAK1 inhibition can reduce downstream signaling from multiple cytokine receptors, but nemolizumab-ilto is an extracellular monoclonal antibody with selective IL-31 receptor-alpha binding.'
    ))
    items.append(make(
        1520,
        'ensartinib',
        'Respiratory System',
        ['Pharmacology','Cell Biology'],
        'A non-small cell lung cancer cell line contains an ALK fusion but no activating EGFR, MET, or ROS1 alteration. After ensartinib exposure, phosphorylation of ALK decreases, followed by reduced phosphorylation of AKT, ERK, and S6 and reduced cellular proliferation.',
        'Which direct pharmacologic action best explains this pattern?',
        {
            'A':'Irreversible inhibition of mutant EGFR',
            'B':'Selective inhibition of MET without ALK inhibition',
            'C':'Direct inhibition of KRAS-GTP loading',
            'D':'Selective inhibition of ROS1 without ALK inhibition',
            'E':'Inhibition of anaplastic lymphoma kinase activity'
        },
        'E',
        'ALK kinase inhibition with reduced downstream AKT/ERK/S6 signaling',
        'Ensartinib is a kinase inhibitor of anaplastic lymphoma kinase. In ALK-driven cells it inhibits ALK phosphorylation and downstream AKT, ERK, and S6 signaling, reducing proliferation.',
        {
            'A':'The cell line lacks an activating EGFR alteration, and the observed direct fall in ALK phosphorylation points away from EGFR inhibition.',
            'B':'Although ensartinib can inhibit MET in vitro, the labeled principal target and the stipulated driver in this experiment are ALK.',
            'C':'KRAS-GTP loading is not the documented direct target of ensartinib.',
            'D':'Although ensartinib can inhibit ROS1 in vitro, the cell line lacks a ROS1 driver and directly shows suppression of phosphorylated ALK.',
            'E':'Correct. ALK kinase inhibition directly explains the fall in ALK phosphorylation and downstream AKT, ERK, and S6 signaling.'
        },
        'Link ALK kinase inhibition to decreased ALK phosphorylation and suppression of downstream proliferative signaling in ALK-fusion-positive lung cancer.',
        'ENSACOVE- ensartinib capsule',
        '1e1b2f79-678a-472a-b924-66909c8a4b2e',
        'D',
        'ROS1 is an in-vitro ensartinib target, but the absence of a ROS1 alteration and direct suppression of ALK phosphorylation in an ALK-fusion cell line make ALK inhibition the single best answer.'
    ))
    b={
        'batch_id':'Q1516-Q1520-20260911',
        'created_at':'2026-09-11',
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1515,
        'canonical_count_after':1515,
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
    assert [x['num'] for x in items]==list(range(1516,1521))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
