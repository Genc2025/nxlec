#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sqlite3
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
DB = ROOT / 'data' / 'usmle-step1.db'
BATCHES = [
    ROOT / 'batch_specs_1401_1500' / '01_q1401_q1425_author_20260908_schema_repaired.json',
    ROOT / 'batch_specs_1401_1500' / '02_q1426_q1450_author_20260908_schema_repaired.json',
]
EXPECTED_BLOBS = {
    BATCHES[0].name: 'd55741f411f11a9b3d7b05d5e9b057ab1e4b9fa5',
    BATCHES[1].name: 'bf75639d0d0725fb37f5c1eef588d5efda3930a3',
}
EXPECTED_DB_BLOB = '1a0f0b702f86a57624161413ba60fa4ce88e8d97'
EXPECTED_CANONICAL_COUNT = 1300
USMLE = 'https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'
OUT = ROOT / 'audit' / 'Q1401_Q1450_DETERMINISTIC_PREFLIGHT.json'

ALLOWED_DISCIPLINES = {
    'Pathology', 'Physiology', 'Nutrition', 'Gross Anatomy & Embryology',
    'Microbiology', 'Pharmacology', 'Behavioral Sciences', 'Biochemistry',
    'Histology & Cell Biology', 'Immunology', 'Genetics'
}
ALLOWED_SOURCE_HOSTS = {
    'dailymed.nlm.nih.gov', 'www.accessdata.fda.gov', 'accessdata.fda.gov',
    'www.fda.gov', 'fda.gov', 'www.usmle.org', 'usmle.org',
    'pubmed.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov'
}
STOP = set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder drug treatment therapy cells cell receptor protein enzyme mechanism action'.split())


def gitblob(path: Path) -> str:
    return subprocess.check_output(
        ['git', '-C', str(REPO), 'hash-object', str(path.relative_to(REPO))], text=True
    ).strip()


def norm(s: str) -> str:
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', s.casefold().replace('β', 'beta').replace('α', 'alpha')).split())


def toks(s: str) -> set[str]:
    return {w for w in norm(s).split() if len(w) > 2 and w not in STOP}


def item_text(x: dict) -> str:
    it = x['item']
    return ' '.join([it.get('vignette', ''), it.get('lead_in', ''), it.get('tested_construct', ''), *it.get('options', {}).values()])


def canonical_text(payload_json: str) -> str:
    d = json.loads(payload_json)
    it = d.get('item', d)
    ex = d.get('explanation', {})
    return ' '.join([
        it.get('vignette', ''), it.get('lead_in', ''), it.get('tested_construct', ''),
        *it.get('options', {}).values(), ex.get('key_explanation', ''),
        ex.get('educational_objective', ''), *ex.get('distractor_explanations', {}).values()
    ])


def jaccard(a: str, b: str) -> float:
    A, B = toks(a), toks(b)
    return len(A & B) / len(A | B) if A | B else 0.0


def seq(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b), autojunk=True).ratio()


def fetch_retry(url: str, tries: int = 5) -> bytes:
    err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36'
            })
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            err = e
            if e.code not in {429, 500, 502, 503, 504}:
                raise
        except (urllib.error.URLError, TimeoutError) as e:
            err = e
        time.sleep(min(15, 2 ** attempt))
    raise err


def htmltext(raw: bytes) -> str:
    return ' '.join(re.sub(r'<[^>]+>', ' ', html.unescape(raw.decode('utf-8', 'ignore'))).split())


