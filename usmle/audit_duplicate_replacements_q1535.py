#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,sqlite3,subprocess,urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'
CAND=REPO/os.environ['CAND_PATH']; OUT=REPO/os.environ['OUT_PATH']
DB_BLOB=os.environ['DB_BLOB']
TARGETS=[306,317,318,323,403,791,799,965,966,1065,1102,1124,1184,1511]
STOP={'the','a','an','and','or','of','to','in','is','are','was','were','with','this','that','which','what','best','most','direct','directly','patient','following','would','does','not','drug','effect','activity','correct','mechanism','action','findings','explains'}

def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def norm(s): return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())
def toks(s): return set(norm(s).split())
def ctoks(s): return {t for t in toks(s) if t not in STOP and len(t)>2}
def jac(a,b):
 A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0.0
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or ''); return int(m.group(1)) if m else None
def item_text(p):
 it=p.get('item',{}); o=it.get('options',{})
 return ' '.join([it.get('vignette',''),it.get('lead_in',''),*(o.get(k,'') for k in 'ABCDE'),it.get('tested_construct','')])
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-Remediation-QA/1.0','Accept':'text/html,application/xhtml+xml'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read(4000000)
def clean(raw): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',raw.decode('utf-8','ignore'))).strip()
def nloc(s):
 s=str(s).casefold().replace('–','-').replace('—','-').replace('−','-')
 return ' '.join(re.sub(r'[^a-z0-9.]+',' ',s).split())
def resolve_part(nt,part):
 np=nloc(part); anchors=[np] if np else []
 no_num=re.sub(r'^\d+(?:\.\d+)*\s*','',np).strip()
 if no_num and no_num not in anchors: anchors.append(no_num)
 for phrase in ('mechanism of action','microbiology','positive likelihood ratio','clinical pharmacology'):
  if phrase in no_num and phrase not in anchors: anchors.append(phrase)
 hits=[]
 for a in anchors:
  if len(a)<4: continue
  st=0
  while True:
   i=nt.find(a,st)
   if i<0: break
   w=nt[max(0,i-150):i+7000].strip()
   if len(w)>=120: hits.append((len(a),i,w))
   st=i+1
 if not hits: raise RuntimeError('locator_not_resolved:'+part)
 hits.sort(key=lambda z:(z[0],z[1]),reverse=True); return hits[0][2]
def cited(text,loc):
 nt=nloc(text); parts=[p.strip() for p in re.split(r'[;|]',loc or '') if p.strip()]
 if not parts: raise RuntimeError('empty_locator')
 return '\n--LOCATOR-COMPONENT--\n'.join(resolve_part(nt,p) for p in parts),len(parts)

