#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
import author_q1476_q1500 as base

# Load the fully repaired R5 definitions without invoking its legacy source-schema main().
_ORIGINAL_MAIN=base.main
base.main=lambda: None
import author_q1476_q1500_r5 as r5
base.main=_ORIGINAL_MAIN

FDA_IDS={
    1490:'NDA 220860',
    1497:'NDA 220711',
    1500:'NDA 218145',
}


def items_r6():
    xs=r5.items_r5()
    for x in xs:
        q=x['num']
        if q in FDA_IDS:
            for s in x['sources']:
                if 'accessdata.fda.gov' in s.get('url',''):
                    if s.get('setid'):
                        raise SystemExit(f'Q{q}: FDA source unexpectedly populated DailyMed setid')
                    s['identifier_type']='FDA_NDA'
                    s['fda_application_id']=FDA_IDS[q]
    return xs


def main():
    prior=r5.prior_drugs_allow_historical_duplicates()
    xs=items_r6()
    assert [x['num'] for x in xs]==list(range(1476,1501))
    assert len(xs)==25
    keys=''.join(x['item']['intended_key'] for x in xs)
    assert keys=='ABCDEABCDEABCDEABCDEABCDE'
    assert Counter(keys)==Counter({'A':5,'B':5,'C':5,'D':5,'E':5})

    collisions=[]; seen={}
    for x in xs:
        d=x['drug'].strip().casefold()
        if d in prior:
            collisions.append({'candidate_q':x['num'],'drug':x['drug'],'prior':prior[d]})
        if d in seen:
            collisions.append({'candidate_q':x['num'],'drug':x['drug'],'within_batch_prior_q':seen[d]})
        seen[d]=x['num']
    if collisions:
        raise SystemExit('exact-drug collision set: '+json.dumps(collisions,sort_keys=True))

    for x in xs:
        assert len(x['evidence_map'])==5
        em={e['option']:e for e in x['evidence_map']}
        assert set(em)==set('ABCDE')
        key=x['item']['intended_key']
        for L in 'ABCDE':
            assert em[L]['claim']==x['explanation']['distractor_explanations'][L]
            assert em[L]['direct_or_inference']==('direct' if L==key else 'inference')
        assert len(x['sources'])>=1
        for s in x['sources']:
            assert s.get('section_locator') and s.get('retrieved_at')=='2026-09-08'
            host=s.get('url','')
            if 'dailymed.nlm.nih.gov' in host:
                assert s.get('setid'),(x['num'],'DailyMed source missing SetID')
                assert not s.get('fda_application_id'),(x['num'],'DailyMed source has wrong FDA identifier')
            elif 'accessdata.fda.gov' in host:
                assert not s.get('setid'),(x['num'],'FDA source must not invent DailyMed SetID')
                assert s.get('identifier_type')=='FDA_NDA' and s.get('fda_application_id'),(x['num'],'FDA source missing NDA identifier')
            else:
                raise AssertionError((x['num'],'unapproved source host',host))

    raw=json.dumps(xs,ensure_ascii=False).casefold()
    assert 'ncjmm' not in raw
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
        'evidence_map_a_e_contract':'PASS','answer_key_balance':'PASS','ncjmm':'NOT_APPLICABLE_USMLE',
        'deterministic_live_source_preflight_complete':False,'independent_auditor_a_complete':False,'independent_auditor_b_complete':False,'trusted_importer_complete':False},
      'author_note':'Drafting, evidence mapping, key balance, exact-drug reuse screening, source-identifier typing, and internal adversarial repair were completed before materialization. Full deterministic canonical/workstream/live-source collision preflight remains mandatory on the immutable candidate blob.'
    }
    base.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print('WROTE',base.OUT)
    print('COUNT',len(xs),'KEYS',keys,'SOURCE_IDENTIFIER_CONTRACT=PASS')

if __name__=='__main__':
    main()
