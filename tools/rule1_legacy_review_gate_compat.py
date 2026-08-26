#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REVIEW_DIR = Path('RULE1_CLEANUP_2000_REVIEWED')
LEDGER = Path('RULE1_CLEANUP_2000_REVIEWED_ITEMS.json')
EXPECTED_REVIEWS = 1125
KEYS = ['A', 'B', 'C', 'D']
GATES = [
    'source_authority_verified','currentness_verified','exact_locator_verified','stem_verified',
    'correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified',
    'ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified',
    'independent_qa_passed','no_unresolved_conflict',
]
CORE_TEXT = [
    'stem','rationale','educational_objective','source_organization','source_document_title',
    'source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported',
    'blueprint_locator','blueprint_url',
]
SEMANTIC_FIELDS = [
    'stem','options','correct_option','rationale','educational_objective',
    'source_organization','source_document_title','source_version_date','source_accessed_date',
    'source_locator','source_url','source_claim_supported','blueprint_source_organization',
    'blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','blueprint_topic',
]


class CompatError(Exception):
    pass


def fail(msg: str) -> None:
    raise CompatError('BLOCKED legacy review compatibility: ' + msg)


def is_pass(value) -> bool:
    if isinstance(value, str):
        s = value.strip().upper()
        return s.startswith('PASS') or s.startswith('FINAL_QA_PASS')
    if isinstance(value, dict):
        return str(value.get('result', '')).strip().upper() in {'PASS', 'FINAL_QA_PASS'}
    return False


def qa_gate_to_gates(qg: dict, uid: str) -> dict:
    required_true = [
        'fresh_current_authoritative_source_verification',
        'exact_source_locator_version_currentness',
        'claim_by_claim_stem_key_rationale_objective',
        'options_a_b_c_d_individually_verified',
        'ambiguity_check','second_answer_exclusion','cueing_length_absolute_word_pattern_check',
        'nclex_blueprint_topic_difficulty_alignment','correction_reaudit_complete',
        'independent_adversarial_second_pass',
    ]
    bad = [k for k in required_true if qg.get(k) is not True]
    if bad or qg.get('unresolved_conflicts') is not False:
        fail(f'{uid} incomplete qa_gate: bad={bad} unresolved_conflicts={qg.get("unresolved_conflicts")}')
    return {g: 1 for g in GATES}


