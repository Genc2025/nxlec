#!/usr/bin/env python3
from __future__ import annotations
import json, math, re, sqlite3, subprocess
from collections import Counter, defaultdict
from pathlib import Path

DB=Path('NCLEX_CANONICAL.db')
EXPECTED_BLOB='182a1e979e11d62bebc85c5ceb859056b8812963'
SUMMARY=Path('RULE1_CLEANUP_2000_SCAN_SUMMARY.json')
CANDIDATES=Path('RULE1_CLEANUP_2000_CANDIDATES.jsonl')
NEARDUPS=Path('RULE1_CLEANUP_2000_NEAR_DUPLICATES.jsonl')
LOCATORS=Path('RULE1_CLEANUP_2000_LOCATOR_CANDIDATES.jsonl')
KEYS=['A','B','C','D']
ABS_RE=re.compile(r'\b(always|never|only|must|completely|entirely|all|none|solely|exclusively)\b',re.I)
WORD_RE=re.compile(r"[a-z0-9']+")
STOP={'a','an','the','and','or','of','to','in','on','for','with','is','are','was','were','be','been','being','that','this','which','who','whom','whose','when','where','what','why','how','client','patient','nurse','should','most','best','first','priority','following','action','finding','statement','indicates','requires'}
LOCATOR_UIDS={'V2-Q0970','V2-Q0972','V2-Q0712','V2-Q0719','V2-Q0984'}
GATES=['source_authority_verified','currentness_verified','exact_locator_verified','stem_verified','correct_answer_verified','distractors_verified','rationale_verified','educational_objective_verified','ambiguity_verified','second_answer_excluded','cueing_verified','blueprint_verified','independent_qa_passed','no_unresolved_conflict']
REQ=['question_uid','stem','item_data_json','correct_answer_json','rationale','educational_objective','source_organization','source_document_title','source_version_date','source_accessed_date','source_locator','source_url','source_claim_supported','blueprint_document_title','blueprint_version','blueprint_locator','blueprint_url','blueprint_topic','client_need','difficulty','audit_status','second_pass_status']

def norm_tokens(s):
    return {w for w in WORD_RE.findall((s or '').lower()) if len(w)>2 and w not in STOP}

def norm_text(s):
    return ' '.join(WORD_RE.findall((s or '').lower()))

def jacc(a,b):
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)

def item_payload(r):
    item=json.loads(r['item_data_json']); ans=json.loads(r['correct_answer_json'])
    return {
      'question_uid':r['question_uid'],'stable_sort_key':r['stable_sort_key'],'category_id':r['category_id'],'client_need':r['client_need'],'difficulty':r['difficulty'],
      'blueprint_topic':r['blueprint_topic'],'stem':r['stem'],'options':item.get('options',{}),'correct_option':ans.get('correct_option'),
      'rationale':r['rationale'],'educational_objective':r['educational_objective'],
      'source_organization':r['source_organization'],'source_document_title':r['source_document_title'],'source_version_date':r['source_version_date'],
      'source_accessed_date':r['source_accessed_date'],'source_locator':r['source_locator'],'source_url':r['source_url'],'source_claim_supported':r['source_claim_supported'],
      'blueprint_document_title':r['blueprint_document_title'],'blueprint_version':r['blueprint_version'],'blueprint_locator':r['blueprint_locator'],'blueprint_url':r['blueprint_url'],
      'audit_status':r['audit_status'],'second_pass_status':r['second_pass_status']
    }

