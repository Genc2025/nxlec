#!/usr/bin/env python3
import json
from pathlib import Path
p=Path('usmle/audit/Q1476_Q1500_DETERMINISTIC_PREFLIGHT.json')
r=json.loads(p.read_text())
blocked_items=[]
for x in r['item_reports']:
    if x['status']!='PASS':
        blocked_items.append({
            'q':x['q'],
            'failures':x['failures'],
            'canonical':{
                'status':x['canonical_duplicate_gate']['status'],
                'max_jaccard':x['canonical_duplicate_gate']['max_jaccard'],
                'max_sequence':x['canonical_duplicate_gate']['max_sequence'],
                'top1':x['canonical_duplicate_gate']['top5'][0] if x['canonical_duplicate_gate']['top5'] else None,
            },
            'workstream':{
                'status':x['prior_workstream_duplicate_gate']['status'],
                'max_jaccard':x['prior_workstream_duplicate_gate']['max_jaccard'],
                'max_sequence':x['prior_workstream_duplicate_gate']['max_sequence'],
                'top1':x['prior_workstream_duplicate_gate']['top5'][0] if x['prior_workstream_duplicate_gate']['top5'] else None,
            },
            'source_live_binding':x['source_live_binding'],
            'blueprint':x['blueprint'],
            'evidence_contract':x['evidence_contract'],
        })
blocked_sources=[s for s in r['source_reports'] if s['status']!='PASS']
print(json.dumps({
    'verdict':r['verdict'],
    'failures':r['failures'],
    'blocked_items':blocked_items,
    'blocked_sources':blocked_sources,
    'intrabatch_top10':r['intrabatch_top10'],
    'blocked_item_count':len(blocked_items),
    'blocked_source_count':len(blocked_sources),
},indent=2,ensure_ascii=False))
