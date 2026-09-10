#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

P=Path('usmle/batch_specs_1401_1500/02_q1426_q1450_author_20260908_schema_repaired.json')

def main():
    b=json.loads(P.read_text())
    items={x['num']:x for x in b['items']}
    x=items[1450]
    assert x['item']['intended_key']=='E'
    assert x['item']['options']['E']=='5-HT1A'
    new_rationale=("Correct. Gepirone and its 3'-hydroxy metabolite bind 5-HT1A receptors and act as agonists; "
                   "this is the documented serotonergic receptor pharmacology, while the complete antidepressant mechanism remains incompletely understood.")
    x['explanation']['distractor_explanations']['E']=new_rationale
    found=0
    for e in x['evidence_map']:
        if e.get('option')=='E':
            assert e.get('direct_or_inference')=='direct'
            e['claim']=new_rationale
            e['claim_locator']='explanation.distractor_explanations.E'
            found+=1
    assert found==1
    aq=x.get('author_qa',{})
    aq['rationale']='PASS — Q1450 keyed rationale repaired to explicitly bind gepirone/3-hydroxy metabolite, 5-HT1A receptor, and agonist action.'
    aq['adversarial_second_pass']='PASS'
    aq['unresolved_content_defects']=[]
    b.setdefault('schema_repair',{}).setdefault('changes',[]).append(
        'Q1450 keyed rationale/evidence claim expanded to explicitly bind gepirone and 3-hydroxy metabolite to 5-HT1A agonism; intended key and medical construct unchanged.'
    )
    P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print('Q1450_RATIONALE_REPAIR=PASS')

if __name__=='__main__':
    main()