def main():
    blob=subprocess.check_output(['git','rev-parse','HEAD:NCLEX_CANONICAL.db'],text=True).strip()
    if blob!=EXPECTED_BLOB: raise SystemExit(f'BLOCKED canonical blob {blob}')
    con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True); con.row_factory=sqlite3.Row
    integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
    rows=con.execute('SELECT * FROM questions ORDER BY stable_sort_key, question_uid').fetchall()
    if integrity!='ok' or len(rows)!=2000: raise SystemExit(f'BLOCKED integrity/count {integrity}/{len(rows)}')
    dup=con.execute('SELECT COUNT(*) FROM (SELECT question_uid,COUNT(*) n FROM questions GROUP BY question_uid HAVING n>1)').fetchone()[0]
    if dup: raise SystemExit(f'BLOCKED duplicate uid groups {dup}')

    missing=defaultdict(list); status=Counter(); second=Counter(); gate_fail=defaultdict(list)
    answer_counts=Counter(); candidate_by_uid=defaultdict(set); candidate_detail=defaultdict(dict)
    option_cache={}; token_cache={}; row_by_uid={r['question_uid']:r for r in rows}
    exact=defaultdict(list); norm=defaultdict(list)

    for idx,r in enumerate(rows):
        uid=r['question_uid']; status[r['audit_status']]+=1; second[r['second_pass_status']]+=1
        for g in GATES:
            if r[g]!=1: gate_fail[g].append(uid)
        for k in REQ:
            v=r[k]
            if v is None or (isinstance(v,str) and not v.strip()): missing[k].append(uid)
        try:
            opts=json.loads(r['item_data_json']).get('options',{})
            ans=json.loads(r['correct_answer_json']).get('correct_option')
        except Exception as e:
            candidate_by_uid[uid].add('malformed_json'); candidate_detail[uid]['json_error']=str(e); continue
        if sorted(opts)!=KEYS or ans not in KEYS:
            candidate_by_uid[uid].add('malformed_answer_or_options'); continue
        option_cache[uid]=(opts,ans); answer_counts[ans]+=1
        lengths={k:len((opts[k] or '').strip()) for k in KEYS}
        corr=lengths[ans]; dist=[lengths[k] for k in KEYS if k!=ans]; dist_avg=sum(dist)/3
        dist_max=max(dist); dist_min=min(dist)
        if corr>=dist_avg*1.40 and corr-dist_avg>=18:
            candidate_by_uid[uid].add('correct_answer_length_cue')
            candidate_detail[uid]['option_lengths']=lengths
        if corr==max(lengths.values()) and corr-dist_max>=12:
            candidate_by_uid[uid].add('correct_answer_uniquely_longest')
            candidate_detail[uid]['option_lengths']=lengths
        abs_by={k:sorted(set(m.group(1).lower() for m in ABS_RE.finditer(opts[k] or ''))) for k in KEYS}
        distractor_abs={k:v for k,v in abs_by.items() if k!=ans and v}
        if distractor_abs and not abs_by.get(ans):
            candidate_by_uid[uid].add('absolute_word_distractor_pattern')
            candidate_detail[uid]['absolute_words']=abs_by
        # structural formatting differences only; candidate, not clinical judgment
        punct={k:bool(re.search(r'[.!?]\s*$',(opts[k] or '').strip())) for k in KEYS}
        if len(set(punct.values()))>1 and sum(punct.values()) in (1,3):
            if punct[ans] != (sum(punct[k] for k in KEYS if k!=ans)>=2):
                candidate_by_uid[uid].add('option_terminal_punctuation_pattern')
                candidate_detail[uid]['terminal_punctuation']=punct
        starts={k:bool(re.match(r'^[A-Z]',(opts[k] or '').strip())) for k in KEYS}
        if len(set(starts.values()))>1 and (sum(starts.values()) in (1,3)):
            candidate_by_uid[uid].add('option_capitalization_pattern')
            candidate_detail[uid]['capitalization']=starts
        # answer-position local runs / deterministic-looking sequences are bank-level only
        exact[(r['stem'] or '').strip().lower()].append(uid)
        norm[norm_text(r['stem'])].append(uid)
        token_cache[uid]=norm_tokens(r['stem'])

    exact_groups=[v for k,v in exact.items() if k and len(v)>1]
    norm_groups=[v for k,v in norm.items() if k and len(v)>1]
    for grp in norm_groups:
        for uid in grp: candidate_by_uid[uid].add('normalized_exact_stem_duplicate')

    # Semantic-near-duplicate candidate generation: same client need or blueprint topic, token Jaccard >= .72.
    buckets=defaultdict(list)
    for r in rows:
        uid=r['question_uid']; buckets[('client',r['client_need'])].append(uid)
        if r['blueprint_topic']: buckets[('topic',r['blueprint_topic'])].append(uid)
    pairs={}
    for _,uids in buckets.items():
        n=len(uids)
        for i in range(n):
            a=uids[i]; ta=token_cache.get(a,set())
            if len(ta)<4: continue
            for j in range(i+1,n):
                b=uids[j]; tb=token_cache.get(b,set())
                if len(tb)<4: continue
                # cheap length bound
                mn=min(len(ta),len(tb)); mx=max(len(ta),len(tb))
                if mn/mx < .70: continue
                s=jacc(ta,tb)
                if s>=.72:
                    key=tuple(sorted((a,b)))
                    if s>pairs.get(key,0): pairs[key]=s
    near=[]
    for (a,b),s in sorted(pairs.items(), key=lambda kv:(-kv[1],kv[0])):
        ra=row_by_uid[a]; rb=row_by_uid[b]
        near.append({'uid_a':a,'uid_b':b,'jaccard':round(s,4),'stem_a':ra['stem'],'stem_b':rb['stem'],'blueprint_topic_a':ra['blueprint_topic'],'blueprint_topic_b':rb['blueprint_topic'],'client_need_a':ra['client_need'],'client_need_b':rb['client_need']})
        candidate_by_uid[a].add('semantic_near_duplicate_candidate'); candidate_by_uid[b].add('semantic_near_duplicate_candidate')

    # answer sequence metrics
    seq=[]
    for r in rows:
        uid=r['question_uid']; ans=option_cache.get(uid,({},None))[1]; seq.append((uid,ans))
    maxrun=(0,None,None,None); run=0; prev=object(); start=None
    for uid,k in seq:
        if k==prev: run+=1
        else: prev=k; run=1; start=uid
        if run>maxrun[0]: maxrun=(run,k,start,uid)
    transitions=Counter()
    for (_,a),(_,b) in zip(seq,seq[1:]): transitions[f'{a}->{b}']+=1

    # metadata normalization candidates
    client_counts=Counter(r['client_need'] for r in rows)
    diff_counts=Counter(r['difficulty'] for r in rows)
    bpdoc=Counter(r['blueprint_document_title'] for r in rows)
    bpver=Counter(r['blueprint_version'] for r in rows)

    with CANDIDATES.open('w',encoding='utf-8') as f:
        for uid in sorted(candidate_by_uid):
            p=item_payload(row_by_uid[uid]); p['candidate_reasons']=sorted(candidate_by_uid[uid]); p['candidate_detail']=candidate_detail.get(uid,{})
            f.write(json.dumps(p,ensure_ascii=False,sort_keys=True)+'\n')
    with NEARDUPS.open('w',encoding='utf-8') as f:
        for x in near: f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
    with LOCATORS.open('w',encoding='utf-8') as f:
        for uid in sorted(LOCATOR_UIDS):
            if uid not in row_by_uid: raise SystemExit(f'BLOCKED missing locator candidate {uid}')
            f.write(json.dumps(item_payload(row_by_uid[uid]),ensure_ascii=False,sort_keys=True)+'\n')

    summary={
      'status':'READ_ONLY_CANDIDATE_SCAN_COMPLETE','canonical_blob':blob,'integrity':integrity,'count':len(rows),'duplicate_uid_groups':dup,
      'final_qa_status_counts':dict(status),'second_pass_status_counts':dict(second),'gate_failure_counts':{g:len(v) for g,v in gate_fail.items()},
      'required_field_missing_counts':{k:len(v) for k,v in missing.items()},'answer_position_counts':dict(answer_counts),'max_same_answer_run':maxrun,'answer_transition_counts':dict(transitions),
      'technical_candidate_uid_count':len(candidate_by_uid),'technical_candidate_reason_counts':dict(Counter(x for v in candidate_by_uid.values() for x in v)),
      'exact_stem_duplicate_groups':len(exact_groups),'normalized_stem_duplicate_groups':len(norm_groups),'semantic_near_duplicate_pair_candidates':len(near),
      'client_need_counts':dict(client_counts),'difficulty_counts':dict(diff_counts),'blueprint_document_title_counts':dict(bpdoc),'blueprint_version_counts':dict(bpver),
      'locator_candidate_uids':sorted(LOCATOR_UIDS),
      'warning':'Heuristic candidates are not clinical failures or FINAL_QA evidence. Every semantic correction requires UID-level source verification and adversarial second pass.'
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RULE1_SCAN_SUMMARY='+json.dumps(summary,ensure_ascii=False,separators=(',',':')))
    con.close()

if __name__=='__main__': main()
