#!/usr/bin/env python3
from __future__ import annotations
import json
import author_q1476_q1500 as base


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


def items_r3():
    z=base.items()
    replacement=base.a.mk(
      1487,'brensocatib','Respiratory System',['Pharmacology','Immunology','Biochemistry'],
      'Bone-marrow neutrophil precursors are exposed to an oral small molecule during granule-protease maturation. After treatment, mature circulating neutrophils contain markedly reduced active neutrophil elastase, cathepsin G, and proteinase 3, although the genes encoding these proteases are transcribed normally.',
      'Inhibition of which enzyme during neutrophil maturation best explains these findings?',
      {'A':'Neutrophil elastase','B':'Dipeptidyl peptidase 1 (DPP1/cathepsin C)','C':'Myeloperoxidase','D':'NADPH oxidase','E':'Cathepsin D'},'B',
      'DPP1 inhibition prevents activation of neutrophil serine proteases during neutrophil maturation','moderate-hard',
      'Brensocatib is a competitive, reversible inhibitor of dipeptidyl peptidase 1 (DPP1). DPP1 activates pro-inflammatory neutrophil serine proteases during neutrophil maturation; inhibiting DPP1 therefore reduces the activities of neutrophil elastase, cathepsin G, and proteinase 3.',
      {
        'A':'Neutrophil elastase is one downstream serine protease whose activity falls; brensocatib does not directly inhibit neutrophil elastase as its primary target.',
        'B':'Brensocatib is a competitive, reversible inhibitor of dipeptidyl peptidase 1 (DPP1). DPP1 activates pro-inflammatory neutrophil serine proteases during neutrophil maturation; inhibiting DPP1 therefore reduces the activities of neutrophil elastase, cathepsin G, and proteinase 3.',
        'C':'Myeloperoxidase generates hypochlorous acid in neutrophil granules but does not proteolytically activate this group of neutrophil serine proteases.',
        'D':'NADPH oxidase generates the respiratory burst; its inhibition would impair reactive oxygen species production rather than selectively prevent maturation of neutrophil serine proteases.',
        'E':'Cathepsin D is a lysosomal aspartyl protease and is not the labeled upstream activator targeted by brensocatib.'
      },
      'Connect DPP1/cathepsin C activity in bone-marrow neutrophil maturation with activation of neutrophil elastase, cathepsin G, and proteinase 3.',
      base.S(1487,'BRINSUPRI- brensocatib tablet','b56986ae-e7db-421e-b622-a7f41e321f3d'),
      'C',
      'Direct inhibition of neutrophil elastase could lower one measured protease, but the simultaneous fall in elastase, cathepsin G, and proteinase 3 points to their shared upstream activator DPP1.'
    )
    z=[replacement if x.get('num')==1487 else x for x in z]
    if len(z)!=25 or [x['num'] for x in z]!=list(range(1476,1501)):
        raise SystemExit('replacement corrupted Q1476-Q1500 batch shape')
    if next(x for x in z if x['num']==1487)['item']['intended_key']!='B':
        raise SystemExit('Q1487 key-balance corruption')
    return z

base.prior_drugs=prior_drugs_allow_historical_duplicates
base.items=items_r3
base.main()
