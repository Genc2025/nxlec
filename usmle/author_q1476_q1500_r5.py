#!/usr/bin/env python3
from __future__ import annotations
import json
import author_q1476_q1500 as base

ORIGINAL_ITEMS=base.items


def prior_drugs_allow_historical_duplicates():
    out={}
    covered=[]
    duplicate_history={}
    for p in base.PRIOR_FILES:
        b=json.loads(p.read_text())
        for x in b.get('items',[]):
            q=x.get('num'); d=str(x.get('drug','')).strip().casefold()
            if isinstance(q,int) and 1301<=q<=1475:
                covered.append(q)
                if d:
                    if d in out:
                        prev=out[d]
                        duplicate_history.setdefault(d,[prev] if isinstance(prev,int) else list(prev))
                        duplicate_history[d].append(q)
                        out[d]=duplicate_history[d]
                    else:
                        out[d]=q
    if len(covered)!=175 or set(covered)!=set(range(1301,1476)):
        raise SystemExit(f'prior workstream coverage failure: count={len(covered)} unique={len(set(covered))}')
    return out


def F(q:int,title:str,url:str,locator:str='12.1 Mechanism of Action'):
    return [base.a.src(
        q,'FDA_PI',title,url,'',locator,'2026-09-08',
        'Current FDA prescribing information checked 2026-09-08. This Drugs@FDA label is identified by NDA/application label URL rather than a DailyMed SetID; no SetID is inferred.'
    )]


def replacement_1487():
    return base.a.mk(
      1487,'garadacimab','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology','Physiology'],
      'Plasma from a patient with hereditary angioedema is exposed to a monoclonal antibody before contact-system activation. Formation of kallikrein and bradykinin decreases, but C1 esterase inhibitor concentration is unchanged. The antibody binds the catalytic domain of an activated coagulation factor at the top of the contact pathway.',
      'Which activated factor is directly inhibited?',
      {'A':'Factor XIa','B':'Factor XIIa','C':'Plasma kallikrein','D':'Factor Xa','E':'Thrombin'},'B',
      'Activated factor XII inhibition suppresses kallikrein-kinin activation and bradykinin generation','moderate-hard',
      'Garadacimab-gxii binds the catalytic domain of activated factor XII (FXIIa and beta-FXIIa) and inhibits its catalytic activity. This reduces activation of prekallikrein to kallikrein and decreases bradykinin generation in the kallikrein-kinin system.',
      {
        'A':'Factor XIa participates in intrinsic coagulation downstream of FXII but is not the labeled catalytic-domain target responsible for suppressing the kallikrein-kinin pathway here.',
        'B':'Garadacimab-gxii binds the catalytic domain of activated factor XII (FXIIa and beta-FXIIa) and inhibits its catalytic activity. This reduces activation of prekallikrein to kallikrein and decreases bradykinin generation in the kallikrein-kinin system.',
        'C':'Direct plasma-kallikrein inhibition can also reduce bradykinin, but garadacimab acts one step upstream by inhibiting activated factor XII.',
        'D':'Factor Xa inhibition is anticoagulant therapy and does not directly block initiation of the bradykinin-producing contact system.',
        'E':'Thrombin inhibition acts downstream in coagulation and is not the labeled target of garadacimab.'
      },
      'Place FXIIa upstream of prekallikrein activation and bradykinin generation in the contact-system pathway of hereditary angioedema.',
      base.S(1487,'ANDEMBRY- garadacimab injection, solution','07b0b671-db81-49f0-a402-0c0219db7fa2'),
      'C',
      'Plasma kallikrein is a plausible alternative because its inhibition also lowers bradykinin, but the stem specifies binding to the activated factor at the top of the contact pathway; the label identifies FXIIa.'
    )


def replacement_1490():
    return base.a.mk(
      1490,'oveporexton','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Physiology'],
      'A patient with narcolepsy type 1 has loss of hypothalamic orexin-producing neurons. An oral drug increases wakefulness and reduces cataplexy despite the persistent absence of endogenous orexin peptide. Receptor-binding studies show direct selective agonism of one orexin receptor subtype.',
      'Which receptor is directly activated by this drug?',
      {'A':'GABA-B receptor','B':'Histamine H3 receptor','C':'Orexin receptor 1 (OX1R)','D':'Dopamine D2 receptor','E':'Orexin receptor 2 (OX2R)'},'E',
      'Selective OX2R agonism restores orexin-pathway signaling in narcolepsy type 1','moderate',
      'Oveporexton is an orexin receptor 2 (OX2R) agonist. Direct OX2R activation restores signaling in a pathway deficient because of loss of orexin-producing neurons in narcolepsy type 1.',
      {
        'A':'GABA-B receptor agonism is associated with inhibitory neurotransmission and is not the direct labeled target of oveporexton.',
        'B':'Histamine H3 receptor antagonism can promote wakefulness, but oveporexton does not use this mechanism.',
        'C':'OX1R participates in orexin signaling, but the approved drug is specifically an OX2R agonist.',
        'D':'Dopamine D2 receptor activation is not the labeled mechanism of oveporexton.',
        'E':'Oveporexton is an orexin receptor 2 (OX2R) agonist. Direct OX2R activation restores signaling in a pathway deficient because of loss of orexin-producing neurons in narcolepsy type 1.'
      },
      'Connect narcolepsy type 1 orexin deficiency with pharmacologic restoration of signaling through selective OX2R agonism.',
      F(1490,'ORZYFUL (oveporexton) tablets, prescribing information','https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/220860Orig1s000lbl.pdf'),
      'A',
      'OX1R is biologically related and therefore tempting, but the FDA prescribing information identifies oveporexton specifically as an OX2R agonist.'
    )


