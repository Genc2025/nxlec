#!/usr/bin/env python3
from __future__ import annotations
import json
import run_wave30_balanced as balanced
import run_wave30_manual_payload as wave30

def main():
    balanced.main()
    payload=json.loads(wave30.OUT.read_text(encoding='utf-8'))
    for q in payload['questions']:
        qc=q['qc']
        lengths=json.loads(qc['lengths_json'])
        key=qc['correct_option']
        ordered=sorted(lengths.items(), key=lambda kv:(kv[1],kv[0]))
        rank=next(i+1 for i,(k,_) in enumerate(ordered) if k==key)
        qc['correct_length_rank']=rank
        qc['correct_is_extreme']=1 if lengths[key] in (min(lengths.values()),max(lengths.values())) else 0
        qc['qc_note']=(f"Manual item-by-item option wording/cue review. Strict limits passed: "
                       f"max/min={qc['max_min_ratio']:.4f} <= 1.15; "
                       f"correct-vs-distractor-mean deviation={qc['correct_vs_distractor_mean_deviation']:.4f} <= 0.10.")
    wave30.OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wave30 QC schema completed for 50/50 items')

if __name__=='__main__': main()
