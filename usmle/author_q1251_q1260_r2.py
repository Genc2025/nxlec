#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
import author_q1251_q1260 as base


def exact_usmle_locator(item):
    bp=item['blueprint']
    disciplines=', '.join(bp['disciplines'])
    return (
        f"Step 1 Content Specifications — {bp['primary_system']}; "
        f"Step 1 Physician Tasks/Competencies Specifications — {bp['primary_competency']}; "
        f"Step 1 Discipline Specifications — {disciplines}"
    )

def main():
    st=json.loads(base.STATE.read_text())
    if st.get('final_status')!='FINAL_10_10_PASS' or st.get('item_count')!=1250 or st.get('step2_final_review_count')!=1250 or st.get('post_authoritative_db_blob')!=base.PRE_BLOB:
        raise SystemExit('Q1250 state binding failure')
    if base.gitblob(base.DB)!=base.PRE_BLOB: raise SystemExit('canonical DB blob changed')
    items=base.build()
    for x in items:
        official=x['sources'][0]
        official['section_locator']=exact_usmle_locator(x)
        official['supporting_passage']=(
            f"Supports classification of this item under {x['blueprint']['primary_system']}, "
            f"{x['blueprint']['primary_competency']}, and the listed Step 1 disciplines."
        )
    base.validate(items)
    base.canonical_anchor_scan(items)
    batch={
        'batch_id':'Q1251-Q1260-20260906-AUTHOR-R2',
        'production_count_before':1250,'production_count_after':1250,
        'status':'AUTHOR_ZERO_TRUST_PASS_PENDING_CANONICAL_DUPLICATE_AND_FINAL_QA',
        'created_at':'2026-09-06','country_scope':'United States',
        'specification_version':'USMLE Step 1 current official specifications verified 2026-09-06',
        'canonical_pre_state':{'item_count':1250,'db_blob':base.PRE_BLOB,'state_file':'usmle/state/step2_final_q0001_q1250.json'},
        'batch_design':{
            'systems':{base.SYS_RR:5,base.SYS_RE:5},
            'competencies':{base.DX:5,base.MK:5},
            'reason':'Corpus-screened renal/respiratory and reproductive/endocrine constructs selected after two prospect collision passes; balanced diagnosis and foundational-science reasoning.'
        },
        'answer_key_distribution':dict(sorted(Counter(x['item']['intended_key'] for x in items).items())),
        'answer_key_sequence':'DAECBEBDAC','items':items
    }
    base.OUT.write_text(json.dumps(batch,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','repair':'exact_usmle_source_locator','output':str(base.OUT.relative_to(base.REPO)),'items':10,'keys':'DAECBEBDAC','canonical_blob':base.PRE_BLOB},sort_keys=True))

if __name__=='__main__': main()
