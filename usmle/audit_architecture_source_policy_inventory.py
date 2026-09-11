#!/usr/bin/env python3
from __future__ import annotations
import json, os, sqlite3, subprocess, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent; DB=ROOT/'data'/'usmle-step1.db'
OUT=REPO/'usmle/audit/FULL_CANONICAL_ARCHITECTURE_AND_SOURCE_POLICY_INVENTORY.json'
DB_BLOB=os.environ['DB_BLOB']
ALLOW_ROOTS={'usmle.org','nbme.org','fsmb.org','nih.gov','nlm.nih.gov','medlineplus.gov','cdc.gov','fda.gov','hhs.gov','ahrq.gov','cms.gov','hrsa.gov','osha.gov','epa.gov','va.gov','federalregister.gov','ecfr.gov','congress.gov','cancer.gov','samhsa.gov','nist.gov'}
def gitblob(p): return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()
def host(url):
    m=re.match(r'https?://([^/]+)',str(url).casefold()); return m.group(1).split(':')[0] if m else ''
def official_host(h):
    return any(h==r or h.endswith('.'+r) for r in ALLOW_ROOTS)
def safe_count(c,t):
    try:return c.execute(f'select count(*) from "{t}"').fetchone()[0]
    except:return None
def main():
    assert gitblob(DB)==DB_BLOB
    c=sqlite3.connect(DB)
    tables=[x[0] for x in c.execute("select name from sqlite_master where type='table' order by name").fetchall()]
    counts={t:safe_count(c,t) for t in tables}
    step=c.execute("select candidate_id,payload_json from step2_final_items order by candidate_id").fetchall()
    step_ids={x[0] for x in step}
    original_sets={}
    for t in ('candidates','blind_audits','audits','decisions','items','executions','direct_reviews'):
        if t in tables:
            try: original_sets[t]={x[0] for x in c.execute(f'select candidate_id from "{t}"').fetchall()}
            except: original_sets[t]=set()
    matches={t:len(step_ids&s) for t,s in original_sets.items()}
    hosts={}; patterns={'medlineplus_ency_adam':0,'pubmed_index_only':0,'pmc_journal_content_review_required':0,'statpearls_bookshelf':0,'geneReviews_bookshelf_review_required':0,'commercial_or_nonfederal':0,'official_federal_or_exam_host':0,'sources_total':0}
    outside={}
    for cid,pj in step:
        p=json.loads(pj)
        for s in p.get('sources',[]) if isinstance(p.get('sources'),list) else []:
            if not isinstance(s,dict):continue
            patterns['sources_total']+=1
            u=str(s.get('url','')); h=host(u); hosts[h]=hosts.get(h,0)+1
            title=str(s.get('title','')).casefold()
            if '/ency/' in u.casefold() and h in {'medlineplus.gov','www.medlineplus.gov'}: patterns['medlineplus_ency_adam']+=1
            if h=='pubmed.ncbi.nlm.nih.gov': patterns['pubmed_index_only']+=1
            if 'statpearls' in title or ('ncbi.nlm.nih.gov/books/nbk' in u.casefold() and 'statpearls' in title): patterns['statpearls_bookshelf']+=1
            if h and h not in ALLOW:
                patterns['outside_allowlist']+=1; outside[h]=outside.get(h,0)+1
    # Blind audit verdict distribution where tables exist.
    blind_verdicts={}; audit_verdicts={}
    if 'blind_audits' in tables:
        for cid,bj in c.execute('select candidate_id,blind_json from blind_audits'):
            try:
                j=json.loads(bj); v=j.get('blind_verdict') or j.get('verdict') or 'MISSING'
            except: v='INVALID_JSON'
            blind_verdicts[v]=blind_verdicts.get(v,0)+1
    if 'audits' in tables:
        for cid,aj in c.execute('select candidate_id,audit_json from audits'):
            try:
                j=json.loads(aj); v=j.get('final_verdict') or j.get('verdict') or j.get('status') or 'MISSING'
            except: v='INVALID_JSON'
            audit_verdicts[v]=audit_verdicts.get(v,0)+1
    c.close()
    out={'audit_id':'FULL-CANONICAL-ARCHITECTURE-SOURCE-POLICY-INVENTORY-20260911','db_blob':DB_BLOB,'production_db_modified':False,
         'tables':tables,'table_counts':counts,'step2_final_candidate_count':len(step_ids),'step2_ids_matching_original_pipeline_tables':matches,
         'blind_audit_verdict_distribution':blind_verdicts,'audit_verdict_distribution':audit_verdicts,
         'source_inventory':{'host_counts':dict(sorted(hosts.items(),key=lambda kv:(-kv[1],kv[0]))),'policy_flags':patterns,'commercial_or_nonfederal_hosts':dict(sorted(outside.items(),key=lambda kv:-kv[1]))}}
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'counts':counts,'matches':matches,'blind':blind_verdicts,'audit':audit_verdicts,'policy_flags':patterns},sort_keys=True))
if __name__=='__main__':main()
