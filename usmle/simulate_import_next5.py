#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,os,re,shutil,sqlite3,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'
START=int(os.environ['START_Q']); END=int(os.environ['END_Q']); PRE=int(os.environ['PRE_COUNT']); POST=END
DB_BLOB=os.environ['DB_BLOB']; CAND=REPO/os.environ['CAND_PATH']; CAND_BLOB=os.environ['CAND_BLOB']; MAN=REPO/os.environ['MAN_PATH']; MAN_BLOB=os.environ['MAN_BLOB']; OUT=REPO/os.environ['SIM_OUT']\nAUDIT_DATE=os.environ.get('AUDIT_DATE','20260910'); CANDIDATE_STAMP=os.environ.get('CANDIDATE_STAMP','20260910T210000Z'); FINALIZED_AT=os.environ.get('FINALIZED_AT',FINALIZED_AT)
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '');
 if not m: raise RuntimeError('bad candidate id '+str(cid))
 return int(m.group(1))
def verify(path,count,maxq):
 c=sqlite3.connect(path); assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); rev=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall(); fin=c.execute('select item_count from step2_finalization where id=1').fetchone(); c.close()
 assert len(rows)==len(rev)==count and fin and fin[0]==count and {qnum(x[0]) for x in rows}==set(range(1,maxq+1))
 rm={x[0]:x for x in rev}
 for cid,pj,ps,ash in rows: assert hobj(json.loads(pj))==ps and cid in rm and rm[cid][2]==ash and rm[cid][3]=='FINAL_10_10_PASS'
 return rows
def validate(d,n):
 i=d['item']; e=d['explanation']; src=d.get('sources',[]); em=d.get('evidence_map',[])
 assert d['num']==n and i['intended_key'] in 'ABCDE' and list(i['options'])==list('ABCDE') and len(set(i['options'].values()))==5
 assert set(e['distractor_explanations'])==set('ABCDE') and e['key_explanation'] and e['educational_objective'] and 'ncjmm' not in canon(d).casefold()
 assert src and all(s.get('url','').startswith('https://') and (s.get('section_locator') or s.get('source_locator')) and s.get('source_page_sha256') and s.get('cited_section_sha256') for s in src)
 oe=[x for x in em if x.get('option') in 'ABCDE']; mm={x['option']:x for x in oe}; assert len(oe)==5 and set(mm)==set('ABCDE') and mm[i['intended_key']]['direct_or_inference'] in {'direct','mixed'}
def main():
 assert END-START+1==5 and START==PRE+1 and POST==PRE+5
 assert gitblob(DB)==DB_BLOB and gitblob(CAND)==CAND_BLOB and gitblob(MAN)==MAN_BLOB
 m=json.loads(MAN.read_text()); assert m['status']=='FINAL_QA_PASS' and m['final_qa_verdict']=='FINAL_QA_PASS_NO_MATERIAL_DEFECT' and m['production_import_ready'] is True and m['unresolved_defects']==[] and m['suggested_changes']==[] and m['candidate_batch_blob']==CAND_BLOB and m['authoritative_db_blob']==DB_BLOB and m['authoritative_db_final_count']==PRE and m['authoritative_review_count']==PRE and m['item_count']==5 and m['ncjmm']=='NOT_APPLICABLE_USMLE'
 b=json.loads(CAND.read_text()); docs={x['num']:x for x in b['items']}; assert set(docs)==set(range(START,END+1)); assert ''.join(docs[n]['item']['intended_key'] for n in range(START,END+1))=='ABCDE'
 for n,d in docs.items(): validate(d,n)
 verify(DB,PRE,PRE)
 with tempfile.TemporaryDirectory() as td:
  sim=Path(td)/'sim.db'; shutil.copy2(DB,sim); c=sqlite3.connect(sim); c.execute('BEGIN IMMEDIATE')
  for n in range(START,END+1):
   d=copy.deepcopy(docs[n]); cid=f'S1-DIRECT-{n:04d}-{CANDIDATE_STAMP}'; d['candidate_id']=cid
   d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','import_scope':f'Q{START}-Q{END}','authoritative_pre_db_blob':DB_BLOB,'authoritative_pre_count':PRE,'final_qa_manifest_blob':MAN_BLOB}
   review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':f'Q{START}-Q{END} detached import simulation'}; rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh; ph=hobj(d)
   c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS',FINALIZED_AT))
   c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS',FINALIZED_AT))
  c.execute('update step2_finalization set item_count=? where id=1',(POST,)); c.commit(); c.close(); verify(sim,POST,POST)
 assert gitblob(DB)==DB_BLOB
 r={'audit_id':f'Q{START}-Q{END}-DETACHED-IMPORT-SIMULATION-{AUDIT_DATE}','status':'DETACHED_IMPORT_SIMULATION_PASS','range':f'Q{START}-Q{END}','incoming_count':5,'pre_production_count':PRE,'simulated_post_count':POST,'candidate_blob':CAND_BLOB,'final_qa_manifest_blob':MAN_BLOB,'production_pre_db_blob':DB_BLOB,'all_final_qa_gates_bound':True,'incoming_contiguous':True,f'post_simulation_contiguous_q0001_q{POST}':True,'sqlite_integrity':'ok','payload_review_consistency':'PASS','ncjmm':'NOT_APPLICABLE_USMLE','production_db_modified':False,'production_transactional_import_ready':True,'failures':[]}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(r,sort_keys=True))
if __name__=='__main__': main()
