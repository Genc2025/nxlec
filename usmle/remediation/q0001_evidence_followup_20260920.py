"""Narrow, hash-guarded Q0001 repair. This does not grant production approval."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CID = 'S1-DIRECT-0001-20260826T223550Z'
EXPECTED = 'a801ece29a0a2ab22dd5c180afce4dee6e2ac440d8da77623344bf6b1c4c7548'
AUDIT = 'Q0001_EVIDENCE_FOLLOWUP_20260920'


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def main():
    db = sqlite3.connect(ROOT / 'data/usmle-step1.db')
    db.row_factory = sqlite3.Row
    archive_path = ROOT / 'remediation' / (AUDIT + '_BEFORE_ROWS.json')
    with db:
        db.execute('BEGIN IMMEDIATE')
        old = dict(db.execute('SELECT * FROM step2_final_items WHERE candidate_id=?', (CID,)).fetchone())
        review = dict(db.execute('SELECT * FROM step2_final_reviews WHERE candidate_id=?', (CID,)).fetchone())
        p = json.loads(old['payload_json'])
        if p.get('current_reaudit', {}).get('audit_id') == AUDIT:
            assert digest(p) == old['payload_sha256']
            assert archive_path.exists(), 'Applied repair without archive'
            print('Already applied; no rows changed')
            return
        assert old['payload_sha256'] == EXPECTED == digest(p)
        assert db.execute('SELECT count(*) FROM step2_final_items').fetchone()[0] == 1635
        original_item = dict(p['item'])
        p['item'].update(difficulty='easy', reasoning_steps_count=2,
            difficulty_basis='Author estimate, not psychometrically calibrated: recognize a mild retrieval complaint with preserved daily function, then select the expected cognitive-domain pattern. No calculation or management decision is required.')
        p['semantic_fingerprint']['reasoning_chain'] = [
            'Recognize a history compatible with normal aging; independence alone does not exclude mild cognitive impairment.',
            'Answer the explicitly normal-aging comparison by selecting the expected cognitive-domain pattern.'
        ]
        note = ' Preserved independence alone does not exclude mild cognitive impairment; this question asks for the expected pattern in normal aging, not a definitive exclusion of every cognitive disorder.'
        p['explanation']['key_explanation'] += note
        p['explanation']['distractor_explanations']['A'] += note
        p['explanation']['educational_objective'] = 'Recognize the expected cognitive pattern of normal aging while avoiding the inference that independent daily function alone excludes mild cognitive impairment.'
        for entry in p['evidence_map']:
            entry['rationale'] = p['explanation']['distractor_explanations'][entry['option']]
            entry['evidence_basis'] = 'LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION'
            entry['source_ids'] = ['S1', 'S2'] if entry['option'] == 'A' else ['S1']
            entry['audit_record'] = 'audit/' + AUDIT + '.md'
        for source in p['sources']:
            source['retrieved_at'] = '2026-09-20'
            source['passage_type'] = 'Reviewer paraphrase, not a verbatim quotation'
            source['set_id_applicability'] = 'NOT_APPLICABLE_NON_DRUG_SOURCE'
            source['raw_source_sha256'] = None
            source['capture_limitation'] = 'Readable live web extraction inspected; raw source bytes were not captured. No raw-source hash is asserted.'
        p['sources'][0]['section_locator'] = 'Introduction, age-related thinking changes and retained abilities, before Clinical trials on brain aging'
        p['sources'][1]['publication_or_revision_date'] = 'Content reviewed November 22, 2023'
        p['sources'][1]['section_locator'] = 'Memory changes with age; Mild cognitive impairment; Dementia versus age-related forgetfulness'
        p['sources'][1]['supporting_passage'] = 'Mild forgetfulness can accompany aging. Repeated questions and getting lost merit evaluation. People with mild cognitive impairment may still perform daily tasks independently; independence therefore does not by itself exclude MCI.'
        # Preserve old declarations as history rather than present-tense PASS claims.
        historical = p.setdefault('historical_audit_metadata', {})
        for field in ('author_self_audit', 'step2_final_audit', 'hashes'):
            if field in p:
                historical[field] = p.pop(field)
        p['current_reaudit'] = {
            'audit_id': AUDIT, 'status': 'BLOCKED_PENDING_FULL_REAUDIT',
            'full_clinical_certification': False,
            'same_reviewer_content_passes': 2,
            'independent_blind_passes': 0,
            'corrections': ['Remove unsupported difficulty calibration and redundant reasoning count',
                'Do not infer exclusion of MCI from preserved independence',
                'Bind source date, section and option-specific references to inspected NIA pages',
                'Isolate obsolete self-scores, hashes and PASS labels as historical metadata'],
            'remaining_gates': ['Independent isolated author/auditor workflow required by README',
                'Durable source-byte capture and evidence hashes',
                'Exhaustive semantic comparison beyond candidate keyword screening']
        }
        assert p['item']['options'] == original_item['options']
        assert p['item']['intended_key'] == original_item['intended_key'] == 'A'
        assert p['item']['vignette'] == original_item['vignette']
        rh = {'candidate_id': CID, 'verdict': 'BLOCKED_PENDING_FULL_REAUDIT',
            'payload_sha256': digest(p), 'prior_review_sha256': review['review_sha256'],
            'reviewed_at': '2026-09-20', 'audit_record': 'audit/' + AUDIT + '.md',
            'review_scope': 'Live claim review and same-reviewer adversarial reread; not independent certification',
            'defects': p['current_reaudit']['remaining_gates']}
        archive = {'item_row': old, 'review_row': review}
        if archive_path.exists():
            assert json.loads(archive_path.read_text()) == archive
        else:
            archive_path.write_text(json.dumps(archive, indent=2) + '\n')
        db.execute('UPDATE step2_final_items SET payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?',
                   (canon(p), digest(p), digest(rh), rh['verdict'], '2026-09-20', CID))
        db.execute('UPDATE step2_final_reviews SET review_json=?,review_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?',
                   (canon(rh), digest(rh), rh['verdict'], '2026-09-20', CID))
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    result = {'candidate_id': CID, 'before_sha256': EXPECTED, 'after_sha256': digest(p),
              'status': rh['verdict'], 'new_final_passes': 0, 'item_count': 1635}
    (ROOT / 'audit' / (AUDIT + '_RESULT.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
