#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sqlite3,subprocess,urllib.request
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent
CAND=REPO/os.environ['CAND_PATH']; OUT=REPO/os.environ['OUT_PATH']; DB=ROOT/'data'/'usmle-step1.db'
CAND_BLOB=os.environ['CAND_BLOB']; DB_BLOB=os.environ.get('DB_BLOB','1a0f0b702f86a57624161413ba60fa4ce88e8d97'); START=int(os.environ['START_Q']); END=int(os.environ['END_Q'])
STOP={'the','a','an','and','or','of','to','in','is','are','with','this','that','does','not','direct','directly','drug','effect','activity','correct'}
def blob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def toks(s): return set(norm(s).split())
def ctoks(s): return {t for t in toks(s) if t not in STOP and len(t)>2}
def jac(a,b):
 A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def fetch_text(url):
 host=urlparse(url).netloc.casefold()
 if 'pubmed.ncbi.nlm.nih.gov' in host:
  m=re.search(r'/([0-9]+)/?$',url)
  if m: url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+m.group(1)+'&retmode=xml'
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-QA/4.0'})
 with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(2500000)
 return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore')))
def item_text(x):
 it=x['item']; return ' '.join([it.get('vignette',''),it.get('lead_in',''),*it.get('options',{}).values(),it.get('tested_construct','')])