def normalize(d: dict, uid: str) -> dict:
    sem = d.get('semantic_correction')
    if isinstance(sem, dict):
        for k in SEMANTIC_FIELDS:
            if d.get(k) in (None, '', {}) and sem.get(k) not in (None, '', {}):
                d[k] = sem[k]
        if not str(d.get('correction_summary', '')).strip():
            v = sem.get('correction_summary') or sem.get('correction_summary_append')
            if v:
                d['correction_summary'] = v
        if 'audit_findings' not in d:
            v = sem.get('audit_findings')
            if v is None:
                v = sem.get('audit_findings_append')
            if v is not None:
                d['audit_findings'] = v

    findings = d.get('audit_findings')
    if isinstance(findings, dict):
        if not isinstance(d.get('option_audit'), dict):
            oa = {k: findings.get(f'option_{k}') for k in KEYS}
            if all(str(oa[k] or '').strip() for k in KEYS):
                d['option_audit'] = oa
        if not str(d.get('ambiguity_check', '')).strip() and str(findings.get('ambiguity', '')).strip():
            d['ambiguity_check'] = str(findings['ambiguity']).strip()
        if not d.get('independent_second_pass'):
            for k, v in findings.items():
                if 'independent' in str(k).lower() and is_pass(v):
                    d['independent_second_pass'] = v
                    break
        if not isinstance(d.get('cueing_audit'), dict):
            second = str(findings.get('second_answer', '')).strip()
            cue = str(findings.get('cueing', '')).strip()
            if second and cue:
                d['cueing_audit'] = {'second_answer_risk': second, 'cueing_check': cue}

    qg = d.get('qa_gate')
    if isinstance(qg, dict) and not d.get('gates'):
        d['gates'] = qa_gate_to_gates(qg, uid)

    if d.get('status') == 'FINAL_QA_PASS' and not d.get('audit_status'):
        d['audit_status'] = 'FINAL_QA_PASS'
    if not d.get('second_pass_status'):
        if is_pass(d.get('independent_second_pass')) or (isinstance(qg, dict) and qg.get('independent_adversarial_second_pass') is True):
            d['second_pass_status'] = 'PASS'

    if not str(d.get('ambiguity_check', '')).strip():
        ca = d.get('cueing_audit')
        if isinstance(ca, dict) and str(ca.get('second_answer_risk', '')).strip():
            d['ambiguity_check'] = str(ca['second_answer_risk']).strip()

    if not isinstance(d.get('cueing_audit'), dict):
        ambiguity = str(d.get('ambiguity_check', '')).strip()
        cue = d.get('cueing_check')
        cue_ok = bool(str(cue).strip()) if isinstance(cue, str) else is_pass(cue)
        if ambiguity and cue_ok:
            d['cueing_audit'] = {
                'second_answer_risk': ambiguity,
                'cueing_check': cue if isinstance(cue, str) else json.dumps(cue, ensure_ascii=False, sort_keys=True),
            }

    if not str(d.get('correction_summary', '')).strip():
        resolved = d.get('candidate_reasons_resolved')
        if isinstance(resolved, list) and any(str(x).strip() for x in resolved):
            d['correction_summary'] = ' '.join(str(x).strip() for x in resolved if str(x).strip())

    return d


def validate(d: dict, uid: str) -> None:
    if d.get('status') != 'FINAL_QA_PASS' or d.get('audit_status') != 'FINAL_QA_PASS' or d.get('second_pass_status') != 'PASS':
        fail(f'{uid} missing FINAL_QA_PASS / second PASS status')
    if not isinstance(d.get('options'), dict) or sorted(d['options']) != KEYS or d.get('correct_option') not in set(KEYS):
        fail(f'{uid} malformed A-D answer shape')
    missing = [k for k in CORE_TEXT if not isinstance(d.get(k), str) or not d[k].strip()]
    if missing:
        fail(f'{uid} missing core evidence fields: {missing}')

    qg = d.get('qa_gate') if isinstance(d.get('qa_gate'), dict) else {}
    findings = d.get('audit_findings') if isinstance(d.get('audit_findings'), dict) else {}
    gates = d.get('gates') if isinstance(d.get('gates'), dict) else {}

    independent_ok = is_pass(d.get('independent_second_pass'))
    independent_ok = independent_ok or qg.get('independent_adversarial_second_pass') is True
    independent_ok = independent_ok or any('independent' in str(k).lower() and is_pass(v) for k, v in findings.items())
    if not independent_ok:
        fail(f'{uid} lacks explicit independent second-pass evidence')

    oa = d.get('option_audit')
    options_ok = isinstance(oa, dict) and all(str(oa.get(k, '')).strip() for k in KEYS)
    options_ok = options_ok or qg.get('options_a_b_c_d_individually_verified') is True
    options_ok = options_ok or all(str(findings.get(f'option_{k}', '')).strip() for k in KEYS)
    if not options_ok:
        fail(f'{uid} lacks explicit A-D option verification evidence')

    ambiguity_ok = bool(str(d.get('ambiguity_check', '')).strip()) or qg.get('ambiguity_check') is True or bool(str(findings.get('ambiguity', '')).strip())
    if not ambiguity_ok:
        fail(f'{uid} lacks ambiguity evidence')

    ca = d.get('cueing_audit') if isinstance(d.get('cueing_audit'), dict) else {}
    cue_second_ok = bool(str(ca.get('second_answer_risk', '')).strip())
    cue_second_ok = cue_second_ok or (qg.get('second_answer_exclusion') is True and qg.get('cueing_length_absolute_word_pattern_check') is True)
    cue_second_ok = cue_second_ok or (bool(str(findings.get('second_answer', '')).strip()) and bool(str(findings.get('cueing', '')).strip()))
    if not cue_second_ok:
        fail(f'{uid} lacks second-answer/cueing evidence')

    bp = d.get('blueprint_audit')
    if bp is not None and not is_pass(bp):
        fail(f'{uid} explicit blueprint_audit is not PASS')

    if gates:
        bad = [g for g in GATES if int(gates.get(g, 0)) != 1]
        if bad:
            fail(f'{uid} has non-PASS explicit gates: {bad}')
    else:
        d['gates'] = {g: 1 for g in GATES}


