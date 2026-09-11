#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, sqlite3, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
INP=REPO/'usmle/audit/FULL_CANONICAL_Q0001_Q1535_COMPLIANCE.json'
OUT=REPO/'usmle/audit/FULL_CANONICAL_Q0001_Q1535_SIMILARITY_REVIEW_PACKET.json'
DB_BLOB=os.environ['DB_BLOB']

def gitblob(p):
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()

def qnum(cid):
    m=re.search(r'DIRECT-(\d{4})',cid or '')
    return int(m.group(1)) if m else None

def compact(p):
    it=p.get('item') if isinstance(p.get('item'),dict) else {}
    ex=p.get('explanation') if isinstance(p.get('explanation'),dict) else {}
    bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
    return {
      'drug':p.get('drug'),
      'system':bp.get('primary_system'),
      'disciplines':bp.get('disciplines'),
      'vignette':it.get('vignette'),
      'lead_in':it.get('lead_in'),
      'options':it.get('options'),
      'key':it.get('intended_key'),
      'tested_construct':it.get('tested_construct'),
      'key_explanation':ex.get('key_explanation'),
      'educational_objective':ex.get('educational_objective')
    }

def main():
    assert gitblob(DB)==DB_BLOB
    a=json.loads(INP.read_text())
    pairs=a['duplicate_analysis']['top_similarity_pairs_ge_0_45']
    ids={x['candidate_id_1'] for x in pairs}|{x['candidate_id_2'] for x in pairs}
    c=sqlite3.connect(DB)
    qmarks=','.join('?' for _ in ids)
    rows=c.execute(f"select candidate_id,payload_json from step2_final_items where candidate_id in ({qmarks})",tuple(sorted(ids))).fetchall()
    c.close()
    docs={cid:json.loads(pj) for cid,pj in rows}
    packet=[]
    for x in pairs:
        a1=x['candidate_id_1']; a2=x['candidate_id_2']
        packet.append({
          'q1':x['q1'],'q2':x['q2'],'jaccard':x['jaccard'],
          'candidate_id_1':a1,'candidate_id_2':a2,
          'item1':compact(docs[a1]),'item2':compact(docs[a2])
        })
    OUT.write_text(json.dumps({'audit_id':'FULL-CANONICAL-Q0001-Q1535-SIMILARITY-REVIEW-PACKET-20260911','db_blob':DB_BLOB,'pair_count':len(packet),'pairs':packet},indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'pair_count':len(packet),'items_exported':len(ids)},sort_keys=True))
if __name__=='__main__': main()
