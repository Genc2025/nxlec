#!/usr/bin/env python3
from __future__ import annotations
import base64, gzip, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
PARTS=sorted(DATA.glob('batch012_manual_decisions.json.gz.b64.part*'))
PENDING=DATA/'pending_audit_next.json'
FROZEN=DATA/'rule1_batch012_input_q0551_q0600.json'
OVERRIDE=DATA/'clinical_overrides_zzzz_rule1_batch012_chronological_q0551_q0600_20260815.json'
EVIDENCE=DATA/'rule1_batch012_chronological_reaudit_evidence_q0551_q0600.json'
IDS=[f'V2-Q{i:04d}' for i in range(551,601)]
STATUS='SOURCE_VERIFIED_2026_RULE1_BATCH012_CHRONOLOGICAL_MANUAL'
CRITERIA=['source_authority_verified','source_currentness_verified','exact_locator_verified','stem_factual_accuracy_verified','correct_answer_verified','rationale_verified','distractors_verified','ambiguity_cue_second_answer_qc_verified','blueprint_topic_difficulty_verified','no_unresolved_conflicts','independent_second_pass_qa']
FLAGS=['RULE1_BATCH012_MANUAL_ITEM_BY_ITEM_REAUDIT','LEGACY_STATUS_NOT_USED_AS_EVIDENCE','SEMANTIC_DECISIONS_NOT_BY_SCRIPT','STATIC_MANUAL_AUTHORED_FINAL_OPTIONS','SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED','MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS','INDEPENDENT_SECOND_PASS_QA_PASS','OPTION_LENGTH_METRICS_MEASUREMENT_ONLY','MANUAL_ANSWER_POSITION_CUE_QC_PASS']
def jd(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def metrics(options,key):
    lengths={k:len(str(options[k]).strip()) for k in 'ABCD'}; mn=min(lengths.values()); mx=max(lengths.values())
    dm=sum(lengths[k] for k in 'ABCD' if k!=key)/3; order=sorted('ABCD',key=lambda k:(lengths[k],k))
    return {'characters':lengths,'lengths_json':jd(lengths),'min_chars':mn,'max_chars':mx,'max_min_ratio':round(mx/max(mn,1),4),'correct_option':key,'correct_length_rank':order.index(key)+1,'correct_is_extreme':int(lengths[key] in (mn,mx)),'correct_deviation_from_distractor_mean':round(abs(lengths[key]-dm)/max(dm,1),4),'use':'MEASUREMENT_ONLY_NOT_SEMANTIC_GATE'}
if not PARTS: raise SystemExit('Batch012 manual-decision parts missing')
try:
    raw=gzip.decompress(base64.b64decode(''.join(p.read_text(encoding='ascii').strip() for p in PARTS)))
    decisions_doc=json.loads(raw.decode('utf-8'))
except Exception as exc: raise SystemExit(f'Batch012 manual-decision payload decode failed: {exc}')
if decisions_doc.get('batch')!='Q0551-Q0600' or decisions_doc.get('legacy_status_evidence') is not False or decisions_doc.get('semantic_decisions_by_script') is not False or decisions_doc.get('criteria_names')!=CRITERIA:
    raise SystemExit('Invalid Batch012 manual-decision header')
decisions=decisions_doc.get('decisions',[])
if [x.get('id') for x in decisions]!=IDS or len(decisions)!=50: raise SystemExit('Batch012 decision scope/order mismatch')
if not FROZEN.exists():
    src=json.loads(PENDING.read_text(encoding='utf-8'))
    if src.get('range')!=[551,600] or src.get('count')!=50 or [x.get('question_uid') for x in src.get('questions',[])]!=IDS:
        raise SystemExit('Current pending audit is not Batch012 Q0551-Q0600; refusing to freeze wrong input')
    FROZEN.write_text(json.dumps(src,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frozen=json.loads(FROZEN.read_text(encoding='utf-8'))
base_items=frozen.get('questions',[])
if frozen.get('range')!=[551,600] or frozen.get('count')!=50 or [x.get('question_uid') for x in base_items]!=IDS: raise SystemExit('Frozen Batch012 input mismatch')
base={x['question_uid']:x for x in base_items}; dec={x['id']:x for x in decisions}
override_items=[]; evidence_items=[]; key_counts={k:0 for k in 'ABCD'}
for uid in IDS:
    b=base[uid]; d=dec[uid]
    if d.get('criteria')!=11 or d.get('criteria_names')!=CRITERIA or d.get('second_pass')!='PASS' or d.get('final')!='FINAL_QA_PASS' or d.get('semantic_decision_origin')!='MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT': raise SystemExit(f'{uid}: manual 11/11 evidence incomplete')
    n=d.get('ncsbn_first_check',{})
    if n.get('required_currentness_and_blueprint_check') is not True or n.get('result')!='PASS' or '2026-04-01' not in n.get('version','') or '2029-03-31' not in n.get('version',''): raise SystemExit(f'{uid}: NCSBN currentness evidence incomplete')
    if not d.get('source_url','').startswith('https://') or not d.get('source_locator','').strip() or not d.get('source_version','').strip(): raise SystemExit(f'{uid}: source provenance incomplete')
    options=d.get('options'); key=d.get('key')
    if not isinstance(options,dict) or set(options)!=set('ABCD') or key not in options: raise SystemExit(f'{uid}: final manual options/key invalid')
    norm=[str(options[k]).strip().casefold() for k in 'ABCD']
    if any(not x for x in norm) or len(set(norm))!=4: raise SystemExit(f'{uid}: blank/duplicate final options')
    stem=d.get('stem',b['stem']); rationale=d.get('rationale',b['rationale'])
    if not str(stem).strip() or not str(rationale).strip(): raise SystemExit(f'{uid}: final stem/rationale blank')
    m=metrics(options,key); key_counts[key]+=1
    detail=f"{d['source_locator']} {d['source_version']} NCSBN first-check: {n['locator']} {n['version']}"
    raw_data=json.loads(b['item_data_json']); raw_data['options']=options
    override_items.append({'question_uid':uid,'source_id':b['source_id'],'category_id':d['category_id'],'client_need':d['client_need'],'difficulty':d['difficulty'],'stem':stem,'item_data_json':jd(raw_data),'correct_answer_json':jd({'correct_option':key}),'rationale':rationale,'source_name':d['source_name'],'source_detail':detail,'source_url':d['source_url'],'clinical_qa_status':STATUS,'editorial_priority':'PRODUCTION_CANDIDATE','editorial_flags_json':jd(FLAGS),'qc':{'question_uid':uid,'lengths_json':m['lengths_json'],'min_chars':m['min_chars'],'max_chars':m['max_chars'],'max_min_ratio':m['max_min_ratio'],'correct_option':key,'correct_length_rank':m['correct_length_rank'],'correct_is_extreme':m['correct_is_extreme'],'qc_status':'MEASURED_NOT_GATE','qc_note':'Length metrics are measurement only; semantic distractor/cue/ambiguity decisions are manual.'}})
    e=dict(d); e['option_measurement']={k:v for k,v in m.items() if k not in {'lengths_json','min_chars','max_chars','correct_length_rank','correct_is_extreme'}}
    e['final_content_sha256']=hashlib.sha256(jd({'stem':stem,'options':options,'key':key,'rationale':rationale,'source_url':d['source_url'],'source_locator':d['source_locator'],'source_version':d['source_version'],'category_id':d['category_id'],'client_need':d['client_need'],'difficulty':d['difficulty']}).encode()).hexdigest()
    evidence_items.append(e)
if key_counts!={'A':13,'B':13,'C':12,'D':12}: raise SystemExit(f'Batch012 manual answer-position distribution mismatch: {key_counts}')
override={'version':decisions_doc['version'],'semantic_decisions_by_script':False,'manual_answer_position_distribution':key_counts,'questions':override_items}
evidence={'standard':'RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT','batch':'Q0551-Q0600','review_date':'2026-08-15','legacy_status_evidence':False,'semantic_decisions_by_script':False,'criteria_names':CRITERIA,'manual_answer_position_distribution':key_counts,'items':evidence_items}
OVERRIDE.write_text(json.dumps(override,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
EVIDENCE.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'BATCH012_MANUAL_PAYLOAD_MATERIALIZED items=50 override=50 evidence=50 keys={key_counts} semantic_script_decisions=0')
