#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,re,shutil,sqlite3,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'; DB_BLOB='1a0f0b702f86a57624161413ba60fa4ce88e8d97'
OUT=ROOT/'audit'/'Q1301_Q1500_DETACHED_IMPORT_SIMULATION.json'
BATCHES=[
(1301,1305,ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',ROOT/'audit'/'Q1301_Q1305_FINAL_QA_PASS.json','6bbaebd807590c4e661df947beef1f2b9d25ad62'),
(1306,1330,ROOT/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',ROOT/'audit'/'Q1306_Q1330_FINAL_QA_PASS.json','39bbec465ec402629690f31a2dad188b807735bb'),
(1331,1355,ROOT/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',ROOT/'audit'/'Q1331_Q1355_FINAL_QA_PASS.json','7098a9022d9499d6ecf37343129b9b29dbd0e322'),
(1356,1380,ROOT/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',ROOT/'audit'/'Q1356_Q1380_FINAL_QA_PASS.json','83580bc8af4651ba9ca99e0957f551788e2b215c'),
(1381,1400,ROOT/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',ROOT/'audit'/'Q1381_Q1400_FINAL_QA_PASS.json','031d7786665fb326df0171873b63ef89296ead97'),
(1401,1425,ROOT/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',ROOT/'audit'/'Q1401_Q1425_FINAL_QA_PASS.json','d74b198c25f5235b227215f6c07b6c2d4dce4ed6'),
(1426,1450,ROOT/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',ROOT/'audit'/'Q1426_Q1450_FINAL_QA_PASS.json','1fe2d0300a65aa62df7d2113f85563e58164912b'),
(1451,1475,ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json',ROOT/'audit'/'Q1451_Q1475_FINAL_QA_PASS.json','f7796e9e3027ebefe6e240e533769128b3f54278'),
(1476,1500,ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json',ROOT/'audit'/'Q1476_Q1500_FINAL_QA_PASS.json','1bf318a2e97fc997b026e80ecb6445c7b208211f'),
]
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def grams(s,n=5):
 w=norm(s).split(); return {tuple(w)} if len(w)<n else {tuple(w[i:i+n]) for i in range(len(w)-n+1)}
def jac(a,b): return len(a&b)/len(a|b) if a|b else 0.0
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 if not m: raise SystemExit('bad candidate id '+str(cid))
 return int(m.group(1))
def item_text(d):
 i=d['item']; return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct','')])
def validate_doc(n,d):
 i=d['item']; e=d['explanation']; bp=d['blueprint']; src=d.get('sources',[]); em=d.get('evidence_map')
 if d.get('num')!=n or i.get('intended_key') not in 'ABCDE' or list(i.get('options',{}))!=list('ABCDE'): raise SystemExit(f'Q{n}: item/key/options')
 if len(set(i['options'].values()))!=5 or set(e.get('distractor_explanations',{}))!=set('ABCDE') or not e.get('key_explanation') or not e.get('educational_objective'): raise SystemExit(f'Q{n}: rationale')
 if bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): raise SystemExit(f'Q{n}: blueprint')
 if 'ncjmm' in canon(d).casefold(): raise SystemExit(f'Q{n}: NCJMM contamination')
 ids={s.get('source_id') for s in src}
 if not src or None in ids or any(not s.get('url','').startswith('https://') or not (s.get('section_locator') or s.get('source_locator')) for s in src): raise SystemExit(f'Q{n}: source metadata')
 if isinstance(em,list):
  option_entries=[x for x in em if isinstance(x.get('option'),str) and x.get('option') in 'ABCDE']
  mm={x['option']:x for x in option_entries}
  if len(option_entries)!=5 or set(mm)!=set('ABCDE') or mm[i['intended_key']].get('direct_or_inference') not in {'direct','mixed'}: raise SystemExit(f'Q{n}: evidence map')
  if any(not set(x.get('source_ids',[])).issubset(ids) for x in option_entries): raise SystemExit(f'Q{n}: evidence source binding')
  for x in em:
   if x in option_entries: continue
   if x.get('source_ids') is not None and not set(x.get('source_ids',[])).issubset(ids): raise SystemExit(f'Q{n}: extra evidence source binding')
   if x.get('claim_locator') and x.get('claim_locator') not in {'item.vignette','explanation.educational_objective'}: raise SystemExit(f'Q{n}: extra evidence locator')
 elif isinstance(em,dict):
  if set(em)!=set('ABCDE'): raise SystemExit(f'Q{n}: compact evidence map')
 else: raise SystemExit(f'Q{n}: evidence map absent')

def main():
 if gitblob(DB)!=DB_BLOB: raise SystemExit('production DB blob changed')
 all_docs={}; manifests=[]
 for a,b,bp,mp,mblob in BATCHES:
  if gitblob(mp)!=mblob: raise SystemExit(f'{mp.name}: manifest blob changed')
  m=json.loads(mp.read_text()); manifests.append(m)
  if m.get('status')!='FINAL_QA_PASS' or m.get('final_qa_verdict')!='FINAL_QA_PASS_NO_MATERIAL_DEFECT' or m.get('production_import_ready') is not True or m.get('unresolved_defects')!=[]: raise SystemExit(f'{mp.name}: final gate')
  if m.get('authoritative_db_blob')!=DB_BLOB or m.get('authoritative_db_final_count')!=1300: raise SystemExit(f'{mp.name}: DB binding')
  if gitblob(bp)!=m.get('candidate_batch_blob'): raise SystemExit(f'{bp.name}: candidate blob mismatch')
  batch=json.loads(bp.read_text()); docs={int(x['num']):x for x in batch['items']}
  if set(docs)!=set(range(a,b+1)) or len(docs)!=m.get('item_count') or m.get('item_range')!=f'Q{a}-Q{b}': raise SystemExit(f'{bp.name}: range/count')
  seq=''.join(docs[n]['item']['intended_key'] for n in range(a,b+1))
  if seq!=m.get('answer_key_sequence'): raise SystemExit(f'{bp.name}: answer sequence')
  for n,d in docs.items(): validate_doc(n,d)
  all_docs.update(docs)
 if set(all_docs)!=set(range(1301,1501)) or len(all_docs)!=200: raise SystemExit('incoming contiguity/count')
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 if con.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('production DB integrity')
 old=con.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
 oldr=con.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall(); con.close()
 if len(old)!=1300 or len(oldr)!=1300: raise SystemExit('production counts')
 if {qnum(x[0]) for x in old}!=set(range(1,1301)): raise SystemExit('production contiguity')
 base=[]
 for cid,pj,ps,ash in old:
  p=json.loads(pj)
  if hobj(p)!=ps: raise SystemExit(cid+' payload hash')
  base.append((cid,grams(item_text({'item':p.get('item',{})})),norm(p.get('item',{}).get('tested_construct',''))))
 incoming=[]; max_cross=0.0; max_canon=0.0; top_cross=None; top_canon=None
 for n in range(1301,1501):
  d=all_docs[n]; g=grams(item_text(d)); tc=norm(d['item'].get('tested_construct',''))
  for cid,og,otc in base:
   j=jac(g,og)
   if j>max_canon: max_canon=j; top_canon=(n,cid)
   if j>=0.80 or (tc and otc and tc==otc): raise SystemExit(f'Q{n}: canonical duplicate {cid}')
  for pn,pg,ptc in incoming:
   j=jac(g,pg)
   if j>max_cross: max_cross=j; top_cross=(n,pn)
   if j>=0.80 or (tc and ptc and tc==ptc): raise SystemExit(f'Q{n}: incoming duplicate Q{pn}')
  incoming.append((n,g,tc))
 with tempfile.TemporaryDirectory() as td:
  sim=Path(td)/'usmle-step1-sim.db'; shutil.copy2(DB,sim); c=sqlite3.connect(sim)
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('sim pre integrity')
  c.execute('BEGIN IMMEDIATE')
  for n in range(1301,1501):
   d=copy.deepcopy(all_docs[n]); cid=f'S1-DIRECT-{n:04d}-20260910T000000Z'; d['candidate_id']=cid
   d['step2_final_audit']={'final_10_10_gate':'FINAL_10_10_PASS','aggregate_import_simulation':'Q1301-Q1500','authoritative_pre_db_blob':DB_BLOB,'authoritative_pre_count':1300}
   review={'candidate_id':cid,'verdict':'FINAL_10_10_PASS','defects':[],'suggested_changes':[],'audit_scope':'Q1301-Q1500 detached import simulation'}
   rh=hobj(review); review['review_sha256']=rh; d['step2_final_audit']['review_sha256']=rh
   ph=hobj(d)
   c.execute('insert into step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) values(?,?,?,?,?,?)',(cid,canon(d),ph,rh,'FINAL_10_10_PASS','2026-09-10T00:00:00Z'))
   c.execute('insert into step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) values(?,?,?,?,?)',(cid,canon(review),rh,'FINAL_10_10_PASS','2026-09-10T00:00:00Z'))
  c.execute("update step2_finalization set item_count=? where id=1",(1500,)); c.commit()
  if c.execute('pragma integrity_check').fetchone()[0]!='ok': raise SystemExit('sim post integrity')
  rows=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); rrows=c.execute("select candidate_id,review_json,review_sha256,final_status from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchall()
  if len(rows)!=1500 or len(rrows)!=1500 or {qnum(x[0]) for x in rows}!=set(range(1,1501)): raise SystemExit('sim post count/contiguity')
  rm={x[0]:x for x in rrows}
  for cid,pj,ps,ash in rows:
   if hobj(json.loads(pj))!=ps or cid not in rm or rm[cid][2]!=ash or rm[cid][3]!='FINAL_10_10_PASS': raise SystemExit(cid+' sim payload/review consistency')
  c.close()
 if gitblob(DB)!=DB_BLOB: raise SystemExit('production DB modified during detached simulation')
 report={'audit_id':'Q1301-Q1500-DETACHED-IMPORT-SIMULATION-20260910','status':'DETACHED_IMPORT_SIMULATION_PASS','incoming_count':200,'range':'Q1301-Q1500','pre_production_count':1300,'simulated_post_count':1500,'manifest_count':len(manifests),'all_manifests_final_qa_pass':True,'all_candidate_blobs_bound':True,'incoming_contiguous':True,'post_simulation_contiguous_q0001_q1500':True,'sqlite_integrity':'ok','payload_review_consistency':'PASS','cross_incoming_duplicate_gate':'PASS','canonical_duplicate_gate':'PASS','max_cross_incoming_jaccard':round(max_cross,5),'max_cross_pair':top_cross,'max_canonical_jaccard':round(max_canon,5),'max_canonical_pair':top_canon,'ncjmm':'NOT_APPLICABLE_USMLE','production_db_blob_before_after':DB_BLOB,'production_db_modified':False,'production_transactional_import_ready':True,'failures':[]}
 OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(report,sort_keys=True))
if __name__=='__main__': main()
