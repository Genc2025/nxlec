#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
import author_q1476_q1500 as base
import author_q1476_q1500_r6 as r6


def main():
    prior=r6.r5.prior_drugs_allow_historical_duplicates()
    xs=r6.items_r6()
    assert [x['num'] for x in xs]==list(range(1476,1501)) and len(xs)==25
    keys=''.join(x['item']['intended_key'] for x in xs)
    assert keys=='ABCDEABCDEABCDEABCDEABCDE'
    assert Counter(keys)==Counter({'A':5,'B':5,'C':5,'D':5,'E':5})
    collisions=[]; seen={}
    for x in xs:
        d=x['drug'].strip().casefold()
        if d in prior: collisions.append({'candidate_q':x['num'],'drug':x['drug'],'prior':prior[d]})
        if d in seen: collisions.append({'candidate_q':x['num'],'drug':x['drug'],'within_batch_prior_q':seen[d]})
        seen[d]=x['num']
    if collisions: raise SystemExit('exact-drug collision set: '+json.dumps(collisions,sort_keys=True))
    for x in xs:
        assert len(x['evidence_map'])==5
        em={e['option']:e for e in x['evidence_map']}; assert set(em)==set('ABCDE')
        key=x['item']['intended_key']
        for L in 'ABCDE':
            assert em[L]['claim']==x['explanation']['distractor_explanations'][L]
            assert em[L]['direct_or_inference']==('direct' if L==key else 'inference')
        for s in x['sources']:
            assert s.get('section_locator') and s.get('retrieved_at')=='2026-09-08'
            u=s.get('url','')
            if 'dailymed.nlm.nih.gov' in u:
                assert s.get('setid') and not s.get('fda_application_id')
            elif 'accessdata.fda.gov' in u:
                assert not s.get('setid')
                assert s.get('identifier_type')=='FDA_NDA' and s.get('fda_application_id')
            else:
                raise AssertionError((x['num'],'unsupported source',u))
    assert 'ncjmm' not in json.dumps(xs,ensure_ascii=False).casefold()
    systems=dict(Counter(x['blueprint']['primary_system'] for x in xs))
    b={
      'batch_id':'Q1476-Q1500-20260908','created_at':'2026-09-08',
      'status':'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT',
      'production_import_ready':False,'candidate_count':25,'preceding_candidate_range':'Q1301-Q1475',
      'new_workstream_candidate_count':200,'canonical_count_before':1300,'canonical_count_after':1300,
      'answer_key_sequence':keys,'answer_key_distribution':{'A':5,'B':5,'C':5,'D':5,'E':5},
      'systems':systems,
      'shared_sources':[
        {'source_id':'USMLE-SPEC','title':'Step 1 Exam Content','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications','retrieved_at':'2026-09-08','section_locator':'Step 1 Content Specifications; Physician Tasks/Competencies Specifications; Discipline Specifications'},
        {'source_id':'USMLE-FORMAT','title':'Step 1 Formats & Questions','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-test-question-formats','retrieved_at':'2026-09-08','section_locator':'Single-best-answer format'}],
      'items':xs,
      'technical_integrity':{
        'exact_drug_reuse_gate_q1301_q1475':'PASS',
        'source_identifier_contract':'PASS_DAILYMED_SETID_OR_FDA_NDA_AS_APPLICABLE',
        'evidence_map_a_e_contract':'PASS','answer_key_balance':'PASS',
        'deterministic_live_source_preflight_complete':False,
        'independent_auditor_a_complete':False,'independent_auditor_b_complete':False,'trusted_importer_complete':False},
      'author_note':'Drafting, evidence mapping, key balance, exact-drug reuse screening, source-identifier typing, and internal adversarial repair were completed before materialization. Non-applicable nursing-exam metadata is intentionally absent. Full deterministic canonical/workstream/live-source collision preflight remains mandatory on the immutable candidate blob.'
    }
    raw=json.dumps(b,ensure_ascii=False).casefold()
    assert 'ncjmm' not in raw
    base.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print('WROTE',base.OUT)
    print('COUNT',len(xs),'KEYS',keys,'ZERO_NONUSMLE_TERM=PASS','SOURCE_IDENTIFIER_CONTRACT=PASS')

if __name__=='__main__':
    main()