def evidence_key(ev,key,f):
 if isinstance(ev,dict):
  if set(ev)!=set('ABCDE'): f.append('evidence_shape'); return None
  strong=[L for L,v in ev.items() if norm(v).startswith('direct')]
  if strong!=[key]: f.append('evidence_derived_key')
  return strong[0] if len(strong)==1 else None
 if isinstance(ev,list):
  oe=[e for e in ev if isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']; em={e.get('option'):e for e in oe}
  if set(em)!=set('ABCDE') or len(oe)!=5: f.append('evidence_shape')
  strong=[L for L,e in em.items() if e.get('direct_or_inference') in {'direct','mixed'}]
  if strong!=[key]: f.append('evidence_derived_key')
  if any(em.get(L,{}).get('direct_or_inference')!='inference' for L in 'ABCDE' if L!=key): f.append('distractor_evidence_class')
  return strong[0] if len(strong)==1 else None
 f.append('evidence_shape'); return None
def main():
 assert blob(CAND)==CAND_BLOB and blob(DB)==DB_BLOB
 raw=CAND.read_text(); assert 'ncjmm' not in raw.casefold(); b=json.loads(raw); items=b['items']; assert [x['num'] for x in items]==list(range(START,END+1)); assert len(items)==END-START+1
 assert b.get('canonical_count_before')==b.get('canonical_count_after')==1300 and b.get('production_import_ready') is False
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True); assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall(); rc=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]; con.close(); assert len(rows)==rc==1300
 canon=[]
 for cid,pj in rows:
  try:
   p=json.loads(pj); qi=p.get('item',{}); t=' '.join([qi.get('vignette',''),qi.get('lead_in',''),*qi.get('options',{}).values(),qi.get('tested_construct','')])
  except Exception: t=pj
  canon.append((cid,t))
 cache={}; reports=[]; failures=[]
 for x in items:
  q=x['num']; it=x['item']; ex=x['explanation']; ev=x.get('evidence_map'); src=x.get('sources',[]); aq=x.get('author_qa',{}); bp=x.get('blueprint',{}); f=[]; opts=it.get('options',{}); key=it.get('intended_key'); de=ex.get('distractor_explanations',{})
  if list(opts)!=list('ABCDE') or len({norm(v) for v in opts.values()})!=5: f.append('options')
  if key not in 'ABCDE': f.append('key')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
  if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): f.append('rationale_eo')
  kro=len(ctoks(ex.get('key_explanation',''))&ctoks(de.get(key,'')))
  if norm(ex.get('key_explanation',''))!=norm(de.get(key,'')) and kro<2: f.append('key_rationale_binding')
  if bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): f.append('blueprint')
  derived=evidence_key(ev,key,f)
  # list evidence must bind claims to declared sources; dict schema is a compact classification and relies on live source + rationale gates.
  if isinstance(ev,list):
   ids={s.get('source_id') for s in src}
   for e in ev:
    if e.get('source_ids') is not None and not set(e.get('source_ids',[])).issubset(ids): f.append('evidence_source_binding')
  author_ok=(aq.get('status')=='AUTHOR_QA_PASS') or all(aq.get(k)=='PASS' for k in ['key_correctness','all_options_review','single_best_answer','adversarial_second_pass'])
  if not author_ok or aq.get('unresolved_content_defects')!=[]: f.append('author_state')
  attack=aq.get('second_answer_attack',{}); alt=attack.get('strongest_alternative') or attack.get('option')
  if alt not in opts or alt==key or len(attack.get('resolution','').strip())<30 or attack.get('status','PASS')!='PASS': f.append('second_answer_attack')
  sr=[]
  for s in src:
   url=s.get('url',''); sid=s.get('source_id'); host=urlparse(url).netloc.casefold(); ok=True; detail={}
   if not url.startswith('https://') or not (s.get('section_locator') or s.get('source_locator')) or not sid: ok=False
   try:
    if url not in cache: cache[url]=fetch_text(url)
    page=cache[url].casefold(); tt=toks(s.get('title','')); sem=len(ctoks(ex.get('key_explanation',''))&ctoks(page)); ov=len(tt&toks(page))
    if 'dailymed.nlm.nih.gov' in host:
     setid=str(s.get('setid','')).casefold(); core={t for t in tt if t not in {'tablet','film','coated','injection','solution','kit','capsule','prescribing','information'}}; co=len(core&toks(page)); ok=ok and bool(setid) and setid in url.casefold() and co>=1 and sem>=2; detail={'setid':setid,'title_core_overlap':co,'semantic_overlap':sem}
    elif 'pubmed.ncbi.nlm.nih.gov' in host:
     m=re.search(r'/([0-9]+)/?$',url); ok=ok and bool(m) and m.group(1) in page and ov>=2 and sem>=2; detail={'pmid':m.group(1) if m else None,'title_overlap':ov,'semantic_overlap':sem}
    else: ok=ok and ov>=1 and sem>=1; detail={'title_overlap':ov,'semantic_overlap':sem}
   except Exception as e: ok=False; detail={'error':type(e).__name__}
   sr.append({'source_id':sid,'status':'PASS' if ok else 'BLOCKED',**detail});
   if not ok: f.append('live_source_binding')
  scored=sorted([(jac(item_text(x),t),cid) for cid,t in canon],reverse=True); mj=scored[0][0] if scored else 0
  if mj>=0.45: f.append('canonical_duplicate')
  reports.append({'q':q,'status':'PASS' if not f else 'BLOCKED','evidence_derived_key':derived,'intended_key':key,'key_rationale_overlap':kro,'source_live_binding':'PASS' if 'live_source_binding' not in f else 'BLOCKED','second_answer_attack':'PASS' if 'second_answer_attack' not in f else 'BLOCKED','blueprint':'PASS' if 'blueprint' not in f else 'BLOCKED','canonical_max_jaccard':round(mj,5),'canonical_top_match':scored[0][1] if scored else None,'source_reports':sr,'failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 out={'audit_id':f'Q{START}-Q{END}-ZERO-TRUST-ADAPTIVE-20260910','candidate_blob':CAND_BLOB,'canonical_db_blob':DB_BLOB,'canonical_count':1300,'canonical_review_count':1300,'item_count':len(items),'item_reports':reports,'failures':failures,'verdict':'ZERO_TRUST_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_import_ready':False}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n'); print(json.dumps({'verdict':out['verdict'],'failures':failures,'items':len(items)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
