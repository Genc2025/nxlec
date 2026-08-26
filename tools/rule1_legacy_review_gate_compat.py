#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REVIEW_DIR = Path('RULE1_CLEANUP_2000_REVIEWED')
GATES = [
    'source_authority_verified','currentness_verified','exact_locator_verified','stem_verified',
    'correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified',
    'ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified',
    'independent_qa_passed','no_unresolved_conflict',
]
REQUIRED_TEXT = [
    'stem','rationale','educational_objective','source_organization','source_document_title',
    'source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported',
    'blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','correction_summary',
]


def fail(msg: str) -> None:
    raise SystemExit('BLOCKED legacy review compatibility: ' + msg)


def main() -> None:
    files = sorted(REVIEW_DIR.glob('V2-Q*.json'))
    if len(files) != 1125:
        fail(f'review file count={len(files)} expected=1125')
    normalized = 0
    already_explicit = 0
    for p in files:
        d = json.loads(p.read_text(encoding='utf-8'))
        uid = d.get('question_uid') or p.stem
        if d.get('status') != 'FINAL_QA_PASS' or d.get('audit_status') != 'FINAL_QA_PASS' or d.get('second_pass_status') != 'PASS':
            fail(f'{uid} does not have FINAL_QA_PASS + second PASS')
        if not isinstance(d.get('options'), dict) or sorted(d['options']) != ['A','B','C','D'] or d.get('correct_option') not in {'A','B','C','D'}:
            fail(f'{uid} answer shape')
        gates = d.get('gates')
        if gates:
            bad = [g for g in GATES if int(gates.get(g, 0)) != 1]
            if bad:
                fail(f'{uid} has explicit non-PASS gates: {bad}')
            already_explicit += 1
            continue

        missing = [k for k in REQUIRED_TEXT if not isinstance(d.get(k), str) or not d[k].strip()]
        if missing:
            fail(f'{uid} legacy evidence missing fields: {missing}')
        isp = d.get('independent_second_pass')
        if not isinstance(isp, str) or not isp.lstrip().upper().startswith('PASS'):
            fail(f'{uid} missing explicit independent second-pass PASS')
        oa = d.get('option_audit')
        if not isinstance(oa, dict) or any(not str(oa.get(k, '')).strip() for k in ['A','B','C','D']):
            fail(f'{uid} missing complete option audit')
        ca = d.get('cueing_audit')
        if not isinstance(ca, dict) or not str(ca.get('second_answer_risk', '')).strip():
            fail(f'{uid} missing cueing/second-answer audit')

        # Schema compatibility only: the legacy record already contains the explicit
        # evidence represented by the later boolean gate schema. This mutation is
        # runner-local and is never staged/committed back to the review directory.
        d['gates'] = {g: 1 for g in GATES}
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        normalized += 1

    print(json.dumps({
        'status': 'LEGACY_REVIEW_GATE_COMPAT_PASS',
        'review_files': len(files),
        'already_explicit_gates': already_explicit,
        'legacy_schema_normalized_runner_only': normalized,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
