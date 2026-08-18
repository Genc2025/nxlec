#!/usr/bin/env python3
"""Temporary staging dispatcher for RULE1 2000 cleanup evidence.

This branch-only version is intentionally READ-ONLY. It runs the technical
candidate scan against the pinned canonical blob and bundles the evidence into
RULE1_CLEANUP_2000_RESULT.json so the existing PR workflow can materialize it.
It MUST be replaced by the original atomic apply script before any cleanup DB
write is allowed.
"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

SUMMARY=Path('RULE1_CLEANUP_2000_SCAN_SUMMARY.json')
CANDIDATES=Path('RULE1_CLEANUP_2000_CANDIDATES.jsonl')
NEARDUPS=Path('RULE1_CLEANUP_2000_NEAR_DUPLICATES.jsonl')
LOCATORS=Path('RULE1_CLEANUP_2000_LOCATOR_CANDIDATES.jsonl')
OUT=Path('RULE1_CLEANUP_2000_RESULT.json')

def load_jsonl(path: Path):
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def main():
    subprocess.check_call(['python3','tools/rule1_cleanup_candidate_scan.py'])
    bundle={
      'mode':'READ_ONLY_STAGING_EVIDENCE',
      'database_modified':False,
      'summary':json.loads(SUMMARY.read_text(encoding='utf-8')),
      'candidates':load_jsonl(CANDIDATES),
      'near_duplicate_pairs':load_jsonl(NEARDUPS),
      'locator_candidates':load_jsonl(LOCATORS),
      'warning':'This file is candidate evidence only. No UID is clinically corrected or FINAL_QA re-approved by this scan.'
    }
    OUT.write_text(json.dumps(bundle,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_CLEANUP_RESULT='+json.dumps({'mode':bundle['mode'],'database_modified':False,'technical_candidate_uid_count':bundle['summary']['technical_candidate_uid_count'],'semantic_near_duplicate_pair_candidates':bundle['summary']['semantic_near_duplicate_pair_candidates']},separators=(',',':')))

if __name__=='__main__': main()
