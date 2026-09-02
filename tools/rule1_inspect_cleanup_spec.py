#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, lzma
from collections import Counter
from pathlib import Path

PARTS=[Path(f'RULE1_CLEANUP_2000_SPEC.part{i}') for i in range(1,5)]
OUT=Path('RULE1_CLEANUP_2000_SPEC_INSPECTION.json')
SELECTED=[
 'V2-Q0712','V2-Q0719','V2-Q0970','V2-Q0972','V2-Q0984',
 'V2-Q0239','V2-Q1468','V2-Q0679','V2-Q1934','V2-Q1174','V2-Q1176',
 'V2-Q0886','V2-Q1038','V2-Q0653','V2-Q1387'
]

def sha256_bytes(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def main():
    meta=[]; chunks=[]
    for p in PARTS:
        if not p.exists(): raise SystemExit(f'BLOCKED missing {p}')
        raw=p.read_bytes(); text=raw.decode('ascii').strip()
        meta.append({'path':str(p),'bytes':len(raw),'sha256':sha256_bytes(raw),'ascii_chars':len(text)})
        chunks.append(text)
    packed=''.join(chunks)
    decoded=base64.b64decode(packed,validate=True)
    plain=lzma.decompress(decoded)
    spec=json.loads(plain.decode('utf-8'))
    if not isinstance(spec,dict): raise SystemExit('BLOCKED spec root')
    cue=spec.get('cueing'); rich=spec.get('rich')
    if not isinstance(cue,list) or not isinstance(rich,dict): raise SystemExit('BLOCKED spec schema')
    sem={}; duplicate_cue=[]
    for row in cue:
        if not isinstance(row,list) or len(row)!=6: raise SystemExit(f'BLOCKED cue row {row!r}')
        uid,a,b,c,d,correct=row
        if uid in sem: duplicate_cue.append(uid)
        v={'options':{'A':a,'B':b,'C':c,'D':d}}
        if correct is not None: v['correct_option']=correct
        sem[uid]=v
    overlap=[]
    for uid,v in rich.items():
        if uid in sem: overlap.append(uid); sem[uid].update(v)
        else: sem[uid]=v
    field_counts=Counter()
    for v in sem.values(): field_counts.update(v.keys())
    selected={uid:sem.get(uid) for uid in SELECTED}
    payload={
      'status':'SPEC_DECODED_READ_ONLY',
      'part_files':meta,
      'packed_ascii_chars':len(packed),
      'packed_sha256':sha256_bytes(packed.encode('ascii')),
      'decoded_lzma_bytes':len(decoded),
      'decompressed_json_bytes':len(plain),
      'decompressed_json_sha256':sha256_bytes(plain),
      'top_level_keys':sorted(spec.keys()),
      'cueing_row_count':len(cue),
      'cueing_unique_uid_count':len({r[0] for r in cue}),
      'cueing_duplicate_uid_count':len(duplicate_cue),
      'rich_uid_count':len(rich),
      'cueing_rich_overlap_uid_count':len(set(overlap)),
      'merged_semantic_uid_count':len(sem),
      'merged_semantic_field_counts':dict(sorted(field_counts.items())),
      'first_20_uids':sorted(sem)[:20],
      'last_20_uids':sorted(sem)[-20:],
      'selected_uid_payloads':selected,
      'warning':'Decoded spec presence/count is not proof of clinical review, source verification, correction validity, or FINAL_QA_PASS.'
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_SPEC_INSPECTION='+json.dumps({k:payload[k] for k in ['status','cueing_row_count','rich_uid_count','merged_semantic_uid_count','packed_sha256','decompressed_json_sha256']},separators=(',',':')))

if __name__=='__main__': main()
