#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sqlite3,subprocess,urllib.request
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
CAND=REPO/os.environ['CAND_PATH']; OUT=REPO/os.environ['OUT_PATH']; DB=ROOT/'data'/'usmle-step1.db'
CAND_BLOB=os.environ['CAND_BLOB']; DB_BLOB=os.environ.get('DB_BLOB','1a0f0b702f86a57624161413ba60fa4ce88e8d97')
START=int(os.environ['START_Q']); END=int(os.environ['END_Q'])
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def toks(s): return set(norm(s).split())
def jac(a,b):
 A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def fetch_text(url):
 host=urlparse(url).netloc.casefold()
 if 'pubmed.ncbi.nlm.nih.gov' in host:
  m=re.search(r'/([0-9]+)/?$',url)
  if m: url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+m.group(1)+'&retmode=xml'
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-QA/3.0'})
 with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(2500000)
 return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore')))
def item_text(x):
 it=x['item']; return ' '.join([it.get('vignette',''),it.get('lead_in',''),*it.get('options',{}).values(),it.get('tested_construct','')])
def main():
 assert blob(CAND)==CAND_BLOB,(blob(CAND),CAND_BLOB); assert blob(DB)==DB_BLOB,(blob(DB),DB_BLOB)
 raw=CAND.read_text(); assert 'ncjmm' not in raw.casefold(); b=json.loads(raw); items=b['items']
 assert [x['num'] for x in items]==list(range(START,END+1)); assert len(items)==END-START+1
 assert b.get('canonical_count_before')==b.get('canonical_count_after')==1300 and b.get('production_import_ready') is False
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close(); assert len(rows)==reviews==1300
 canon=[]
 for cid,pj in rows:
  try:
   p=json.loads(pj); qi=p.get('item',{}); text=' '.join([qi.get('vignette',''),qi.get('lead_in',''),*qi.get('options',{}).values(),qi.get('tested_construct','')])
  except Exception: text=pj
  canon.append((cid,text))
 cache={}; reports=[]; failures=[]
 for x in items:
  q=x['num']; it=x['item']; ex=x['explanation']; ev=x.get('evidence_map',[]); src=x.get('sources',[]); aq=x.get('author_qa',{}); bp=x.get('blueprint',{}); f=[]
  opts=it.get('options',{}); key=it.get('intended_key'); de=ex.get('distractor_explanations',{})
  if list(opts)!=list('ABCDE') or len({norm(v) for v in opts.values()})!=5: f.append('options')
  if key not in 'ABCDE': f.append('key')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
  if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): f.append('rationale_eo')
  if ex.get('key_explanation')!=de.get(key): f.append('key_rationale_binding')
  if bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): f.append('blueprint')
  em={e.get('option'):e for e in ev} if isinstance(ev,list) else {}
  if set(em)!=set('ABCDE'): f.append('evidence_shape')
  direct=[L for L,e in em.items() if e.get('direct_or_inference')=='direct']
  if direct!=[key]: f.append('evidence_derived_key')
  ids={s.get('source_id') for s in src}
  for L,e in em.items():
   if not set(e.get('source_ids',[])).issubset(ids): f.append('evidence_source_binding')
   loc=e.get('claim_locator') or e.get('source_locator')
   if loc and 'distractor_explanations' in loc and loc!=f'explanation.distractor_explanations.{L}': f.append('evidence_locator_binding')
  if aq.get('status')!='AUTHOR_QA_PASS' or aq.get('unresolved_content_defects')!=[]: f.append('author_state')
  attack=aq.get('second_answer_attack',{}); alt=attack.get('strongest_alternative') or attack.get('option')
  if alt not in opts or alt==key or len(attack.get('resolution','').strip())<35: f.append('second_answer_attack')
  source_status=[]
  for s in src:
   url=s.get('url',''); sid=s.get('source_id'); host=urlparse(url).netloc.casefold(); ok=True; detail={}
   if not url.startswith('https://') or not (s.get('section_locator') or s.get('source_locator')) or not sid: ok=False
   try:
    if url not in cache: cache[url]=fetch_text(url)
    page=cache[url].casefold(); tt=toks(s.get('title','')); overlap=len(tt&toks(page)); sem=len(toks(ex.get('key_explanation',''))&toks(page))
    if 'dailymed.nlm.nih.gov' in host:
     setid=str(s.get('setid','')).casefold(); core=[t for t in tt if t not in {'tablet','film','coated','injection','solution','prescribing','information','capsule'}]; co=len(set(core)&toks(page)); ok=ok and bool(setid) and setid in url.casefold() and co>=1 and sem>=2; detail={'setid':setid,'title_core_overlap':co,'semantic_overlap':sem}
    elif 'pubmed.ncbi.nlm.nih.gov' in host:
     m=re.search(r'/([0-9]+)/?$',url); ok=ok and bool(m) and m.group(1) in page and overlap>=2 and sem>=2; detail={'pmid':m.group(1) if m else None,'title_overlap':overlap,'semantic_overlap':sem}
    else:
     ok=ok and overlap>=1 and sem>=1; detail={'title_overlap':overlap,'semantic_overlap':sem}
   except Exception as e: ok=False; detail={'error':type(e).__name__}
   source_status.append({'source_id':sid,'url':url,'status':'PASS' if ok else 'BLOCKED',**detail})
   if not ok: f.append('live_source_binding')
  scored=sorted([(jac(item_text(x),ct),cid) for cid,ct in canon],reverse=True); maxj=scored[0][0] if scored else 0
  if maxj>=0.45: f.append('canonical_duplicate')
  reports.append({'q':q,'status':'PASS' if not f else 'BLOCKED','evidence_derived_key':direct[0] if len(direct)==1 else None,'intended_key':key,'second_answer_attack':'PASS' if 'second_answer_attack' not in f else 'BLOCKED','source_live_binding':'PASS' if 'live_source_binding' not in f else 'BLOCKED','blueprint':'PASS' if 'blueprint' not in f else 'BLOCKED','canonical_max_jaccard':round(maxj,5),'canonical_top_match':scored[0][1] if scored else None,'ncjmm':'NOT_APPLICABLE_USMLE','source_reports':source_status,'failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 out={'audit_id':f'Q{START}-Q{END}-ZERO-TRUST-20260910','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'canonical_review_count':1300,'item_count':len(items),'item_reports':reports,'failures':failures,'verdict':'ZERO_TRUST_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n'); print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(items)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
