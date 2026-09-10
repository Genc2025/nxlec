#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1501_q1505 as a

def main():
 a.main()
 b=json.loads(a.OUT.read_text())
 b['scope']='Five original USMLE Step 1 mechanism-focused items. Author QA does not substitute for zero-trust evidence-derived auditing.'
 a.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert 'ncjmm' not in a.OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_BATCH_V2_CLEAN','items':len(b['items']),'keys':b['answer_key_sequence']}))
if __name__=='__main__': main()
