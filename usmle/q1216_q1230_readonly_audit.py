#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, re, sqlite3, subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
STATE=ROOT/'state'/'step2_final_q0001_q1215.json'
BATCH=ROOT/'batch_specs_1201_1300'
OFFICIAL_DISC={
 'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology',
 'Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'
}
TOKEN_RE=re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
STOP={"the","and","for","with","that","this","from","into","most","which","patient","patients","cell","cells","normal","shows","show","directly","defect","signaling","loss","function","genetic","testing","identifies","receptor","receptors","disease","disorder"}
TERMS={
 1216:['friedreich','fxn','frataxin','gaa repeat'],
 1217:['adrenoleukodystrophy','abcd1','very-long-chain fatty','peroxisom'],
 1218:['spinal muscular atrophy','smn1','smn2','survival motor neuron'],
 1219:['pmp22','charcot-marie-tooth','schwann','uniformly slowed'],
 1220:['rett','mecp2','methyl-cpg','hand-wringing'],
 1221:['pseudohypoparathyroidism','gnas','albright hereditary','gs-alpha'],
 1222:['abcc8','congenital hyperinsulinism','katp','beta-cell depolarization'],
 1223:['gck-mody','glucokinase','glucose sensor','mild fasting hyperglycemia'],
 1224:['mc2r','familial glucocorticoid deficiency','acth resistance'],
 1225:['familial hypocalciuric hypercalcemia','casr','hypocalciuria','calcium set point'],
 1226:['aire','tissue-restricted','medullary thymic','negative selection'],
 1227:['tap2','transporter associated with antigen','mhc class i deficiency'],
 1228:['il2rg','common gamma chain','x-linked scid'],
 1229:['zap70','zap-70','anti-cd3','pma','ionomycin'],
 1230:['myd88','irak4','toll-like receptor','interleukin-1 receptor'],
}

