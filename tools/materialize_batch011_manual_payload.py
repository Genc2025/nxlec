#!/usr/bin/env python3
from __future__ import annotations
import base64, gzip, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
PARTS=sorted(DATA.glob('batch011_manual_payload.json.gz.b64.part*'))
OVERRIDE=DATA/'clinical_overrides_zzz_rule1_batch011_chronological_q0501_q0550_20260815.json'
EVIDENCE=DATA/'rule1_batch011_chronological_reaudit_evidence_q0501_q0550.json'
IDS=[f'V2-Q{i:04d}' for i in range(501,551)]
if not PARTS:
    raise SystemExit('Batch011 payload parts missing')
raw=gzip.decompress(base64.b64decode(''.join(p.read_text(encoding='ascii').strip() for p in PARTS)))
doc=json.loads(raw.decode('utf-8'))
ov=doc.get('override'); ev=doc.get('evidence')
if not isinstance(ov,dict) or not isinstance(ev,dict):
    raise SystemExit('Batch011 payload missing override/evidence')
if ov.get('semantic_decisions_by_script') is not False:
    raise SystemExit('Batch011 semantic_decisions_by_script must be false')
if [x.get('question_uid') for x in ov.get('questions',[])] != IDS:
    raise SystemExit('Batch011 override scope/order mismatch')
if [x.get('id') for x in ev.get('items',[])] != IDS:
    raise SystemExit('Batch011 evidence scope/order mismatch')
if len(ov['questions'])!=50 or len(ev['items'])!=50:
    raise SystemExit('Batch011 payload must contain exactly 50 items')
# Technical-only QC normalization required by build_nclex_master.py.
# These measurements do not make semantic/clinical decisions.
for q in ov['questions']:
    opts=json.loads(q['item_data_json'])['options']
    key=json.loads(q['correct_answer_json'])['correct_option']
    lengths={k:len(str(opts[k]).strip()) for k in 'ABCD'}
    ordered=sorted('ABCD', key=lambda k:(lengths[k],k))
    qc=dict(q.get('qc') or {})
    qc.update({
        'question_uid':q['question_uid'],
        'lengths_json':json.dumps(lengths,separators=(',',':')),
        'min_chars':min(lengths.values()),
        'max_chars':max(lengths.values()),
        'max_min_ratio':round(max(lengths.values())/max(min(lengths.values()),1),4),
        'correct_option':key,
        'correct_length_rank':ordered.index(key)+1,
        'correct_is_extreme':int(lengths[key] in (min(lengths.values()),max(lengths.values()))),
        'qc_status':'MEASURED_NOT_GATE',
        'qc_note':'Length metrics are measurement only; semantic option/cue/ambiguity decisions are manual.'
    })
    q['qc']=qc
OVERRIDE.write_text(json.dumps(ov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
EVIDENCE.write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('BATCH011_MANUAL_PAYLOAD_MATERIALIZED items=50 override=50 evidence=50 semantic_script_decisions=0 qc_measurement_normalized=50')
