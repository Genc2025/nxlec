#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from difflib import SequenceMatcher
from itertools import permutations
from pathlib import Path

DB=Path('NCLEX_FULL_3525_RULE1_1125.db')
OUT=Path('RULE1_FULL_3525_DUPLICATE_CANDIDATES.json')
PAIRS=[
('V2-Q2045','V2-Q2244'),('V2-Q2045','V2-Q2094'),('V2-Q0702','V2-Q1435'),('V2-Q1224','V2-Q1225'),('V2-Q2094','V2-Q2244'),('V2-Q1036','V2-Q1037'),
('V2-Q0768','V2-Q1058'),('V2-Q0231','V2-Q1159'),('V2-Q2022','V2-Q2168'),('V2-Q1174','V2-Q1175'),('V2-Q1432','V2-Q1437')]

def seq(a,b): return SequenceMatcher(None,(a or '').lower(),(b or '').lower(),autojunk=False).ratio()

def opts(row):
    try:
        d=json.loads(row['item_data_json']); o=d.get('options',{})
        if isinstance(o,dict): return {k:str(v) for k,v in o.items()}
    except Exception: pass
    return {}

def answer_text(row,o):
    try:
        c=json.loads(row['correct_answer_json']); k=c.get('correct_option')
        return o.get(k,'')
    except Exception: return ''

def option_match(a,b):
    av=list(a.values()); bv=list(b.values())
    if len(av)!=len(bv) or not av: return 0.0
    if len(av)>7: return 0.0
    best=0.0
    for p in permutations(range(len(bv))):
        s=sum(seq(av[i],bv[p[i]]) for i in range(len(av)))/len(av)
        best=max(best,s)
    return best

def main():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    wanted=sorted({u for p in PAIRS for u in p})
    qmarks=','.join('?' for _ in wanted)
    rows={r['question_uid']:r for r in con.execute(f'SELECT question_uid,stem,item_data_json,correct_answer_json,rationale,case_uid FROM questions WHERE question_uid IN ({qmarks})',wanted)}
    out=[]
    for a,b in PAIRS:
        ra,rb=rows[a],rows[b]; oa,ob=opts(ra),opts(rb); aa,ab=answer_text(ra,oa),answer_text(rb,ob)
        om=option_match(oa,ob); ss=seq(ra['stem'],rb['stem']); ans=seq(aa,ab) if aa and ab else 0.0; rat=seq(ra['rationale'],rb['rationale'])
        if ss>=0.85 and om>=0.72 and ans>=0.72:
            signal='STRONG_DUPLICATE_SIGNAL'
        elif ss>=0.80 and (om>=0.55 or ans>=0.65 or rat>=0.65):
            signal='REVIEW_FOR_REDUNDANCY'
        else:
            signal='SIMILAR_STEM_DIFFERENT_CONTENT'
        out.append({'uid_a':a,'uid_b':b,'signal':signal,'stem_similarity':round(ss,4),'option_set_similarity':round(om,4),'correct_answer_text_similarity':round(ans,4),'rationale_similarity':round(rat,4),'stem_a':ra['stem'],'stem_b':rb['stem'],'options_a':oa,'options_b':ob,'correct_answer_text_a':aa,'correct_answer_text_b':ab,'rationale_a':ra['rationale'],'rationale_b':rb['rationale']})
    con.close()
    report={'status':'DUPLICATE_CANDIDATE_CONTENT_REVIEW_PASS','pair_count':len(out),'strong_duplicate_signal_count':sum(x['signal']=='STRONG_DUPLICATE_SIGNAL' for x in out),'review_for_redundancy_count':sum(x['signal']=='REVIEW_FOR_REDUNDANCY' for x in out),'similar_stem_different_content_count':sum(x['signal']=='SIMILAR_STEM_DIFFERENT_CONTENT' for x in out),'pairs':out}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('DUP_CANDIDATE_REVIEW='+json.dumps({k:v for k,v in report.items() if k!='pairs'},sort_keys=True))
if __name__=='__main__': main()
