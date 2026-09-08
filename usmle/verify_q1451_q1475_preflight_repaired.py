#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import verify_q1451_q1475_preflight as v

ROOT=Path(__file__).resolve().parent
v.CAND=ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json'
v.OUT=ROOT/'audit'/'Q1451_Q1475_DETERMINISTIC_PREFLIGHT_REPAIRED.json'
v.EXPECTED_CAND_BLOB='5b32187ea11d09aa147a421f4b8099e06a7d7632'

v.main()

# If and only if the complete inherited preflight passed, add explicit repair provenance.
out=json.loads(v.OUT.read_text())
assert out['verdict']=='DETERMINISTIC_PREFLIGHT_PASS' and out['failures']==[]
out['audit_id']='Q1451-Q1475-DETERMINISTIC-PREFLIGHT-REPAIRED-20260908'
out['repair_provenance']={
    'blocked_candidate_git_blob':'1fb2d5ea9dd1b687555c6fbbe82281bb4476b9d0',
    'repaired_candidate_git_blob':'5b32187ea11d09aa147a421f4b8099e06a7d7632',
    'replaced_items':[1454,1460,1473],
    'reason':'First full preflight detected prior-workstream Jaccard collisions; constructs were replaced and the complete preflight restarted from zero.'
}
v.OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'REPAIRED_DETERMINISTIC_PREFLIGHT_PASS','candidate_blob':v.EXPECTED_CAND_BLOB,'failures':0},sort_keys=True))
