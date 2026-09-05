#!/usr/bin/env python3
"""Read-only term retrieval for human originality review; never an acceptance gate.

Example: python usmle/corpus_probe.py --term GNAS --term MC2R --term CASR
Matches include distractors, so a hit alone does not establish duplication.
No matches do not establish originality. Review synonymous constructs and staged
candidates separately. The database is opened read-only and must already exist.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def probe(database, terms):
    database = Path(database).resolve(strict=True)
    normalized = [term.casefold().strip() for term in terms]
    if not normalized or any(not term for term in normalized):
        raise ValueError('Supply at least one nonempty search term')
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as con:
        con.execute('PRAGMA query_only=ON')
        rows = con.execute(
            'SELECT candidate_id, payload_json, payload_sha256, final_status '
            'FROM step2_final_items ORDER BY candidate_id'
        ).fetchall()
        matches = []
        for candidate_id, payload, stored_hash, status in rows:
            item = json.loads(payload)['item']
            searchable = json.dumps(item, ensure_ascii=False).casefold()
            matched = [term for term in normalized if term in searchable]
            if matched:
                matches.append(dict(candidate_id=candidate_id, matched_terms=matched,
                                    stored_payload_sha256=stored_hash,
                                    computed_payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                                    final_status=status, item=item))
    return dict(scope='step2_final_items; item fields only; all statuses',
                scanned_rows=len(rows), terms=normalized, matches=matches,
                acceptance_verdict=None,
                limitation='Term retrieval is not a complete semantic duplicate audit.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path,
                        default=Path(__file__).resolve().parent / 'data/usmle-step1.db')
    parser.add_argument('--term', action='append', required=True)
    args = parser.parse_args()
    print(json.dumps(probe(args.db, args.term), ensure_ascii=False, indent=2))
