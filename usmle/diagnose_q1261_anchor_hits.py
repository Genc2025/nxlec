#!/usr/bin/env python3
import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'usmle-step1.db'
terms=['phospholamban','serca2a','notch1','bicuspid aortic valve']
con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall();con.close()
for term in terms:
    print('\nTERM',term)
    for cid,pj in rows:
        if term in pj.casefold():
            p=json.loads(pj); i=p.get('item',p)
            print(cid,'TESTED=',i.get('tested_construct',''))
            print('LEAD=',i.get('lead_in',''))
            print('KEY=',i.get('intended_key',''),i.get('options',{}).get(i.get('intended_key',''),'') )
