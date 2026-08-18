#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, lzma, sqlite3, subprocess
from pathlib import Path

SOURCE=Path('NCLEX_COMMERCIAL_MASTER_CURRENT.db')
CANON=Path('NCLEX_CANONICAL.db')
PARTS=[Path(f'RULE1_CLEANUP_2000_SPEC.part{i}') for i in range(1,5)]
OUT=Path('RULE1_CLEANUP_2000_EVIDENCE_REFRESH.json')

def inspect_db(path: Path):
    con=sqlite3.connect(f'file:{path}?mode=ro',uri=True); con.row_factory=sqlite3.Row
    out={
      'integrity':con.execute('PRAGMA integrity_check').fetchone()[0],
      'questions':con.execute('SELECT COUNT(*) FROM questions').fetchone()[0],
      'duplicate_uid_groups':con.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) n FROM questions GROUP BY question_uid HAVING n>1)').fetchone()[0],
      'tables':[r['name'] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")],
      'question_columns':[r['name'] for r in con.execute('PRAGMA table_info(questions)')]
    }
    con.close(); return out

def main():
    source_blob=subprocess.check_output(['git','rev-parse',f'HEAD:{SOURCE}'],text=True).strip()
    canon_blob=subprocess.check_output(['git','rev-parse',f'HEAD:{CANON}'],text=True).strip()
    s=inspect_db(SOURCE); c=inspect_db(CANON)
    scon=sqlite3.connect(f'file:{SOURCE}?mode=ro',uri=True); scon.row_factory=sqlite3.Row
    ccon=sqlite3.connect(f'file:{CANON}?mode=ro',uri=True); ccon.row_factory=sqlite3.Row
    cuids={r['question_uid'] for r in ccon.execute('SELECT question_uid FROM questions')}
    v2=list(scon.execute("SELECT question_uid,stable_sort_key FROM questions WHERE source_bank='v2' ORDER BY stable_sort_key,question_uid"))
    missing=[dict(r) for r in v2 if r['question_uid'] not in cuids]
    v2canon=ccon.execute("SELECT COUNT(*) FROM questions WHERE source_bank='v2'").fetchone()[0]
    scon.close(); ccon.close()

    meta=[]; chunks=[]
    for p in PARTS:
        if not p.exists(): raise SystemExit(f'BLOCKED missing {p}')
        raw=p.read_bytes(); text=raw.decode('ascii').strip()
        meta.append({'path':str(p),'bytes':len(raw),'blob':subprocess.check_output(['git','rev-parse',f'HEAD:{p}'],text=True).strip(),'sha256':hashlib.sha256(raw).hexdigest()})
        chunks.append(text)
    packed=''.join(chunks)
    decoded=base64.b64decode(packed,validate=True)
    plain=lzma.decompress(decoded)
    spec=json.loads(plain.decode('utf-8'))
    cue=spec.get('cueing'); rich=spec.get('rich')
    if not isinstance(cue,list) or not isinstance(rich,dict): raise SystemExit('BLOCKED spec schema')
    merged={}
    for row in cue:
        if not isinstance(row,list) or len(row)!=6: raise SystemExit('BLOCKED cue row schema')
        uid,a,b,c1,d,correct=row
        merged[uid]={'options':{'A':a,'B':b,'C':c1,'D':d},**({'correct_option':correct} if correct is not None else {})}
    for uid,v in rich.items(): merged.setdefault(uid,{}).update(v)
    selected={uid:merged.get(uid) for uid in ['V2-Q0712','V2-Q0719','V2-Q0970','V2-Q0972','V2-Q0984']}
    payload={
      'status':'READ_ONLY_EVIDENCE_REFRESH_COMPLETE',
      'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'branch':'rule1-cleanup-2000',
      'source_blob':source_blob,'canonical_blob':canon_blob,
      'source_sqlite':s,'canonical_sqlite':c,
      'v2_source_count':len(v2),'v2_canonical_count':v2canon,
      'v2_source_minus_canonical_count':len(missing),'first_v2_source_minus_canonical':missing[0] if missing else None,
      'spec_parts':meta,
      'spec_packed_sha256':hashlib.sha256(packed.encode('ascii')).hexdigest(),
      'spec_decompressed_sha256':hashlib.sha256(plain).hexdigest(),
      'spec_top_level_keys':sorted(spec.keys()),
      'cueing_row_count':len(cue),
      'cueing_unique_uid_count':len({r[0] for r in cue}),
      'rich_uid_count':len(rich),
      'merged_semantic_uid_count':len(merged),
      'selected_locator_uid_proposals':selected,
      'warning':'Spec counts/proposals are materialized evidence of payload existence only; they are not proof of clinical review or FINAL_QA_PASS.'
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_EVIDENCE_REFRESH='+json.dumps({k:payload[k] for k in ['source_blob','canonical_blob','v2_source_minus_canonical_count','cueing_row_count','rich_uid_count','merged_semantic_uid_count']},separators=(',',':')))

if __name__=='__main__': main()
