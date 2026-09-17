#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'usmle-step1.db'
PROSPECTS=ROOT/'prospects'/'q1606_q1610_candidates_20260918.json'
OUT=ROOT/'audit'/'Q1606_Q1610_PROSPECT_SCREEN.json'
STOP={'the','a','an','and','or','of','to','in','is','are','was','were','with','this','that','which','what','best','most','direct','directly','patient','following','would','does','not','drug','effect','activity','correct','mechanism','action','findings','explains','recognize','differentiate','link'}

def norm(s):
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())

def toks(s):
    return {t for t in norm(s).split() if len(t)>2 and t not in STOP}

def jac(a,b):
    u=a|b
    return len(a&b)/len(u) if u else 0.0

def qnum(cid):
    m=re.search(r'DIRECT-(\d{4})',cid or '')
    return int(m.group(1)) if m else None

def main():
    prospects=json.loads(PROSPECTS.read_text())
    c=sqlite3.connect(DB)
    rows=c.execute("select candidate_id,payload_json from step2_final_items order by candidate_id").fetchall()
    fin=c.execute('select item_count from step2_finalization where id=1').fetchone()[0]
    c.close()
    assert len(rows)==fin==1605

    canon=[]
    for cid,pj in rows:
        p=json.loads(pj)
        it=p.get('item') if isinstance(p.get('item'),dict) else {}
        ex=p.get('explanation') if isinstance(p.get('explanation'),dict) else {}
        drug=str(p.get('drug') or '')
        construct=str(it.get('tested_construct') or '')
        eo=str(ex.get('educational_objective') or '')
        text=' '.join([drug,construct,eo])
        canon.append({'q':qnum(cid),'candidate_id':cid,'drug':drug,'tested_construct':construct,'educational_objective':eo,'tokens':toks(text)})

    reports=[]
    for pr in prospects:
        ptext=' '.join([pr.get('drug',''),pr.get('proposed_construct',''),pr.get('proposed_objective','')])
        pt=toks(ptext)
        exact=[x for x in canon if norm(x['drug'])==norm(pr.get('drug','')) and norm(pr.get('drug',''))]
        scored=[]
        for x in canon:
            s=jac(pt,x['tokens'])
            if s>0:
                scored.append((s,x))
        scored.sort(key=lambda z:z[0],reverse=True)
        top=[{'jaccard':round(s,5),'q':x['q'],'candidate_id':x['candidate_id'],'drug':x['drug'],'tested_construct':x['tested_construct'],'educational_objective':x['educational_objective']} for s,x in scored[:8]]
        maxj=top[0]['jaccard'] if top else 0.0
        reports.append({
            'drug':pr['drug'],
            'proposed_construct':pr['proposed_construct'],
            'proposed_objective':pr['proposed_objective'],
            'exact_drug_matches':[{k:x[k] for k in ('q','candidate_id','drug','tested_construct','educational_objective')} for x in exact],
            'canonical_max_jaccard':maxj,
            'top_matches':top,
            'screen_status':'REJECT' if exact or maxj>=0.40 else ('MANUAL_REVIEW' if maxj>=0.30 else 'CLEAR')
        })

    out={
        'audit_id':'Q1606-Q1610-PROSPECT-CONSTRUCT-SCREEN-20260918',
        'canonical_count':fin,
        'scope':'Q0001-Q1605',
        'method':'Exact normalized drug match plus token-set Jaccard on drug + tested_construct + educational_objective; threshold >=0.40 rejects, 0.30-0.39999 manual review.',
        'reports':reports
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'canonical_count':fin,'results':[(x['drug'],x['screen_status'],x['canonical_max_jaccard'],len(x['exact_drug_matches'])) for x in reports]}))

if __name__=='__main__':
    main()