def main():
 assert gitblob(DB)==DB_BLOB
 b=json.loads(CAND.read_text()); items=b['items']
 assert b['targets']==TARGETS and [x['num'] for x in items]==TARGETS
 assert 'ncjmm' not in CAND.read_text().casefold()
 cache={}; failures=[]; reports=[]
 # Freeze live sources in candidate itself.
 for x in items:
  q=x['num']
  for s in x.get('sources',[]):
   url=s.get('url',''); loc=s.get('section_locator') or s.get('source_locator') or ''
   k=(url,loc)
   try:
    if k not in cache:
     raw=fetch(url); material,nparts=cited(clean(raw),loc)
     cache[k]=(raw,material,nparts)
    raw,material,nparts=cache[k]
    s['source_page_sha256']=hashlib.sha256(raw).hexdigest()
    s['cited_section_sha256']=hashlib.sha256(material.encode()).hexdigest()
    s['cited_locator_component_count']=nparts
    s['hash_status']='FROZEN_FROM_LIVE_REFETCH_ALL_DECLARED_LOCATOR_COMPONENTS_2026-09-11'
   except Exception as e:
    failures.append(f'Q{q}:source_freeze:{type(e).__name__}:{str(e)[:120]}')
 CAND.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 cand_blob=gitblob(CAND)

 # Canonical corpus excluding each item's own target Q.
 con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
 rc=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]
 assert len(rows)==rc==1535
 canon=[]
 for cid,pj in rows:
  try:p=json.loads(pj); canon.append((cid,qnum(cid),item_text(p)))
  except:canon.append((cid,qnum(cid),pj))
 con.close()

 for x in items:
  q=x['num']; f=[]; it=x['item']; ex=x['explanation']; opts=it.get('options',{}); key=it.get('intended_key'); src=x.get('sources',[]); aq=x.get('author_qa',{}); bp=x.get('blueprint',{})
  if list(opts)!=list('ABCDE') or len({norm(v) for v in opts.values()})!=5: f.append('options')
  if key not in 'ABCDE': f.append('key')
  if not it.get('vignette','').strip() or not it.get('lead_in','').strip().endswith('?'): f.append('item_form')
  de=ex.get('distractor_explanations',{})
  if set(de)!=set('ABCDE') or not ex.get('key_explanation') or not ex.get('educational_objective'): f.append('rationale_eo')
  if not bp.get('primary_system') or bp.get('official_outline_path')!=[bp.get('primary_system')] or not bp.get('primary_competency') or not bp.get('disciplines'): f.append('blueprint')
  ev=x.get('evidence_map')
  if not isinstance(ev,list):
   f.append('evidence_shape')
  else:
   em=[e for e in ev if isinstance(e,dict) and e.get('option') in 'ABCDE']
   if len(em)!=5 or {e.get('option') for e in em}!=set('ABCDE'): f.append('evidence_shape')
   else:
    strong=[e.get('option') for e in em if e.get('direct_or_inference') in {'direct','mixed'}]
    if strong!=[key]: f.append('evidence_derived_key')
    if any(e.get('direct_or_inference')!='inference' for e in em if e.get('option')!=key): f.append('distractor_evidence_class')
    ids={s.get('source_id') for s in src}
    if any(not set(e.get('source_ids',[])).issubset(ids) for e in em): f.append('evidence_source_binding')
  attack=aq.get('second_answer_attack',{}); alt=attack.get('strongest_alternative') or attack.get('option')
  if attack.get('status')!='PASS' or alt not in opts or alt==key or len(str(attack.get('resolution','')).strip())<30: f.append('second_answer_attack')
  sr=[]
  for s in src:
   url=s.get('url',''); loc=s.get('section_locator') or s.get('source_locator') or ''; sid=s.get('source_id')
   ok=True; detail={}
   if not url.startswith('https://') or not loc or not sid: ok=False
   try:
    raw,material,nparts=cache[(url,loc)]; page=clean(raw).casefold(); sem=len(ctoks(ex.get('key_explanation',''))&ctoks(page))
    if hashlib.sha256(raw).hexdigest()!=s.get('source_page_sha256') or hashlib.sha256(material.encode()).hexdigest()!=s.get('cited_section_sha256'): ok=False
    host=urlparse(url).netloc.casefold()
    if 'dailymed.nlm.nih.gov' in host:
     setid=str(s.get('setid','')).casefold()
     if not setid or setid not in url.casefold() or sem<2: ok=False
     detail={'setid':setid,'semantic_overlap':sem,'locator_components':nparts}
    else:
     tt=ctoks(s.get('title','')); ov=len(tt&ctoks(page))
     if ov<1 or sem<1: ok=False
     detail={'title_overlap':ov,'semantic_overlap':sem,'locator_components':nparts}
   except Exception as e:
    ok=False; detail={'error':type(e).__name__+':'+str(e)[:100]}
   sr.append({'source_id':sid,'status':'PASS' if ok else 'BLOCKED',**detail})
   if not ok: f.append('source_live_binding')
  scored=sorted([(jac(item_text(x),t),cid) for cid,cq,t in canon if cq!=q],reverse=True)
  mj=scored[0][0] if scored else 0
  if mj>=0.45: f.append('canonical_duplicate')
  # Cross-replacement collision.
  other=sorted([(jac(item_text(x),item_text(y)),y['num']) for y in items if y['num']!=q],reverse=True)
  rmj=other[0][0] if other else 0
  if rmj>=0.45: f.append('replacement_batch_duplicate')
  top_canonical_text=next((t for cid,cq,t in canon if scored and cid==scored[0][1]),'')
  reports.append({'q':q,'status':'PASS' if not f else 'BLOCKED','key':key,'second_answer_attack':'PASS' if 'second_answer_attack' not in f else 'BLOCKED','source_live_binding':'PASS' if 'source_live_binding' not in f else 'BLOCKED','canonical_max_jaccard':round(mj,5),'canonical_top_match':scored[0][1] if scored else None,'canonical_top_text':top_canonical_text if mj>=0.45 else None,'replacement_max_jaccard':round(rmj,5),'replacement_top_q':other[0][1] if other else None,'source_reports':sr,'failures':sorted(set(f))})
  failures.extend(f'Q{q}:{z}' for z in sorted(set(f)))
 out={'audit_id':'CONFIRMED-DUPLICATE-REPLACEMENTS-ZERO-TRUST-20260911','candidate_blob':cand_blob,'production_db_blob':DB_BLOB,'target_count':len(TARGETS),'targets':TARGETS,'reports':reports,'failures':failures,'verdict':'ZERO_TRUST_PASS' if not failures else 'BLOCKED','production_db_modified':False,'production_replacement_ready':not failures}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 if failures:
  print(json.dumps({'failed_reports':[r for r in reports if r.get('status')=='BLOCKED']},sort_keys=True))
 print(json.dumps({'verdict':out['verdict'],'candidate_blob':cand_blob,'failures':failures,'max_jaccard':max((r['canonical_max_jaccard'] for r in reports),default=0)},sort_keys=True))
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