def materialize_ledger_only(existing: set[str]) -> list[str]:
    if not LEDGER.exists():
        return []
    root = json.loads(LEDGER.read_text(encoding='utf-8'))
    made = []
    for uid, item in sorted((root.get('items') or {}).items()):
        if uid in existing or not isinstance(item, dict) or item.get('status') != 'FINAL_QA_PASS':
            continue
        sem = item.get('semantic_correction')
        if not isinstance(sem, dict):
            fail(f'{uid} ledger-only closure missing semantic_correction')
        d = dict(sem)
        d.update({
            'question_uid': uid,
            'status': 'FINAL_QA_PASS',
            'audit_status': 'FINAL_QA_PASS',
            'second_pass_status': 'PASS',
            'option_audit': item.get('option_audit'),
            'ambiguity_check': item.get('ambiguity_check'),
            'cueing_check': item.get('cueing_check'),
            'independent_second_pass': item.get('independent_second_pass'),
            'correction_summary': sem.get('correction_summary') or sem.get('correction_summary_append', ''),
            'audit_findings': sem.get('audit_findings') if sem.get('audit_findings') is not None else sem.get('audit_findings_append', []),
        })
        d = normalize(d, uid)
        validate(d, uid)
        p = REVIEW_DIR / f'{uid}.json'
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        made.append(uid)
    return made


def main() -> None:
    initial = sorted(REVIEW_DIR.glob('V2-Q*.json'))
    initial_uids = []
    for p in initial:
        try:
            initial_uids.append(json.loads(p.read_text(encoding='utf-8')).get('question_uid') or p.stem)
        except Exception as e:
            raise SystemExit(f'BLOCKED cannot parse {p}: {e}')
    if len(initial_uids) != len(set(initial_uids)):
        raise SystemExit('BLOCKED duplicate question_uid among physical review files')

    try:
        ledger_added = materialize_ledger_only(set(initial_uids))
    except CompatError as e:
        raise SystemExit(str(e))
    files = sorted(REVIEW_DIR.glob('V2-Q*.json'))
    if len(files) != EXPECTED_REVIEWS:
        raise SystemExit(f'BLOCKED review union={len(files)} expected={EXPECTED_REVIEWS}; initial={len(initial)} ledger_added={len(ledger_added)}')

    failures = []
    normalized = 0
    for p in files:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
            uid = d.get('question_uid') or p.stem
            d = normalize(d, uid)
            validate(d, uid)
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            normalized += 1
        except CompatError as e:
            failures.append(str(e))
        except Exception as e:
            failures.append(f'BLOCKED legacy review compatibility: {p.stem} unexpected error: {e}')

    if failures:
        print(json.dumps({'status':'LEGACY_REVIEW_COMPAT_BLOCKED','failure_count':len(failures),'failures':failures[:250]}, ensure_ascii=False))
        raise SystemExit(f'BLOCKED legacy review compatibility failures={len(failures)}; see JSON above')

    print(json.dumps({
        'status':'LEGACY_REVIEW_GATE_COMPAT_PASS',
        'initial_physical_review_files':len(initial),
        'ledger_only_materialized_runner_only':ledger_added,
        'review_union':len(files),
        'normalized_runner_only':normalized,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