def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def hobj(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def qnum(cid):
 m=re.search(r'DIRECT-(\d{4})',cid or '')
 return int(m.group(1)) if m else None

def strings(x):
 if isinstance(x,str): yield x
 elif isinstance(x,dict):
  for v in x.values(): yield from strings(v)
 elif isinstance(x,list):
  for v in x: yield from strings(v)
def text_of(x): return ' '.join(strings(x))
def toks(s): return [t for t in TOKEN_RE.findall(s.casefold()) if len(t)>2 and t not in STOP]
def vec(ts,idf):
 c=Counter(ts); return {k:(1+math.log(v))*idf.get(k,1.0) for k,v in c.items()}
def cos(a,b):
 if not a or not b:return 0.0
 n=sum(a[k]*b[k] for k in set(a)&set(b)); da=math.sqrt(sum(v*v for v in a.values())); db=math.sqrt(sum(v*v for v in b.values()))
 return n/(da*db) if da and db else 0.0

def load_candidates():
 out={}; paths={}
 for n in range(1216,1221):
  p=BATCH/'q1216_q1220_retry_20260905'/f'q{n}.json'; out[n]=json.loads(p.read_text()); paths[n]=p
 combo=BATCH/'05_q1221_q1225_retry_20260905_author.json'; batch=json.loads(combo.read_text())
 assert [int(x['num']) for x in batch['items']]==list(range(1221,1226))
 for x in batch['items']: out[int(x['num'])]=x; paths[int(x['num'])]=combo
 for n in range(1226,1231):
  p=BATCH/'q1226_q1230_r2'/f'Q{n}.json'; out[n]=json.loads(p.read_text()); paths[n]=p
 assert sorted(out)==list(range(1216,1231))
 return out,paths

def compact(i):
 return {'vignette':i.get('vignette'),'lead_in':i.get('lead_in'),'options':i.get('options'),'intended_key':i.get('intended_key'),'tested_construct':i.get('tested_construct')}

def main():
 assert STATE.exists(),'canonical Q1215 state missing'
 state=json.loads(STATE.read_text())
 assert state.get('final_status')=='FINAL_10_10_PASS'
 assert int(state.get('item_count',-1))==1215
 assert state.get('contiguous_q0001_q1215') is True
 expected_blob=state.get('post_authoritative_db_blob'); assert expected_blob
 actual_blob=gitblob(DB); assert actual_blob==expected_blob,(actual_blob,expected_blob)

 docs,paths=load_candidates(); validations={}; keys=[]
 for n,d in docs.items():
  item=d['item']; opts=item.get('options',{}); tags=d['blueprint'].get('disciplines',[]); sources=d.get('sources',[])
  frozen=d.get('status')=='CANDIDATE_FROZEN'
  prod_flag=d.get('production_import_permitted','ABSENT')
  zt=d.get('zero_trust_audit',{})
  validations[f'Q{n}']={
   'num_matches':int(d.get('num',-1))==n,
   'candidate_frozen':frozen,
   'five_options':list(opts)==['A','B','C','D','E'] and len(set(opts.values()))==5,
   'key_exists':item.get('intended_key') in opts,
   'official_disciplines':bool(tags) and all(t in OFFICIAL_DISC for t in tags),
   'sources_with_https_and_locators':len(sources)>=2 and all(str(s.get('url','')).startswith('https://') and str(s.get('section_locator','')).strip() for s in sources),
   'ncjmm_absent':'ncjmm' not in text_of(d).casefold(),
   'production_flag_not_true':prod_flag is not True,
   'zero_trust_defects_zero_or_legacy_absent':('material_defects_remaining' not in zt) or zt.get('material_defects_remaining')==0,
  }
  if not all(validations[f'Q{n}'].values()): raise SystemExit(f'Q{n} candidate validation failed: {validations[f"Q{n}"]}')
  keys.append(item['intended_key'])
 assert Counter(keys)==Counter({'A':3,'B':3,'C':3,'D':3,'E':3}),Counter(keys)

 with sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True) as con:
  con.execute('PRAGMA query_only=ON')
  integrity=con.execute('PRAGMA integrity_check').fetchone()[0]; assert integrity=='ok'
  rows=con.execute("SELECT candidate_id,payload_json,payload_sha256,final_status FROM step2_final_items ORDER BY candidate_id").fetchall()
  reviews=con.execute("SELECT candidate_id,review_json,review_sha256,final_status FROM step2_final_reviews ORDER BY candidate_id").fetchall()
 assert len(rows)==1215 and len(reviews)==1215
 assert Counter(r[3] for r in rows)==Counter({'FINAL_10_10_PASS':1215})
 assert {qnum(r[0]) for r in rows}==set(range(1,1216))
 assert len({r[0] for r in rows})==1215 and len({r[0] for r in reviews})==1215
 prod=[]; mismatches=[]
 for cid,payload,stored,status in rows:
  obj=json.loads(payload); calc=hobj(obj)
  if calc!=stored:mismatches.append(cid)
  item=obj.get('item',obj); prod.append({'candidate_id':cid,'status':status,'item':item,'text':text_of(item)})
 assert not mismatches,mismatches

 term_hits={}
 for n,terms in TERMS.items():
  term_hits[f'Q{n}']={}
  for term in terms:
   needle=term.casefold(); hits=[]
   for r in prod:
    if needle in r['text'].casefold(): hits.append({'candidate_id':r['candidate_id'],'item':compact(r['item'])})
   term_hits[f'Q{n}'][term]=hits

 pt=[toks(r['text']) for r in prod]; N=len(pt); df=Counter()
 for ts in pt: df.update(set(ts))
 idf={t:math.log((N+1)/(f+1))+1 for t,f in df.items()}; pv=[vec(ts,idf) for ts in pt]
 nearest={}; cand_vec={}; cand_tok={}
 for n,d in docs.items():
  q=f'Q{n}'; ctext=text_of(d['item']); ct=toks(ctext); cv=vec(ct,idf); cand_vec[n]=cv; cand_tok[n]=ct; cs=set(ct)
  scored=[]
  for r,ts,v in zip(prod,pt,pv):
   score=cos(cv,v); overlap=sorted(cs & set(ts),key=lambda t:idf.get(t,0),reverse=True)[:18]
   scored.append((score,r,overlap))
  scored.sort(key=lambda x:x[0],reverse=True)
  nearest[q]=[{'candidate_id':r['candidate_id'],'tfidf_cosine':round(s,6),'overlap':o,'item':compact(r['item'])} for s,r,o in scored[:15]]

 within=[]
 for a in range(1216,1231):
  for b in range(a+1,1231):
   s=cos(cand_vec[a],cand_vec[b])
   if s>=0.15: within.append({'a':f'Q{a}','b':f'Q{b}','tfidf_cosine':round(s,6),'overlap':sorted(set(cand_tok[a])&set(cand_tok[b]),key=lambda t:idf.get(t,0),reverse=True)[:18]})
 within.sort(key=lambda x:x['tfidf_cosine'],reverse=True)

 out={
  'batch':'Q1216-Q1230','status':'RETRIEVAL_AUDIT_COMPLETE_REQUIRES_ADVERSARIAL_NEIGHBOR_REVIEW',
  'canonical_state_blob':gitblob(STATE),'authoritative_db_blob':actual_blob,'authoritative_db_sha256':hashlib.sha256(DB.read_bytes()).hexdigest(),
  'canonical_count':1215,'canonical_contiguous_range':'Q0001-Q1215','sqlite_integrity_check':integrity,
  'payload_hash_mismatches':mismatches,'candidate_validation':validations,'answer_key_distribution':dict(sorted(Counter(keys).items())),
  'candidate_file_blobs':{f'Q{n}':gitblob(paths[n]) for n in docs},
  'term_hits':term_hits,'nearest_neighbours':nearest,'within_batch_similarity':within,
  'production_db_modified':False,
  'note':'Retrieval evidence only. FINAL duplicate disposition must be adversarially reviewed; no production write occurs here.'
 }
 print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=='__main__':main()
