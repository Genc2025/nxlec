#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/06_q1526_q1530_author_20260911.json')
DB_BLOB='487f4756e6771b6472b96abb7a18402484334abd'
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
        1526,
        'xanomeline/trospium chloride',
        'Behavioral Health',
        ['Pharmacology','Neuroscience'],
        'A patient with schizophrenia receives a fixed-dose combination containing a centrally active muscarinic agonist and a quaternary ammonium antimuscarinic agent. The first component is intended to engage central muscarinic signaling, whereas the second predominantly antagonizes muscarinic receptors in peripheral tissues.',
        'Which pair of direct pharmacologic actions best describes this combination?',
        {
            'A':'Central M1/M4 muscarinic agonism plus predominantly peripheral muscarinic antagonism',
            'B':'Central D2 receptor antagonism plus peripheral beta-1 receptor blockade',
            'C':'Central NMDA receptor agonism plus peripheral nicotinic receptor antagonism',
            'D':'Central 5-HT2A agonism plus peripheral alpha-1 receptor blockade',
            'E':'Central M2 antagonism plus peripheral M1 agonism'
        },
        'A',
        'Central muscarinic M1/M4 agonism from xanomeline paired with predominantly peripheral muscarinic antagonism from trospium',
        'COBENFY combines xanomeline, whose efficacy is thought to involve agonist activity at central M1 and M4 muscarinic acetylcholine receptors, with trospium chloride, a muscarinic antagonist acting primarily in peripheral tissues.',
        {
            'A':'Correct. Xanomeline provides central muscarinic agonist activity with higher agonist activity at M1/M4, while trospium predominantly antagonizes peripheral muscarinic receptors.',
            'B':'D2 antagonism is a conventional antipsychotic mechanism but is not the direct target pair of this combination.',
            'C':'Neither NMDA agonism nor nicotinic antagonism is the labeled pharmacologic mechanism.',
            'D':'The combination is not based on 5-HT2A agonism or alpha-1 blockade.',
            'E':'The directions and receptor distribution are reversed relative to the documented actions of xanomeline and trospium.'
        },
        'Recognize the complementary central muscarinic agonist and predominantly peripheral antimuscarinic actions of xanomeline/trospium.',
        'COBENFY- xanomeline and trospium chloride capsule, coated pellets COBENFY- xanomeline and trospium chloride kit',
        '8f0e73bf-6025-44f6-ab64-0983322de0df',
        'B',
        'D2 antagonism is a familiar schizophrenia mechanism, but the fixed-dose drug pair is defined by muscarinic pharmacology rather than dopamine-receptor blockade.'
    ))

    items.append(make(
        1527,
        'zanidatamab-hrii',
        'Gastrointestinal System',
        ['Pharmacology','Immunology'],
        'HER2-overexpressing tumor cells are exposed to zanidatamab-hrii. The antibody simultaneously engages two nonoverlapping extracellular regions on the same receptor, promotes receptor clustering and internalization, and can trigger complement-dependent and antibody-dependent cellular cytotoxicity.',
        'Which direct binding pattern best explains these findings?',
        {
            'A':'Binding to HER2 extracellular domain 4 only',
            'B':'Bispecific binding to HER2 extracellular domains 2 and 4',
            'C':'Binding to HER3 and EGFR simultaneously',
            'D':'Binding to PD-L1 and HER2 simultaneously',
            'E':'Binding to soluble VEGF-A and membrane HER2'
        },
        'B',
        'Dual-epitope HER2 binding at extracellular domains 2 and 4',
        'Zanidatamab-hrii is a bispecific HER2-directed antibody that binds extracellular domains 2 and 4 on HER2. Binding promotes receptor clustering/internalization and can induce CDC, ADCC, and ADCP.',
        {
            'A':'Single-domain HER2 binding does not match the documented dual-epitope ECD2/ECD4 interaction.',
            'B':'Correct. Zanidatamab-hrii binds HER2 at both ECD2 and ECD4, accounting for receptor clustering and downstream immune effector mechanisms.',
            'C':'HER3/EGFR dual binding describes a different receptor-targeting strategy.',
            'D':'PD-L1 is not one of the direct binding targets of zanidatamab-hrii.',
            'E':'VEGF-A neutralization is an antiangiogenic mechanism and is not part of this antibody’s labeled target profile.'
        },
        'Identify zanidatamab-hrii as a dual-epitope HER2 antibody binding ECD2 and ECD4 rather than a conventional single-epitope HER2 antibody.',
        'ZIIHERA- zanidatamab-hrii injection, powder, lyophilized, for solution',
        'ae5d9425-fae5-4541-a158-150998343348',
        'A',
        'HER2 ECD4-only binding is plausible because other HER2 antibodies bind that region, but simultaneous ECD2 and ECD4 engagement is the distinguishing zanidatamab feature.'
    ))

    items.append(make(
        1528,
        'vorasidenib',
        'Nervous System & Special Senses',
        ['Pharmacology','Biochemistry'],
        'Glioma cells carrying an IDH1 R132 mutation are exposed to vorasidenib. Intracellular 2-hydroxyglutarate falls and markers of cellular differentiation partially recover. The same drug can inhibit susceptible mutant IDH2 proteins.',
        'Which direct molecular action best explains these findings?',
        {
            'A':'Inhibition of mutant BRAF kinase',
            'B':'Inhibition of histone deacetylases',
            'C':'Inhibition of IDH1 and IDH2 enzymes',
            'D':'Inhibition of DNA methyltransferase 1',
            'E':'Inhibition of mTOR complex 1'
        },
        'C',
        'Dual IDH1/IDH2 inhibition that lowers 2-hydroxyglutarate production',
        'Vorasidenib is a small-molecule inhibitor of IDH1 and IDH2. In models expressing susceptible mutant IDH1 or IDH2 proteins, it decreases production of the oncometabolite 2-hydroxyglutarate and can partially restore cellular differentiation.',
        {
            'A':'BRAF inhibition targets MAPK signaling and does not directly lower the IDH-derived oncometabolite 2-hydroxyglutarate.',
            'B':'Histone deacetylase inhibition alters chromatin acetylation but is not the direct target of vorasidenib.',
            'C':'Correct. Vorasidenib directly inhibits IDH1 and IDH2, reducing 2-hydroxyglutarate production in susceptible mutant glioma cells.',
            'D':'DNA methyltransferase inhibition can alter differentiation state but does not directly inhibit mutant IDH enzymes.',
            'E':'mTORC1 inhibition suppresses growth signaling but does not explain selective reduction of 2-hydroxyglutarate.'
        },
        'Connect mutant IDH1/IDH2 activity with 2-hydroxyglutarate production and recognize dual IDH1/IDH2 inhibition as the direct mechanism of vorasidenib.',
        'VORANIGO- vorasidenib tablet, film coated',
        '31405fee-55b7-4857-987e-2724ee76be84',
        'D',
        'Epigenetic therapies can partially restore differentiation downstream of mutant IDH, but the direct fall in 2-hydroxyglutarate identifies inhibition of IDH1/IDH2 itself.'
    ))

    items.append(make(
        1529,
        'repotrectinib',
        'Respiratory System',
        ['Pharmacology','Cell Biology'],
        'A kinase inhibitor suppresses proliferation of cultured tumor cells driven by a ROS1 fusion and also inhibits cells driven by NTRK1, NTRK2, or NTRK3 fusions. The drug retains activity against several solvent-front resistance substitutions in these kinases.',
        'Which direct target profile best explains this activity?',
        {
            'A':'EGFR and HER2 inhibition',
            'B':'ALK and MET inhibition only',
            'C':'BRAF and MEK1/2 inhibition',
            'D':'ROS1 and TRKA/TRKB/TRKC inhibition',
            'E':'RET and VEGFR2 inhibition'
        },
        'D',
        'Inhibition of ROS1 and tropomyosin receptor kinases A, B, and C',
        'Repotrectinib directly inhibits ROS1 and the tropomyosin receptor tyrosine kinases TRKA, TRKB, and TRKC, including activity in models harboring multiple fusion and resistance variants.',
        {
            'A':'EGFR/HER2 inhibition would not explain activity across ROS1- and NTRK-fusion-driven models.',
            'B':'ALK/MET inhibition is a distinct kinase-target profile and omits the directly demonstrated TRK activity.',
            'C':'BRAF/MEK inhibition acts in the MAPK pathway downstream and does not match the fusion-specific kinase profile.',
            'D':'Correct. Repotrectinib directly targets ROS1 and TRKA/B/C, fitting both ROS1- and NTRK-fusion models.',
            'E':'RET/VEGFR2 inhibition describes a different multikinase profile.'
        },
        'Recognize repotrectinib as a ROS1 and pan-TRK inhibitor and distinguish it from other kinase-inhibitor target profiles.',
        'AUGTYRO- repotrectinib capsule',
        'fb526827-40ba-4462-94cf-179ae3b0cb8a',
        'B',
        'ALK/MET inhibition can be relevant in lung cancer, but simultaneous activity in ROS1- and NTRK-driven systems directly identifies the ROS1/pan-TRK profile.'
    ))

    items.append(make(
        1530,
        'mirdametinib',
        'Nervous System & Special Senses',
        ['Pharmacology','Cell Biology'],
        'Cells from an NF1-associated plexiform neurofibroma show constitutive RAS-pathway signaling. After exposure to mirdametinib, phosphorylation of ERK decreases even though RAS activation itself is not directly inhibited.',
        'Which direct molecular action best explains this finding?',
        {
            'A':'Inhibition of RAF dimerization',
            'B':'Inhibition of ERK1/2 catalytic activity',
            'C':'Inhibition of mutant RAS-GTP loading',
            'D':'Inhibition of PI3K alpha',
            'E':'Inhibition of MEK1 and MEK2'
        },
        'E',
        'MEK1/2 inhibition causing reduced downstream ERK phosphorylation',
        'Mirdametinib inhibits MEK1 and MEK2, upstream regulators of ERK. In vitro it inhibits MEK1/2 kinase activity and reduces downstream ERK phosphorylation.',
        {
            'A':'RAF lies upstream of MEK, but mirdametinib is not labeled as a RAF-dimer inhibitor.',
            'B':'ERK phosphorylation falls because the upstream MEK kinases are inhibited; ERK itself is not the direct labeled target.',
            'C':'NF1 loss increases RAS signaling, but mirdametinib does not directly block RAS nucleotide loading.',
            'D':'PI3K-alpha inhibition targets a parallel signaling axis and does not directly explain selective suppression of MEK-dependent ERK phosphorylation.',
            'E':'Correct. Direct MEK1/2 inhibition decreases phosphorylation of downstream ERK.'
        },
        'Localize mirdametinib within the RAS-RAF-MEK-ERK pathway as a direct MEK1/2 inhibitor.',
        'GOMEKLI- mirdametinib capsule GOMEKLI- mirdametinib tablet, for suspension',
        '4c41bf90-5fa7-4935-a95c-e047ea6bbf8e',
        'B',
        'Direct ERK inhibition can also reduce ERK-pathway output, but the labeled target of mirdametinib is MEK1/2, which is upstream of ERK phosphorylation.'
    ))

    b={
        'batch_id':'Q1526-Q1530-20260911',
        'created_at':'2026-09-11',
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1525,
        'canonical_count_after':1525,
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
    assert [x['num'] for x in items]==list(range(1526,1531))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
