"""Apply explicit reviewed payloads as one guarded batch; never certify clinical QA."""
import json, sqlite3, sys
from pathlib import Path
from q0006_clinical_followup_20260920 import canon, digest

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads(Path(sys.argv[1]).read_text())
    batch = manifest['batch_id']
    archive_path = ROOT / 'remediation' / (batch + '_BEFORE_ROWS.json')
    result_path = ROOT / 'audit' / (batch + '_RESULT.json')
    db = sqlite3.connect(ROOT / 'data/usmle-step1.db')
    db.row_factory = sqlite3.Row
    before, updates = [], []
    with db:
        db.execute('BEGIN IMMEDIATE')
        assert db.execute('select count(*) from step2_final_items').fetchone()[0] == manifest['canonical_count']
        for entry in manifest['changes']:
            cid, p = entry['candidate_id'], entry['payload']
            old = dict(db.execute('select * from step2_final_items where candidate_id=?', (cid,)).fetchone())
            rev = dict(db.execute('select * from step2_final_reviews where candidate_id=?', (cid,)).fetchone())
            assert digest(json.loads(old['payload_json'])) == old['payload_sha256']
            if old['payload_sha256'] == digest(p):
                assert old['final_status'] == rev['final_status'] == 'BLOCKED_PENDING_FULL_REAUDIT'
                continue
            assert old['payload_sha256'] == entry['before_sha256'], 'Concurrent item change: ' + cid
            assert p['current_reaudit']['status'] == 'BLOCKED_PENDING_FULL_REAUDIT'
            before.append(dict(item_row=old, review_row=rev))
            review = dict(candidate_id=cid, verdict='BLOCKED_PENDING_FULL_REAUDIT', payload_sha256=digest(p),
                prior_review_sha256=rev['review_sha256'], reviewed_at=manifest['date'],
                audit_record=manifest['audit_record'], defects=p['current_reaudit']['remaining_gates'])
            updates.append((cid, p, review))
        if not updates:
            assert archive_path.exists() and result_path.exists()
            print('Batch already applied; no changes'); return
        assert len(updates) == len(manifest['changes']), 'Refuse partial batch replay'
        if archive_path.exists():
            assert json.loads(archive_path.read_text()) == before
        else:
            archive_path.write_text(json.dumps(before, indent=2) + '\n')
        for cid, p, review in updates:
            db.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',
                (canon(p), digest(p), digest(review), review['verdict'], manifest['date'], cid))
            db.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',
                (canon(review), digest(review), review['verdict'], manifest['date'], cid))
        assert db.execute('pragma integrity_check').fetchone()[0] == 'ok'
    result = dict(batch_id=batch, changed=len(updates), full_clinical_passes=0,
        after_hashes={cid:digest(p) for cid,p,_ in updates})
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(batch_id=batch,changed=len(updates),full_clinical_passes=0)))

if __name__ == '__main__': main()
