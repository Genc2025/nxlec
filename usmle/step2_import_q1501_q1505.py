#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,os,re,shutil,sqlite3,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
PRE_DB_BLOB='3ed79b65e3422fa8d9649ba7870185fbf0a07e9c'
CAND=ROOT/'batch_specs_1501_1600'/'01_q1501_q1505_author_20260910.json'; CAND_BLOB='934773fbd826484dea8c9917c4c763a2891871d9'
MAN=ROOT/'audit'/'Q1501_Q1505_FINAL_QA_PASS.json'; MAN_BLOB='c7c105fdfbafcf274bd55f0e7df0718057d6584c'
SIM=ROOT/'audit'/'Q1501_Q1505_DETACHED_IMPORT_SIMULATION.json'; SIM_BLOB='52495430b9c57315cbfcc8887b0e5654ef67d843'
POST=ROOT/'audit'/'Q1501_Q1505_PRODUCTION_IMPORT_VERIFY.json'
STATE=ROOT/'state'/'step2_final_q0001_q1505.json'

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 if not m: raise RuntimeError('bad candidate id '+str(cid))
 return int(m.group(1))
def verify_db(path,expect_count,expect_max):
 c=sqlite3.connect(path)
 integ=c.execute('pragma integrity_check').fetchone()[0]
 rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
 revs=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall()
 fin=c.execute('select item_count from step2_finalization where id=1').fetchone(); c.close()
 if integ!='ok' or len(rows)!=expect_count or len(revs)!=expect_count or not fin or fin[0]!=expect_count: raise RuntimeError('DB count/integrity/finalization')
 nums={qnum(x[0]) for x in rows}
 if nums!=set(range(1,expect_max+1)): raise RuntimeError('DB contiguity')
 rm={x[0]:x for x in revs}
 for cid,pj,ps,ash in rows:
  if hobj(json.loads(pj))!=ps or cid not in rm or rm[cid][2]!=ash or rm[cid][3]!='FINAL_10_10_PASS': raise RuntimeError(cid+' payload/review consistency')
 return rows,revs

def main():
 if gitblob(DB)!=PRE_DB_BLOB: raise SystemExit('pre DB blob changed')
 if gitblob(CAND)!=CAND_BLOB or gitblob(MAN)!=MAN_BLOB or gitblob(SIM)!=SIM_BLOB: raise SystemExit('evidence blob changed')
 m=json.loads(MAN.read_text()); s=json.loads(SIM.read_text()); b=json.loads(CAND.read_text())
 if not (m['status']=='FINAL_QA_PASS' and m['final_qa_verdict']=='FINAL_QA_PASS_NO_MATERIAL_DEFECT' and m['production_import_ready'] is True and m['unresolved_defects']==[] and m['candidate_batch_blob']==CAND_BLOB and m['authoritative_db_blob']==PRE_DB_BLOB): raise SystemExit('manifest gate')
 if not (s['status']=='DETACHED_IMPORT_SIMULATION_PASS' and s['production_transactional_import_ready'] is True and s['failures']==[] and s['candidate_blob']==CAND_BLOB and s['final_qa_manifest_blob']==MAN_BLOB and s['production_pre_db_blob']==PRE_DB_BLOB and s['simulated_post_count']==1505): raise SystemExit('simulation gate')
 docs={int(x['num']):x for x in b['items']}
 if set(docs)!=set(range(1501,1506)) or ''.join(docs[n]['item']['intended_key'] for n in range(1501,1506))!='ABCDE': raise SystemExit('candidate scope')
 verify_db(DB,1500,1500)
 with tempfile.TemporaryDirectory() as td:
  work=Path(td)/'usmle-step1-q1505.db'; shutil.copy2(DB,work); c=sqlite3.connect(work)
  try:
   c.execute('BEGIN IMMEDIATE')
   for n in range(1501,1506):
    d=copy.deepcopy(docs[n]); cid=f'S1-DIRECT-{n:04d}-20260910T204600Z'; d['candidate_id']=cid
    d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','production_import_scope':'Q1501-Q1505','authoritative_pre_db_blob':PRE_DB_BLOB,'authoritative_pre_count':1500,'final_qa_manifest_blob':MAN_BLOB,'detached_simulation_blob':SIM_BLOB}
    review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':'Q1501-Q1505 production transactional import V3'}
    rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh; ph=hobj(d)
    c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS','2026-09-10T20:46:00Z'))
    c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS','2026-09-10T20:46:00Z'))
   c.execute('update step2_finalization set item_count=? where id=1',(1505,)); c.commit()
  except Exception:
   c.rollback(); c.close(); raise
  c.close()
  verify_db(work,1505,1505)
  shutil.copy2(work,DB)
 post_blob=gitblob(DB)
 verify_db(DB,1505,1505)
 post={'audit_id':'Q1501-Q1505-PRODUCTION-IMPORT-VERIFY-20260910','status':'PRODUCTION_IMPORT_PASS','imported_range':'Q1501-Q1505','imported_count':5,'pre_db_blob':PRE_DB_BLOB,'post_db_blob':post_blob,'candidate_blob':CAND_BLOB,'final_qa_manifest_blob':MAN_BLOB,'detached_simulation_blob':SIM_BLOB,'item_count':1505,'review_count':1505,'contiguous_q0001_q1505':True,'sqlite_integrity':'ok','payload_review_consistency':'PASS','q1501_q1505_present_exactly_once':True,'production_import_status':'PASS','failures':[]}
 state={'audit_id':'STEP2-FINAL-Q0001-Q1505-20260910','item_count':1505,'step2_final_review_count':1505,'contiguous_q0001_q1505':True,'q1501_q1505_present_exactly_once':True,'sqlite_integrity':'ok','pre_db_blob':PRE_DB_BLOB,'post_db_blob':post_blob,'imported_range':'Q1501-Q1505','imported_count':5,'detached_simulation_blob':SIM_BLOB,'final_qa_manifest_blob':MAN_BLOB,'production_import_status':'PASS','verified_at':'2026-09-10T20:46:00Z'}
 POST.write_text(json.dumps(post,indent=2,ensure_ascii=False)+'\n'); STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(post,sort_keys=True))
if __name__=='__main__': main()
