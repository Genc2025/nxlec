#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/14_q1566_q1570_author_20260913.json')
DB_BLOB='f988cd9d7f04439435cb71ef7289c6269900f020'
TODAY='2026-09-13'

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
    return x

def main():
    items=[]

    items.append(make(
        1566,'taletrectinib','Respiratory System',['Pharmacology','Molecular Biology'],
        'A patient with metastatic non-small cell lung cancer has a ROS1 fusion and later develops a ROS1 solvent-front resistance mutation. Tumor cells remain sensitive to taletrectinib, with decreased phosphorylation of downstream survival pathways.',
        'Which molecular target is most directly inhibited?',
        {'A':'ROS1 tyrosine kinase','B':'BRAF serine/threonine kinase','C':'MET receptor tyrosine kinase','D':'ALK tyrosine kinase','E':'KRAS GTPase'},
        'A','Direct inhibition of ROS1 tyrosine kinase, including resistance-mutant ROS1',
        'Taletrectinib inhibits ROS1 tyrosine kinase, including clinically relevant resistance mutations. ROS1 fusion proteins can constitutively activate downstream proliferative signaling; ROS1 inhibition suppresses growth of ROS1-driven tumor cells.',
        {'A':'Correct. Taletrectinib directly inhibits ROS1 tyrosine kinase, including resistance-mutant forms.','B':'BRAF is a downstream MAPK-pathway kinase and is not the direct target.','C':'MET is targeted by other agents but is not the labeled primary target of taletrectinib.','D':'ALK rearrangements can also drive NSCLC, but this tumor is ROS1-driven.','E':'KRAS is a small GTPase and is not directly inhibited by taletrectinib.'},
        'Identify ROS1 as the direct oncogenic target of taletrectinib in ROS1-positive NSCLC, including disease with resistance mutations.',
        'IBTROZI- taletrectinib capsule','51ac8e52-3269-4102-8dc8-dba22d82128c','C',
        'ALK and ROS1 rearrangements can produce similar NSCLC phenotypes, but the documented fusion and resistance mutation identify ROS1 as the direct target.'
    ))

    items.append(make(
        1567,'inclisiran','Cardiovascular System',['Pharmacology','Molecular Biology'],
        'A hepatocyte is exposed to inclisiran. After uptake through a liver-targeting carbohydrate conjugate, the drug enters the RNA interference pathway and lowers synthesis of a secreted protein that normally reduces LDL-receptor recycling.',
        'Which cellular change most directly follows?',
        {'A':'Decreased LDL-receptor density on hepatocyte surfaces','B':'Increased recycling of LDL receptors to the hepatocyte surface','C':'Increased HMG-CoA reductase transcription','D':'Reduced endocytosis of circulating LDL particles','E':'Increased secretion of apolipoprotein B'},
        'B','Increased hepatocyte-surface LDL-receptor recycling after PCSK9 mRNA degradation',
        'Inclisiran is a GalNAc-conjugated small interfering RNA that is taken up by hepatocytes and directs catalytic degradation of PCSK9 mRNA. Lower PCSK9 production increases LDL-receptor recycling and surface expression, which enhances LDL uptake from plasma.',
        {'A':'PCSK9 reduction increases rather than decreases hepatocyte-surface LDL receptors.','B':'Correct. Reduced PCSK9 allows more LDL receptors to recycle to the cell surface instead of being degraded.','C':'Inclisiran does not lower LDL cholesterol by increasing HMG-CoA reductase expression.','D':'More surface LDL receptors increase LDL uptake rather than reducing endocytosis.','E':'ApoB secretion is not the direct downstream effect of PCSK9 mRNA silencing.'},
        'Connect hepatocyte-targeted PCSK9 siRNA therapy with increased LDL-receptor recycling and increased plasma LDL clearance.',
        'LEQVIO- inclisiran injection, solution','6fc0afca-4513-4c35-b594-6544aee29a44','C',
        'Increased HMG-CoA reductase transcription would oppose LDL lowering and is not the mechanism of inclisiran; PCSK9 mRNA silencing instead increases LDL-receptor recycling.'
    ))

    items.append(make(
        1568,'migalastat','Multisystem Processes & Disorders',['Pharmacology','Cell Biology'],
        'A patient with Fabry disease has an amenable GLA missense variant that produces alpha-galactosidase A with residual catalytic activity but poor folding and endoplasmic-reticulum retention. Migalastat increases lysosomal enzyme activity without supplying exogenous enzyme.',
        'Which mechanism best explains this effect?',
        {'A':'Permanent covalent activation of alpha-galactosidase A','B':'Increased transcription of the GLA gene','C':'Reversible active-site binding that stabilizes folding and permits lysosomal trafficking','D':'Inhibition of lysosomal proteases that degrade alpha-galactosidase A','E':'Insertion of a normal GLA cDNA into hematopoietic stem cells'},
        'C','Pharmacological chaperoning of amenable mutant alpha-galactosidase A',
        'Migalastat reversibly binds the active site of certain amenable mutant alpha-galactosidase A proteins and stabilizes their folding in the endoplasmic reticulum. This allows trafficking to lysosomes, where the lower pH and high substrate concentrations favor dissociation of migalastat and restoration of enzyme activity.',
        {'A':'Migalastat does not permanently activate or covalently modify the enzyme.','B':'The drug does not work primarily by increasing GLA transcription.','C':'Correct. Reversible active-site binding stabilizes amenable mutant enzyme and permits lysosomal trafficking.','D':'Lysosomal protease inhibition is not the labeled mechanism.','E':'Migalastat is a small-molecule pharmacological chaperone, not a gene therapy.'},
        'Recognize pharmacological chaperoning as stabilization of an amenable misfolded enzyme to restore intracellular trafficking and function.',
        'GALAFOLD- migalastat hydrochloride capsule','66dbd928-0f1c-48b1-a832-54e4abd9f1db','D',
        'The apparent paradox is that migalastat binds the active site, but the binding is reversible and primarily stabilizes folding before the drug dissociates in the lysosome.'
    ))

    items.append(make(
        1569,'avacopan','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'Neutrophils from a patient with ANCA-associated vasculitis are exposed to C5a in the presence of avacopan. C5a remains detectable in the medium, but upregulation of CD11b and chemotactic migration are markedly reduced.',
        'Which step is most directly blocked?',
        {'A':'Proteolytic cleavage of C5 into C5a and C5b','B':'Formation of C3 convertase','C':'Assembly of the membrane attack complex','D':'Binding of C5a to its neutrophil receptor','E':'Classical-pathway activation by C1q'},
        'D','Antagonism of the C5a receptor on neutrophils',
        'Avacopan is a complement C5a receptor antagonist. It blocks interaction of the anaphylatoxin C5a with C5aR, thereby reducing C5a-mediated neutrophil activation and migration without directly preventing generation of C5a itself.',
        {'A':'C5 cleavage can still occur because avacopan blocks the receptor rather than complement protein C5.','B':'C3-convertase formation is upstream and is not directly inhibited by avacopan.','C':'MAC formation is a downstream terminal-complement event and is not the direct receptor-level target.','D':'Correct. Avacopan directly antagonizes C5aR and blocks C5a-driven neutrophil activation.','E':'C1q-mediated classical-pathway initiation is not the direct target of avacopan.'},
        'Differentiate C5a-receptor antagonism from upstream complement blockade and direct C5 inhibition.',
        'TAVNEOS- avacopan capsule','c93cbc0b-29a3-46a5-9c85-41815ea5cf4a','C',
        'A C5 inhibitor would reduce generation of C5a itself; persistence of C5a with loss of neutrophil response specifically indicates C5a-receptor antagonism.'
    ))

    items.append(make(
        1570,'belzutifan','Renal & Urinary System',['Pharmacology','Molecular Biology'],
        'Renal tumor cells lacking functional VHL protein accumulate HIF-2alpha and express genes that promote angiogenesis and tumor growth. Belzutifan reduces transcription of these genes without restoring VHL function.',
        'Which molecular interaction is most directly disrupted?',
        {'A':'HIF-1alpha binding to prolyl hydroxylase','B':'VHL binding to ubiquitin ligase components','C':'VEGF binding to VEGFR2','D':'HIF-2alpha binding to DNA at hypoxia-response elements','E':'HIF-2alpha binding to HIF-1beta'},
        'E','Blockade of HIF-2alpha heterodimerization with HIF-1beta',
        'Belzutifan binds HIF-2alpha and blocks its interaction with HIF-1beta. In VHL-deficient cells, HIF-2alpha is stabilized and would otherwise form a transcriptionally active heterodimer that increases expression of genes involved in angiogenesis, proliferation, and tumor growth.',
        {'A':'Prolyl hydroxylation regulates HIF stability upstream but is not the direct interaction blocked by belzutifan.','B':'Belzutifan does not restore VHL-E3-ligase function.','C':'VEGF signaling is downstream of HIF activity; belzutifan acts upstream at HIF-2alpha.','D':'The direct labeled mechanism is inhibition of HIF-2alpha/HIF-1beta complex formation rather than direct blockade of DNA binding.','E':'Correct. Belzutifan prevents HIF-2alpha from heterodimerizing with HIF-1beta and thereby reduces HIF-2alpha-dependent transcription.'},
        'Link VHL loss to HIF-2alpha stabilization and recognize HIF-2alpha/HIF-1beta heterodimerization as the direct target of belzutifan.',
        'WELIREG- belzutifan tablet, film coated','13e15ee0-d679-4fa9-9430-e2e2170474da','A',
        'VEGF blockade could also reduce angiogenic signaling, but belzutifan acts one level upstream by preventing formation of the HIF-2alpha/HIF-1beta transcription complex.'
    ))

    b={
        'batch_id':'Q1566-Q1570-20260913',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1565,
        'canonical_count_after':1565,
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
    assert [x['num'] for x in items]==list(range(1566,1571))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
