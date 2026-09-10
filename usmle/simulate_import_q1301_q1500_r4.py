#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import simulate_import_q1301_q1500 as s

R=s.ROOT
INV=R/'audit'/'Q1301_Q1500_CROSS_COLLISION_INVENTORY.json'
s.BATCHES=[
(1301,1305,R/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',R/'audit'/'Q1301_Q1305_FINAL_QA_PASS.json','6bbaebd807590c4e661df947beef1f2b9d25ad62'),
(1306,1330,R/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',R/'audit'/'Q1306_Q1330_FINAL_QA_PASS.json','39bbec465ec402629690f31a2dad188b807735bb'),
(1331,1355,R/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',R/'audit'/'Q1331_Q1355_FINAL_QA_PASS.json','7098a9022d9499d6ecf37343129b9b29dbd0e322'),
(1356,1380,R/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',R/'audit'/'Q1356_Q1380_FINAL_QA_PASS.json','5545d82cc8e4f07a80702d95ef3bcffd4a78a361'),
(1381,1400,R/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',R/'audit'/'Q1381_Q1400_FINAL_QA_PASS.json','031d7786665fb326df0171873b63ef89296ead97'),
(1401,1425,R/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',R/'audit'/'Q1401_Q1425_FINAL_QA_PASS.json','80cccbcd9f0823c9628246d306329c2669c6c4ad'),
(1426,1450,R/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',R/'audit'/'Q1426_Q1450_FINAL_QA_PASS.json','54e016ac63856b62eb771426b7134affcad2ffff'),
(1451,1475,R/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json',R/'audit'/'Q1451_Q1475_FINAL_QA_PASS.json','408d02147a76f93b43e317e1cc8578fa851575b2'),
(1476,1500,R/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json',R/'audit'/'Q1476_Q1500_FINAL_QA_PASS.json','1bf318a2e97fc997b026e80ecb6445c7b208211f'),
]

def main():
 inv=json.loads(INV.read_text())
 assert inv['scope']=='Q1301-Q1500' and inv['pair_count']==0 and inv['pairs']==[]
 s.main()
 out=json.loads(s.OUT.read_text())
 out['aggregate_collision_inventory_blob']=s.gitblob(INV)
 out['aggregate_collision_pair_count']=0
 out['simulation_revision']='R4_CURRENT_PERSISTED_STATE'
 s.OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
