#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,os,re,shutil,sqlite3,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'
START=int(os.environ['START_Q']); END=int(os.environ['END_Q']); PRE=int(os.environ['PRE_COUNT']); POST=END
DB_BLOB=os.environ['DB_BLOB']; CAND=REPO/os.environ['CAND_PATH']; CAND_BLOB=os.environ['CAND_BLOB']; MAN=REPO/os.environ['MAN_PATH']; MAN_BLOB=os.environ['MAN_BLOB']; SIM=REPO/os.environ['SIM_PATH']; SIM_BLOB=os.environ['SIM_BLOB']; VERIFY=REPO/os.environ['VERIFY_OUT']; STATE=REPO/os.environ['STATE_OUT']
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 if not m: raise RuntimeError('bad candidate id '+str(cid))
 return int(m.group(1))
def verify(path,count,maxq):
 c=sqlite3.connect(path); integ=c.execute('pragma integrity_check').fetchone()[0]
 rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); rev=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall(); fin=c.execute('select item_count from step2_finalization where id=1').fetchone(); c.close()
 if integ!='ok' or len(rows)!=len(rev) or len(rows)!=count or not fin or fin[0]!=count or {qnum(x[0]) for x in rows}!=set(range(1,maxq+1)): raise RuntimeError('DB integrity/count/contiguity')
 rm={x[0]:x for x in rev}
 for cid,pj,ps,ash in rows:
  if hobj(json.loads(pj))!=ps or cid not in rm or rm[cid][2]!=ash or rm[cid][3]!='FINAL_10_10_PASS': raise RuntimeError(cid+' payload/review consistency')
 return True
def main():
 assert END-START+1==5 and START==PRE+1 and POST==PRE+5
 assert gitblob(DB)==DB_BLOB and gitblob(CAND)==CAND_BLOB and gitblob(MAN)==MAN_BLOB and gitblob(SIM)==SIM_BLOB
 m=json.loads(MAN.read_text()); s=json.loads(SIM.read_text()); b=json.loads(CAND.read_text())
 assert m['status']=='FINAL_QA_PASS' and m['final_qa_verdict']=='FINAL_QA_PASS_NO_MATERIAL_DEFECT' and m['production_import_ready'] is True and m['unresolved_defects']==[] and m['suggested_changes']==[] and m['candidate_batch_blob']==CAND_BLOB and m['authoritative_db_blob']==DB_BLOB and m['authoritative_db_final_count']==PRE and m['authoritative_review_count']==PRE
 assert s['status']=='DETACHED_IMPORT_SIMULATION_PASS' and s['production_transactional_import_ready'] is True and s['failures']==[] and s['candidate_blob']==CAND_BLOB and s['final_qa_manifest_blob']==MAN_BLOB and s['production_pre_db_blob']==DB_BLOB and s['pre_production_count']==PRE and s['simulated_post_count']==POST
 docs={x['num']:x for x in b['items']}; assert set(docs)==set(range(START,END+1)); assert ''.join(docs[n]['item']['intended_key'] for n in range(START,END+1))=='ABCDE'; assert 'ncjmm' not in CAND.read_text().casefold()
 verify(DB,PRE,PRE)
 with tempfile.TemporaryDirectory() as td:
  work=Path(td)/'promote.db'; shutil.copy2(DB,work); c=sqlite3.connect(work)
  try:
   c.execute('BEGIN IMMEDIATE')
   for n in range(START,END+1):
    d=copy.deepcopy(docs[n]); cid=f'S1-DIRECT-{n:04d}-20260910T211500Z'; d['candidate_id']=cid
    d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','production_import_scope':f'Q{START}-Q{END}','authoritative_pre_db_blob':DB_BLOB,'authoritative_pre_count':PRE,'final_qa_manifest_blob':MAN_BLOB,'detached_simulation_blob':SIM_BLOB}
    review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':f'Q{START}-Q{END} production transactional import'}; rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh; ph=hobj(d)
    c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS','2026-09-10T21:15:00Z'))
    c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS','2026-09-10T21:15:00Z'))
   c.execute('update step2_finalization set item_count=? where id=1',(POST,)); c.commit()
  except Exception:
   c.rollback(); c.close(); raise
  c.close(); verify(work,POST,POST); shutil.copy2(work,DB)
 post_blob=gitblob(DB); verify(DB,POST,POST)
 v={'audit_id':f'Q{START}-Q{END}-PRODUCTION-IMPORT-VERIFY-20260910','status':'PRODUCTION_IMPORT_PASS','imported_range':f'Q{START}-Q{END}','imported_count':5,'pre_db_blob':DB_BLOB,'post_db_blob':post_blob,'candidate_blob':CAND_BLOB,'final_qa_manifest_blob':MAN_BLOB,'detached_simulation_blob':SIM_BLOB,'item_count':POST,'review_count':POST,f'contiguous_q0001_q{POST}':True,'sqlite_integrity':'ok','payload_review_consistency':'PASS',f'q{START}_q{END}_present_exactly_once':True,'production_import_status':'PASS','failures':[]}
 st={'audit_id':f'STEP2-FINAL-Q0001-Q{POST}-20260910','item_count':POST,'step2_final_review_count':POST,f'contiguous_q0001_q{POST}':True,f'q{START}_q{END}_present_exactly_once':True,'sqlite_integrity':'ok','pre_db_blob':DB_BLOB,'post_db_blob':post_blob,'imported_range':f'Q{START}-Q{END}','imported_count':5,'detached_simulation_blob':SIM_BLOB,'final_qa_manifest_blob':MAN_BLOB,'production_import_status':'PASS','verified_at':'2026-09-10T21:15:00Z'}
 VERIFY.parent.mkdir(exist_ok=True); VERIFY.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n'); STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(st,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(v,sort_keys=True))
if __name__=='__main__': main()
