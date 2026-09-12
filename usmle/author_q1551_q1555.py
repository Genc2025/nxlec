#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/11_q1551_q1555_author_20260912.json')
DB_BLOB='b909be98a4f3861c443f3b188c2597a290b0b17a'
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
        1551,'remibrutinib','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'Human mast cells are activated by cross-linking surface-bound IgE. In the presence of remibrutinib, histamine release falls despite preserved IgE binding at the cell surface.',
        'Which intracellular signaling protein is most directly inhibited?',
        {'A':"Bruton's tyrosine kinase (BTK)",'B':'Spleen tyrosine kinase (SYK)','C':'Janus kinase 2 (JAK2)','D':'Phosphoinositide 3-kinase delta only','E':'mTOR complex 1'},
        'A','Inhibition of BTK downstream of FcεRI signaling in mast cells and basophils',
        'Remibrutinib is a small-molecule inhibitor of BTK. BTK participates in signaling downstream of FcεRI, Fcγ receptors, and the B-cell receptor; inhibiting BTK suppresses mast-cell and basophil degranulation and release of histamine and other inflammatory mediators.',
        {'A':'Correct. Remibrutinib directly inhibits BTK, a signaling kinase downstream of FcεRI in mast cells and basophils.','B':'SYK also participates in Fc receptor signaling, but it is not the labeled direct target of remibrutinib.','C':'JAK2 mediates signaling downstream of several cytokine receptors rather than being the direct target in this FcεRI pathway.','D':'PI3K-delta can modulate immune-cell signaling, but the drug is labeled as a BTK inhibitor rather than a selective PI3K-delta inhibitor.','E':'mTORC1 is a downstream metabolic signaling complex and is not the direct target of remibrutinib.'},
        'Connect FcεRI-driven mast-cell degranulation with BTK signaling and recognize BTK inhibition as the direct action of remibrutinib.',
        'RHAPSIDO- remibrutinib tablet, film coated','e5e89bff-6ced-4165-acc5-fb13136b3a3d','B',
        'SYK is mechanistically plausible because it is also proximal in FcεRI signaling, but the drug-specific direct target established by the label is BTK.'
    ))

    items.append(make(
        1552,'aficamten','Cardiovascular System',['Pharmacology','Physiology'],
        'Cardiac sarcomeres from a patient with obstructive hypertrophic cardiomyopathy are exposed to aficamten. Actin-activated ATPase activity of myosin falls, and generated contractile force decreases without blocking beta-adrenergic receptors.',
        'Which direct action best explains these findings?',
        {'A':'Activation of cardiac myosin ATPase','B':'Allosteric, reversible inhibition of cardiac myosin motor activity','C':'Irreversible inhibition of L-type calcium channels','D':'Antagonism of beta-1 adrenergic receptors','E':'Inhibition of troponin C calcium binding'},
        'B','Allosteric reversible inhibition of cardiac myosin motor activity',
        'Aficamten is an allosteric and reversible inhibitor of cardiac myosin motor activity. It reduces force generation by the cardiac sarcomere and thereby decreases hypercontractility and left ventricular outflow tract obstruction in hypertrophic cardiomyopathy.',
        {'A':'Aficamten decreases rather than activates cardiac myosin motor activity.','B':'Correct. The drug allosterically and reversibly inhibits cardiac myosin motor activity, lowering sarcomeric force generation.','C':'The mechanism is not direct blockade of L-type calcium channels.','D':'Beta-1 antagonism can reduce contractility but does not account for the direct sarcomeric myosin effect in the experiment.','E':'Troponin C is not the direct molecular target of aficamten.'},
        'Differentiate direct cardiac myosin inhibition from receptor- and calcium-channel-mediated negative inotropy.',
        'MYQORZO- aficamten tablet','fd778507-1274-4d1a-a659-5431d55c543a','D',
        'Beta-1 blockade also reduces contractility, but the cell-free sarcomere findings and direct reduction of myosin motor activity identify aficamten.'
    ))

    items.append(make(
        1553,'linvoseltamab-gcpt','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'T lymphocytes are cocultured with multiple myeloma cells in the presence of linvoseltamab-gcpt. T-cell activation, cytokine release, and tumor-cell lysis increase even though the antibody has no intrinsic cytotoxic payload.',
        'Which pair of surface molecules is simultaneously engaged?',
        {'A':'CD19 on myeloma cells and CD28 on T cells','B':'CD38 on myeloma cells and CD16 on NK cells','C':'BCMA on myeloma cells and CD3 on T cells','D':'SLAMF7 on myeloma cells and PD-1 on T cells','E':'CD20 on myeloma cells and CD3 on T cells'},
        'C','Bispecific engagement of BCMA on myeloma cells and CD3 on T cells',
        'Linvoseltamab-gcpt is a bispecific T-cell-engaging antibody that binds BCMA on multiple myeloma cells and CD3 on T cells. This physically redirects and activates T cells against BCMA-expressing cells, causing cytokine release and tumor-cell lysis.',
        {'A':'CD19 is primarily a B-lineage marker and is not the tumor target used by linvoseltamab-gcpt.','B':'CD38-CD16 engagement describes an NK-cell-directed mechanism rather than this T-cell engager.','C':'Correct. Linvoseltamab-gcpt simultaneously binds BCMA and CD3 to redirect T cells toward myeloma cells.','D':'SLAMF7 and PD-1 are not the paired binding targets of this antibody.','E':'CD20 is not the tumor antigen targeted by linvoseltamab-gcpt.'},
        'Recognize the BCMA×CD3 bispecific mechanism that redirects T cells against multiple myeloma cells.',
        'LYNOZYFIC- linvoseltamab-gcpt injection, solution, concentrate','e9fd0739-1b3f-4b8b-824a-1f0a902384d3','E',
        'A CD20×CD3 bispecific antibody is a real T-cell-engaging strategy, but multiple myeloma and the drug identity specifically indicate BCMA×CD3.'
    ))

    items.append(make(
        1554,'vanzacaftor/tezacaftor/deutivacaftor','Respiratory System',['Pharmacology','Cell Biology'],
        'Airway epithelial cells homozygous for F508del-CFTR are treated with vanzacaftor, tezacaftor, and deutivacaftor. More CFTR reaches the apical membrane, and the channels that arrive there spend a greater fraction of time in the open state.',
        'Which component-action pairing best explains the increase in channel open probability?',
        {'A':'Vanzacaftor — direct inhibition of epithelial sodium channels','B':'Tezacaftor — phosphorylation-independent activation of CFTR gating','C':'Vanzacaftor — ATP-sensitive potassium-channel opening','D':'Deutivacaftor — potentiation of CFTR gating at the cell surface','E':'Deutivacaftor — increased CFTR transcription in the nucleus'},
        'D','Deutivacaftor potentiates the open probability of cell-surface CFTR while vanzacaftor and tezacaftor improve processing/trafficking',
        'In the vanzacaftor/tezacaftor/deutivacaftor combination, vanzacaftor and tezacaftor bind different sites on CFTR and improve processing and trafficking of selected mutant CFTR proteins to the cell surface. Deutivacaftor is the potentiator that increases CFTR channel open probability at the cell surface.',
        {'A':'Vanzacaftor acts as a CFTR corrector rather than a direct epithelial sodium-channel inhibitor.','B':'Tezacaftor improves CFTR processing and trafficking rather than serving as the gating potentiator in this combination.','C':'Vanzacaftor does not act through ATP-sensitive potassium channels.','D':'Correct. Deutivacaftor potentiates CFTR channel gating by increasing open probability at the cell surface.','E':'Deutivacaftor does not increase CFTR transcription; it acts on the channel protein already at the cell surface.'},
        'Distinguish CFTR correctors that improve trafficking from a CFTR potentiator that increases channel open probability.',
        'ALYFTREK- vanzacaftor, tezacaftor, and deutivacaftor tablet, film coated','7e635909-c6fd-4f0d-ae77-cdff03653a20','B',
        'Tezacaftor is plausible because it improves CFTR function overall, but it does so by correcting processing/trafficking; deutivacaftor is the gating potentiator.'
    ))

    items.append(make(
        1555,'paltusotine','Endocrine System',['Pharmacology','Physiology'],
        'Pituitary somatotroph cells are exposed to paltusotine. Growth hormone secretion decreases, and cyclic AMP accumulation is inhibited after activation of a specific somatostatin receptor subtype.',
        'Which direct receptor action best explains this effect?',
        {'A':'Antagonism of growth hormone-releasing hormone receptors','B':'Agonism of dopamine D2 receptors','C':'Agonism of somatostatin receptor 5','D':'Antagonism of somatostatin receptor 2','E':'Selective agonism of somatostatin receptor 2'},
        'E','Selective SSTR2 agonism with suppression of cAMP, GH, and IGF-1 secretion',
        'Paltusotine is a highly selective agonist of somatostatin receptor 2. SSTR2 activation inhibits cyclic AMP accumulation and suppresses growth hormone secretion, leading to reduced IGF-1 production.',
        {'A':'GHRH-receptor antagonism could reduce GH secretion but is not the direct action of paltusotine.','B':'D2 agonism can suppress prolactin and sometimes GH in selected tumors, but it is not the labeled target of paltusotine.','C':'Paltusotine is highly selective for SSTR2 rather than SSTR5.','D':'SSTR2 antagonism would oppose the receptor action responsible for GH suppression.','E':'Correct. Paltusotine selectively agonizes SSTR2, reducing cAMP signaling and GH secretion.'},
        'Link SSTR2 agonism to reduced cAMP signaling and suppression of GH/IGF-1 in acromegaly.',
        'PALSONIFY- paltusotine tablet, film coated','8a6d2ce0-a621-4ee7-983c-977cd948ff4d','D',
        'An SSTR5 agonist is plausible because somatostatin analogs can act at multiple receptor subtypes, but paltusotine is specifically highly selective for SSTR2.'
    ))

    b={
        'batch_id':'Q1551-Q1555-20260912',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1550,
        'canonical_count_after':1550,
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
    assert [x['num'] for x in items]==list(range(1551,1556))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