def source_binding_ok(source: dict, page_text: str) -> tuple[bool, dict]:
    title_tokens = toks(source.get('title', ''))
    actual = toks(page_text)
    title_overlap = len(title_tokens & actual)
    title_need = max(2, min(5, max(1, len(title_tokens) // 2)))

    setid = source.get('setid')
    setid_ok = True
    if setid:
        setid_ok = setid.casefold() in page_text.casefold() or setid.casefold() in source.get('url', '').casefold()

    locator = source.get('section_locator', '')
    locator_ok = bool(locator.strip())
    # For DailyMed/FDA labels, require mechanism/description section terminology to be represented when cited.
    if '12.1' in locator:
        locator_ok = locator_ok and ('Mechanism of Action' in page_text or 'MECHANISM OF ACTION' in page_text.upper())
    if '12.4' in locator:
        locator_ok = locator_ok and ('Microbiology' in page_text or 'MICROBIOLOGY' in page_text.upper())

    return title_overlap >= title_need and setid_ok and locator_ok, {
        'title_token_overlap': title_overlap,
        'title_token_minimum': title_need,
        'setid_ok': setid_ok,
        'locator_ok': locator_ok,
    }


def main() -> None:
    assert gitblob(DB) == EXPECTED_DB_BLOB, (gitblob(DB), EXPECTED_DB_BLOB)
    for p in BATCHES:
        assert gitblob(p) == EXPECTED_BLOBS[p.name], (p.name, gitblob(p), EXPECTED_BLOBS[p.name])

    con = sqlite3.connect(DB.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    rows = con.execute("SELECT candidate_id,payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    review_count = con.execute("SELECT count(*) FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]
    con.close()
    assert len(rows) == review_count == EXPECTED_CANONICAL_COUNT, (len(rows), review_count)
    canonical = [(cid, canonical_text(pj)) for cid, pj in rows]

    usmle_text = htmltext(fetch_retry(USMLE))
    for d in sorted(ALLOWED_DISCIPLINES):
        assert d in usmle_text, ('current USMLE discipline label missing', d)

    batches = [json.loads(p.read_text()) for p in BATCHES]
    all_items = []
    source_cache: dict[str, str] = {}
    source_reports = []
    item_reports = []

    expected_ranges = [list(range(1401, 1426)), list(range(1426, 1451))]
    for b, nums in zip(batches, expected_ranges):
        items = b['items']
        assert [x['num'] for x in items] == nums
        assert b['candidate_count'] == 25
        assert b['canonical_count_before'] == b['canonical_count_after'] == EXPECTED_CANONICAL_COUNT
        assert b['production_import_ready'] is False
        assert b['answer_key_sequence'] == 'ABCDEABCDEABCDEABCDEABCDE'
        assert b['answer_key_distribution'] == {'A': 5, 'B': 5, 'C': 5, 'D': 5, 'E': 5}
        assert b.get('schema_repair', {}).get('medical_content_changed') is False
        assert b.get('schema_repair', {}).get('intended_keys_changed') is False

        for x in items:
            q = x['num']; it = x['item']; bp = x['blueprint']; ex = x['explanation']; ev = x['evidence_map']; src = x['sources']
            fail = []

            if bp['primary_system'] not in usmle_text:
                fail.append('system_label')
            if bp['primary_competency'] not in usmle_text:
                fail.append('competency_label')
            if bp.get('official_outline_path') != [bp['primary_system']]:
                fail.append('outline_path')
            if not set(bp.get('disciplines', [])).issubset(ALLOWED_DISCIPLINES):
                fail.append('discipline_enum')
            if any(d not in usmle_text for d in bp.get('disciplines', [])):
                fail.append('discipline_currentness')
            if 'ncjmm' in json.dumps(x).casefold() and bp.get('ncjmm') not in {False, None}:
                fail.append('ncjmm')

            if list(it.get('options', {})) != list('ABCDE'):
                fail.append('options_labels')
            if len(set(norm(v) for v in it.get('options', {}).values())) != 5:
                fail.append('options_unique')
            key = it.get('intended_key')
            if key not in 'ABCDE':
                fail.append('key')
            if not it.get('vignette', '').strip() or not it.get('lead_in', '').strip().endswith('?'):
                fail.append('stem_leadin')
            de = ex.get('distractor_explanations', {})
            if set(de) != set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'):
                fail.append('rationale_eo')

            if not isinstance(ev, list) or len(ev) != 5:
                fail.append('evidence_map_shape')
                em = {}
            else:
                em = {e.get('option'): e for e in ev}
                if set(em) != set('ABCDE'):
                    fail.append('evidence_map_options')
            ids = {s.get('source_id') for s in src}
            if em:
                for L in 'ABCDE':
                    e = em[L]
                    if e.get('claim') != de.get(L):
                        fail.append('evidence_rationale_binding')
                    if e.get('direct_or_inference') != ('direct' if L == key else 'inference'):
                        fail.append('evidence_class')
                    if not set(e.get('source_ids', [])).issubset(ids):
                        fail.append('evidence_source_ids')
                    if not e.get('source_locator'):
                        fail.append('evidence_locator')

            for s in src:
                u = urlparse(s.get('url', ''))
                if u.scheme != 'https' or u.netloc not in ALLOWED_SOURCE_HOSTS:
                    fail.append('source_domain')
                    continue
                if not s.get('section_locator') or not s.get('retrieved_at'):
                    fail.append('source_metadata')
                if s.get('retrieved_at') != '2026-09-08':
                    fail.append('source_retrieval_date')
                url = s['url']
                if url not in source_cache:
                    source_cache[url] = htmltext(fetch_retry(url))
                ok, detail = source_binding_ok(s, source_cache[url])
                source_reports.append({'q': q, 'source_id': s.get('source_id'), 'url': url, 'status': 'PASS' if ok else 'BLOCKED', **detail})
                if not ok:
                    fail.append('live_source_binding')

            text = item_text(x)
            scored = []
            for cid, ct in canonical:
                j, s = jaccard(text, ct), seq(text, ct)
                scored.append((max(j, s), j, s, cid))
            scored.sort(reverse=True)
            maxj = max(z[1] for z in scored)
            maxs = max(z[2] for z in scored)
            if maxj >= 0.45:
                fail.append('canonical_jaccard_collision')
            if maxs >= 0.70:
                fail.append('canonical_sequence_collision')

            item_reports.append({
                'q': q,
                'status': 'PASS' if not fail else 'BLOCKED',
                'failures': sorted(set(fail)),
                'key': key,
                'evidence_contract': 'PASS' if not any(f.startswith('evidence_') for f in fail) else 'BLOCKED',
                'source_live_binding': 'PASS' if 'live_source_binding' not in fail else 'BLOCKED',
                'blueprint': 'PASS' if not any(f in fail for f in ['system_label','competency_label','outline_path','discipline_enum','discipline_currentness']) else 'BLOCKED',
                'ncjmm': 'NOT_APPLICABLE_USMLE',
                'canonical_duplicate_gate': {
                    'status': 'PASS' if not any('collision' in f for f in fail) else 'BLOCKED',
                    'max_jaccard': round(maxj, 5),
                    'max_sequence': round(maxs, 5),
                    'top5': [{'candidate_id': z[3], 'jaccard': round(z[1], 5), 'sequence': round(z[2], 5)} for z in scored[:5]],
                },
            })
            all_items.append(x)

    # Intra-new-workstream collision gate across all repaired Q1401-Q1450 items.
    intra = []
    global_fail = []
    for i, a in enumerate(all_items):
        for b in all_items[i+1:]:
            j, s = jaccard(item_text(a), item_text(b)), seq(item_text(a), item_text(b))
            intra.append((max(j, s), j, s, a['num'], b['num']))
            if j >= 0.40 or s >= 0.65:
                global_fail.append(f"INTRABATCH:{a['num']}-{b['num']}")
    intra.sort(reverse=True)
    for r in item_reports:
        global_fail.extend(f"Q{r['q']}:{f}" for f in r['failures'])
    if any(s['status'] != 'PASS' for s in source_reports):
        global_fail.append('SOURCE_REPORT_BLOCKED')

    out = {
        'audit_id': 'Q1401-Q1450-DETERMINISTIC-PREFLIGHT-20260908',
        'scope': 'Deterministic repaired-candidate preflight. This is not blind Auditor A or Auditor B and is not production acceptance evidence.',
        'canonical_db_blob': EXPECTED_DB_BLOB,
        'canonical_count': EXPECTED_CANONICAL_COUNT,
        'canonical_review_count': review_count,
        'candidate_files': [
            {'path': str(p.relative_to(REPO)), 'git_blob': EXPECTED_BLOBS[p.name]} for p in BATCHES
        ],
        'candidate_count': len(all_items),
        'item_range': 'Q1401-Q1450',
        'answer_distribution': dict(Counter(x['item']['intended_key'] for x in all_items)),
        'schema_repair_materialized': True,
        'per_source_sha_required_by_current_importer': False,
        'live_source_reverification_performed': True,
        'current_usmle_blueprint_reverification_performed': True,
        'item_reports': item_reports,
        'source_reports': source_reports,
        'intrabatch_top10': [
            {'q1': q1, 'q2': q2, 'jaccard': round(j, 5), 'sequence': round(s, 5)}
            for _, j, s, q1, q2 in intra[:10]
        ],
        'failures': sorted(set(global_fail)),
        'verdict': 'DETERMINISTIC_PREFLIGHT_PASS' if not global_fail else 'BLOCKED',
        'independent_auditor_a_complete': False,
        'independent_auditor_b_complete': False,
        'production_import_ready': False,
        'production_db_modified': False,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({
        'verdict': out['verdict'],
        'candidate_count': len(all_items),
        'failures': out['failures'],
        'max_canonical_jaccard': max(r['canonical_duplicate_gate']['max_jaccard'] for r in item_reports),
        'max_canonical_sequence': max(r['canonical_duplicate_gate']['max_sequence'] for r in item_reports),
        'max_intrabatch_jaccard': round(max(z[1] for z in intra), 5),
        'max_intrabatch_sequence': round(max(z[2] for z in intra), 5),
        'source_checks': len(source_reports),
    }, ensure_ascii=False, sort_keys=True))
    if global_fail:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
