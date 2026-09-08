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


def items_r4():
    z=ORIGINAL_ITEMS()
    replacement=base.a.mk(
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
    z=[replacement if x.get('num')==1487 else x for x in z]
    if len(z)!=25 or [x['num'] for x in z]!=list(range(1476,1501)):
        raise SystemExit('replacement corrupted Q1476-Q1500 batch shape')
    q=next(x for x in z if x['num']==1487)
    if q['drug']!='garadacimab' or q['item']['intended_key']!='B':
        raise SystemExit('Q1487 replacement/key corruption')
    return z

base.prior_drugs=prior_drugs_allow_historical_duplicates
base.items=items_r4
base.main()
