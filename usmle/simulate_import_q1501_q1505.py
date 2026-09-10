#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,re,shutil,sqlite3,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
DB_BLOB='3ed79b65e3422fa8d9649ba7870185fbf0a07e9c'
CAND=ROOT/'batch_specs_1501_1600'/'01_q1501_q1505_author_20260910.json'
CAND_BLOB='934773fbd826484dea8c9917c4c763a2891871d9'
MAN=ROOT/'audit'/'Q1501_Q1505_FINAL_QA_PASS.json'
MAN_BLOB='c7c105fdfbafcf274bd55f0e7df0718057d6584c'
OUT=ROOT/'audit'/'Q1501_Q1505_DETACHED_IMPORT_SIMULATION.json'

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 if not m: raise SystemExit('bad candidate id '+str(cid))
 return int(m.group(1))
def validate_doc(n,d):
 i=d['item']; e=d['explanation']; bp=d['blueprint']; src=d.get('sources',[]); em=d.get('evidence_map')
 if d.get('num')!=n or i.get('intended_key') not in 'ABCDE' or list(i.get('options',{}))!=list('ABCDE'): raise SystemExit(f'Q{n}: item/key/options')
 if len(set(i['options'].values()))!=5 or set(e.get('distractor_explanations',{}))!=set('ABCDE') or not e.get('key_explanation') or not e.get('educational_objective'): raise SystemExit(f'Q{n}: rationale')
 if bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): raise SystemExit(f'Q{n}: blueprint')
 if 'ncjmm' in canon(d).casefold(): raise SystemExit(f'Q{n}: NCJMM contamination')
 ids={s.get('source_id') for s in src}
 if not src or None in ids or any(not s.get('url','').startswith('https://') or not (s.get('section_locator') or s.get('source_locator')) or not s.get('source_page_sha256') or not s.get('cited_section_sha256') for s in src): raise SystemExit(f'Q{n}: source/freeze metadata')
 if not isinstance(em,list): raise SystemExit(f'Q{n}: evidence map shape')
 oe=[x for x in em if isinstance(x.get('option'),str) and x.get('option') in 'ABCDE']; mm={x['option']:x for x in oe}
 if len(oe)!=5 or set(mm)!=set('ABCDE') or mm[i['intended_key']].get('direct_or_inference') not in {'direct','mixed'}: raise SystemExit(f'Q{n}: evidence map')
 if any(not set(x.get('source_ids',[])).issubset(ids) for x in oe): raise SystemExit(f'Q{n}: evidence source binding')

def main():
 if gitblob(DB)!=DB_BLOB: raise SystemExit('production DB blob changed')
 if gitblob(CAND)!=CAND_BLOB: raise SystemExit('candidate blob changed')
 if gitblob(MAN)!=MAN_BLOB: raise SystemExit('manifest blob changed')
 m=json.loads(MAN.read_text())
 if m.get('status')!='FINAL_QA_PASS' or m.get('final_qa_verdict')!='FINAL_QA_PASS_NO_MATERIAL_DEFECT' or m.get('production_import_ready') is not True or m.get('unresolved_defects')!=[] or m.get('suggested_changes')!=[]: raise SystemExit('manifest final gate')
 if m.get('candidate_batch_blob')!=CAND_BLOB or m.get('authoritative_db_blob')!=DB_BLOB or m.get('authoritative_db_final_count')!=1500 or m.get('authoritative_review_count')!=1500: raise SystemExit('manifest binding')
 if m.get('item_count')!=5 or m.get('item_range')!='Q1501-Q1505' or m.get('answer_key_sequence')!='ABCDE' or m.get('ncjmm')!='NOT_APPLICABLE_USMLE': raise SystemExit('manifest scope')
 b=json.loads(CAND.read_text()); docs={int(x['num']):x for x in b['items']}
 if set(docs)!=set(range(1501,1506)) or len(docs)!=5: raise SystemExit('candidate range')
 if ''.join(docs[n]['item']['intended_key'] for n in range(1501,1506))!='ABCDE': raise SystemExit('candidate key sequence')
 for n,d in docs.items(): validate_doc(n,d)
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 if con.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('production integrity')
 old=con.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
 oldr=con.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall(); fin=con.execute('select item_count from step2_finalization where id=1').fetchone(); con.close()
 if len(old)!=1500 or len(oldr)!=1500 or not fin or fin[0]!=1500: raise SystemExit('production count')
 if {qnum(x[0]) for x in old}!=set(range(1,1501)): raise SystemExit('production contiguity')
 rmap={x[0]:x for x in oldr}
 for cid,pj,ps,ash in old:
  if hobj(json.loads(pj))!=ps or cid not in rmap or rmap[cid][2]!=ash or rmap[cid][3]!='FINAL_10_10_PASS': raise SystemExit(cid+' pre payload/review consistency')
 with tempfile.TemporaryDirectory() as td:
  sim=Path(td)/'usmle-step1-sim.db'; shutil.copy2(DB,sim); c=sqlite3.connect(sim)
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('sim pre integrity')
  c.execute('BEGIN IMMEDIATE')
  for n in range(1501,1506):
   d=copy.deepcopy(docs[n]); cid=f'S1-DIRECT-{n:04d}-20260910T000000Z'; d['candidate_id']=cid
   d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','import_scope':'Q1501-Q1505','authoritative_pre_db_blob':DB_BLOB,'authoritative_pre_count':1500,'final_qa_manifest_blob':MAN_BLOB}
   review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':'Q1501-Q1505 detached import simulation V3'}
   rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh; ph=hobj(d)
   c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS','2026-09-10T00:00:00Z'))
   c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS','2026-09-10T00:00:00Z'))
  c.execute('update step2_finalization set item_count=? where id=1',(1505,)); c.commit()
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('sim post integrity')
  rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); rr=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall(); f2=c.execute('select item_count from step2_finalization where id=1').fetchone(); c.close()
  if len(rows)!=1505 or len(rr)!=1505 or not f2 or f2[0]!=1505 or {qnum(x[0]) for x in rows}!=set(range(1,1506)): raise SystemExit('sim post count/contiguity')
  rm={x[0]:x for x in rr}
  for cid,pj,ps,ash in rows:
   if hobj(json.loads(pj))!=ps or cid not in rm or rm[cid][2]!=ash or rm[cid][3]!='FINAL_10_10_PASS': raise SystemExit(cid+' sim payload/review consistency')
 if gitblob(DB)!=DB_BLOB: raise SystemExit('production DB modified during detached simulation')
 report={'audit_id':'Q1501-Q1505-DETACHED-IMPORT-SIMULATION-20260910','status':'DETACHED_IMPORT_SIMULATION_PASS','range':'Q1501-Q1505','incoming_count':5,'pre_production_count':1500,'simulated_post_count':1505,'candidate_blob':CAND_BLOB,'final_qa_manifest_blob':MAN_BLOB,'production_pre_db_blob':DB_BLOB,'all_final_qa_gates_bound':True,'incoming_contiguous':True,'post_simulation_contiguous_q0001_q1505':True,'sqlite_integrity':'ok','payload_review_consistency':'PASS','ncjmm':'NOT_APPLICABLE_USMLE','production_db_modified':False,'production_transactional_import_ready':True,'failures':[]}
 OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(report,sort_keys=True))
if __name__=='__main__': main()
