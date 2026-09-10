#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,re,sqlite3,subprocess
from pathlib import Path
from datetime import datetime,timezone
import simulate_import_q1301_q1500 as s
import simulate_import_q1301_q1500_r4 as r4

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; PRE_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
SIM=ROOT/'audit'/'Q1301_Q1500_DETACHED_IMPORT_SIMULATION.json'; SIM_BLOB='8345601b959231227f227bf1d2b6ba4471edd5da'
INV=ROOT/'audit'/'Q1301_Q1500_CROSS_COLLISION_INVENTORY.json'; INV_BLOB='0e317344f0ddb87c8bf1a736a022fb5c4155a008'
STATE=ROOT/'state'/'step2_final_q0001_q1500.json'; AUDIT=ROOT/'audit'/'STEP2_FINAL_10_10_Q0001_Q1500.json'
CID_SUFFIX='20260910T100000Z'

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 if not m: raise SystemExit('bad candidate id '+str(cid))
 return int(m.group(1))

def load_all():
 if gitblob(DB)!=PRE_BLOB: raise SystemExit('production DB pre-blob mismatch')
 if gitblob(SIM)!=SIM_BLOB: raise SystemExit('detached simulation report blob mismatch')
 if gitblob(INV)!=INV_BLOB: raise SystemExit('collision inventory blob mismatch')
 sim=json.loads(SIM.read_text()); inv=json.loads(INV.read_text())
 if sim.get('status')!='DETACHED_IMPORT_SIMULATION_PASS' or sim.get('production_transactional_import_ready') is not True or sim.get('simulated_post_count')!=1500 or sim.get('failures')!=[]: raise SystemExit('simulation gate failure')
 if inv.get('pair_count')!=0 or inv.get('pairs')!=[]: raise SystemExit('collision gate failure')
 all_docs={}
 for a,b,bp,mp,mblob in r4.s.BATCHES:
  if gitblob(mp)!=mblob: raise SystemExit(mp.name+' manifest blob mismatch')
  m=json.loads(mp.read_text())
  if m.get('status')!='FINAL_QA_PASS' or m.get('final_qa_verdict')!='FINAL_QA_PASS_NO_MATERIAL_DEFECT' or m.get('production_import_ready') is not True or m.get('unresolved_defects')!=[] or m.get('authoritative_db_blob')!=PRE_BLOB or m.get('authoritative_db_final_count')!=1300: raise SystemExit(mp.name+' manifest gate')
  if gitblob(bp)!=m.get('candidate_batch_blob'): raise SystemExit(bp.name+' candidate binding')
  batch=json.loads(bp.read_text()); docs={int(x['num']):x for x in batch['items']}
  if set(docs)!=set(range(a,b+1)) or len(docs)!=m['item_count']: raise SystemExit(bp.name+' range/count')
  if ''.join(docs[n]['item']['intended_key'] for n in range(a,b+1))!=m['answer_key_sequence']: raise SystemExit(bp.name+' key sequence')
  for n,d in docs.items(): s.validate_doc(n,d)
  all_docs.update(docs)
 if set(all_docs)!=set(range(1301,1501)) or len(all_docs)!=200: raise SystemExit('incoming contiguity')
 return all_docs

def main():
 docs=load_all(); now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
 c=sqlite3.connect(DB)
 try:
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('pre-import integrity')
  old=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
  oldr=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall()
  if len(old)!=1300 or len(oldr)!=1300 or {qnum(x[0]) for x in old}!=set(range(1,1301)): raise SystemExit('pre-import count/contiguity')
  rm={x[0]:x for x in oldr}
  for cid,pj,ps,ash in old:
   if hobj(json.loads(pj))!=ps or cid not in rm or rm[cid][2]!=ash or rm[cid][3]!='FINAL_10_10_PASS': raise SystemExit(cid+' pre payload/review consistency')
  c.execute('BEGIN IMMEDIATE')
  for n in range(1301,1501):
   d=copy.deepcopy(docs[n]); cid=f'S1-DIRECT-{n:04d}-{CID_SUFFIX}'
   if c.execute('select 1 from step2_final_items where candidate_id=?',(cid,)).fetchone(): raise SystemExit(cid+' already exists')
   d['candidate_id']=cid
   d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','aggregate_import':'Q1301-Q1500-R4','authoritative_pre_db_blob':PRE_BLOB,'authoritative_pre_count':1300,'detached_simulation_blob':SIM_BLOB,'collision_inventory_blob':INV_BLOB,'imported_at':now,'unresolved_conflicts':0}
   review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':'Q1301-Q1500 R4 transactional production import','detached_simulation_blob':SIM_BLOB,'collision_inventory_blob':INV_BLOB,'reviewed_at':now}
   rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh; ph=hobj(d)
   c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS',now))
   c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS',now))
  c.execute('update step2_finalization set item_count=? where id=1',(1500,))
  # Verify inside transaction before commit.
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('post-import integrity before commit')
  rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
  rrows=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall()
  if len(rows)!=1500 or len(rrows)!=1500 or {qnum(x[0]) for x in rows}!=set(range(1,1501)): raise SystemExit('post-import count/contiguity before commit')
  rr={x[0]:x for x in rrows}
  for cid,pj,ps,ash in rows:
   if hobj(json.loads(pj))!=ps or cid not in rr or rr[cid][2]!=ash or rr[cid][3]!='FINAL_10_10_PASS': raise SystemExit(cid+' post payload/review consistency')
  c.commit()
 except BaseException:
  c.rollback(); c.close(); raise
 c.close()
 # Reopen independently after commit.
 v=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 integ=v.execute('pragma integrity_check').fetchone()[0]
 ni=v.execute("select count(*) from step2_final_items where final_status='FINAL_10_10_PASS'").fetchone()[0]
 nr=v.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]
 ids=[x[0] for x in v.execute("select candidate_id from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()]; v.close()
 nums={qnum(x) for x in ids}
 if integ!='ok' or ni!=1500 or nr!=1500 or nums!=set(range(1,1501)): raise SystemExit('independent post-commit verification failure')
 post=gitblob(DB)
 state={'audit_id':'STEP2-FINAL-Q0001-Q1500-20260910','item_count':1500,'step2_final_review_count':1500,'contiguous_q0001_q1500':True,'q1301_q1500_present_exactly_once':True,'sqlite_integrity':'ok','pre_db_blob':PRE_BLOB,'post_db_blob':post,'imported_range':'Q1301-Q1500','imported_count':200,'detached_simulation_blob':SIM_BLOB,'collision_inventory_blob':INV_BLOB,'production_import_status':'PASS','verified_at':now}
 STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
 audit={'audit_id':'STEP2-FINAL-10-10-Q0001-Q1500-20260910','status':'FINAL_10_10_PASS','final_count':1500,'reviews':1500,'range_imported':'Q1301-Q1500','transactional_import':'PASS','independent_post_commit_verification':'PASS','sqlite_integrity':'ok','contiguous_q0001_q1500':True,'pre_db_blob':PRE_BLOB,'post_db_blob':post,'detached_simulation_blob':SIM_BLOB,'collision_inventory_blob':INV_BLOB,'unresolved_defects':[],'production_db_modified':True}
 AUDIT.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'PRODUCTION_IMPORT_PASS','pre_count':1300,'post_count':1500,'post_db_blob':post,'integrity':integ},sort_keys=True))

if __name__=='__main__': main()