def replacement_1497():
    return base.a.mk(
      1497,'sonrotoclax','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry'],
      'Mantle-cell lymphoma cells overexpress an anti-apoptotic mitochondrial protein. After exposure to a small molecule, pro-apoptotic proteins are displaced from that protein, mitochondrial apoptosis proceeds, and caspases are activated. The drug does not inhibit Bruton tyrosine kinase.',
      'Which protein is directly bound and inhibited by the drug?',
      {'A':'Bruton tyrosine kinase','B':'BCL-2','C':'BCL-XL','D':'MCL-1','E':'Proteasome beta-5 subunit'},'B',
      'BCL-2 inhibition releases pro-apoptotic proteins and triggers intrinsic apoptosis','moderate-hard',
      'Sonrotoclax directly binds and inhibits BCL-2, displacing pro-apoptotic proteins and thereby promoting intrinsic apoptotic signaling with caspase activation in BCL-2-dependent malignant cells.',
      {
        'A':'BTK inhibition is an important mantle-cell lymphoma strategy, but the stem states that BTK is not inhibited and the FDA label identifies BCL-2 as sonrotoclax’s target.',
        'B':'Sonrotoclax directly binds and inhibits BCL-2, displacing pro-apoptotic proteins and thereby promoting intrinsic apoptotic signaling with caspase activation in BCL-2-dependent malignant cells.',
        'C':'BCL-XL is another anti-apoptotic BCL-2-family protein, but it is not the direct labeled target of sonrotoclax.',
        'D':'MCL-1 is also anti-apoptotic but is not the protein identified as the direct target in the sonrotoclax prescribing information.',
        'E':'Proteasome beta-5 inhibition causes proteotoxic stress rather than displacement of pro-apoptotic proteins from BCL-2.'
      },
      'Recognize BCL-2 inhibition as release of sequestered pro-apoptotic proteins followed by intrinsic apoptosis.',
      F(1497,'BEQALZI (sonrotoclax) tablets, prescribing information','https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/220711Orig1s000lbl.pdf'),
      'C',
      'BCL-XL and MCL-1 are mechanistically related anti-apoptotic proteins, but the FDA prescribing information specifically identifies BCL-2 as the direct sonrotoclax target.'
    )


def replacement_1500():
    return base.a.mk(
      1500,'centanafadine','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Physiology'],
      'A central nervous system stimulant is studied in presynaptic-neuron preparations. Binding assays show occupancy of three monoamine transporters, and extracellular norepinephrine, dopamine, and serotonin all increase because their reuptake is inhibited. Vesicular monoamine transport is unchanged.',
      'Which transporter profile best matches the direct pharmacologic action?',
      {'A':'DAT only','B':'NET and DAT only','C':'SERT only','D':'VMAT2 and DAT','E':'NET, DAT, and SERT'},'E',
      'Centanafadine inhibits norepinephrine, dopamine, and serotonin reuptake transporters','moderate',
      'Centanafadine binds the norepinephrine transporter (NET), dopamine transporter (DAT), and serotonin transporter (SERT) and inhibits reuptake of all three monoamines.',
      {
        'A':'DAT inhibition alone would increase dopamine but does not account for the directly demonstrated norepinephrine- and serotonin-transporter effects.',
        'B':'NET and DAT inhibition explains two monoamines but omits the directly demonstrated serotonin-transporter inhibition.',
        'C':'SERT inhibition alone would not account for the norepinephrine and dopamine reuptake effects.',
        'D':'VMAT2 controls vesicular monoamine packaging; the stem states that vesicular transport is unchanged, and VMAT2 is not the labeled direct target.',
        'E':'Centanafadine binds the norepinephrine transporter (NET), dopamine transporter (DAT), and serotonin transporter (SERT) and inhibits reuptake of all three monoamines.'
      },
      'Identify centanafadine as a triple norepinephrine-dopamine-serotonin reuptake inhibitor at NET, DAT, and SERT.',
      F(1500,'SIMTRIYO (centanafadine) extended-release capsules, prescribing information','https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/218145s000lbl.pdf'),
      'A',
      'NET/DAT-only inhibition resembles some stimulant mechanisms, but the FDA label directly documents binding to and reuptake inhibition at NET, DAT, and SERT.'
    )


def items_r5():
    replacements={
        1487:replacement_1487(),
        1490:replacement_1490(),
        1497:replacement_1497(),
        1500:replacement_1500(),
    }
    z=[replacements.get(x.get('num'),x) for x in ORIGINAL_ITEMS()]
    if len(z)!=25 or [x['num'] for x in z]!=list(range(1476,1501)):
        raise SystemExit('replacement corrupted Q1476-Q1500 batch shape')
    expected={1487:('garadacimab','B'),1490:('oveporexton','E'),1497:('sonrotoclax','B'),1500:('centanafadine','E')}
    for q,(drug,key) in expected.items():
        x=next(x for x in z if x['num']==q)
        if x['drug']!=drug or x['item']['intended_key']!=key:
            raise SystemExit(f'Q{q} replacement/key corruption')
    return z

# Adversarial exact-name diagnostic before base.main so every proposed collision is reported together.
_prior=prior_drugs_allow_historical_duplicates()
_proposed=items_r5()
_collisions=[]
_seen={}
for x in _proposed:
    d=x['drug'].strip().casefold()
    if d in _prior:
        _collisions.append({'candidate_q':x['num'],'drug':x['drug'],'prior':_prior[d]})
    if d in _seen:
        _collisions.append({'candidate_q':x['num'],'drug':x['drug'],'within_batch_prior_q':_seen[d]})
    _seen[d]=x['num']
if _collisions:
    raise SystemExit('exact-drug collision set: '+json.dumps(_collisions,sort_keys=True))

base.prior_drugs=prior_drugs_allow_historical_duplicates
base.items=items_r5
base.main()
