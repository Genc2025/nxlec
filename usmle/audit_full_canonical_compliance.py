#!/usr/bin/env python3
from __future__ import annotations
import collections, hashlib, json, os, re, sqlite3, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
OUT=REPO/os.environ.get('AUDIT_OUT','usmle/audit/FULL_CANONICAL_Q0001_Q1535_COMPLIANCE.json')
EXPECTED=int(os.environ.get('EXPECTED_COUNT','1535'))
DB_BLOB=os.environ.get('DB_BLOB','')

STOP={'the','a','an','and','or','of','to','in','is','are','was','were','with','this','that','which','what','best','most','direct','directly','patient','following','would','does','not','drug','effect','activity','correct','mechanism','action','findings','explains'}

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def hobj(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()

def gitblob(p):
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()

def norm(s):
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',str(s).casefold()).split())

def toks(s):
    return {t for t in norm(s).split() if len(t)>2 and t not in STOP}

def jac(a,b):
    if not a or not b: return 0.0
    u=a|b
    return len(a&b)/len(u) if u else 0.0

def qnum(cid):
    m=re.search(r'DIRECT-(\d{4})',cid or '')
    return int(m.group(1)) if m else None

def is_sha256(s):
    return isinstance(s,str) and bool(re.fullmatch(r'[0-9a-f]{64}',s.casefold()))

def item_text(payload):
    it=payload.get('item') if isinstance(payload.get('item'),dict) else {}
    opts=it.get('options') if isinstance(it.get('options'),dict) else {}
    return ' '.join([
        str(it.get('vignette','')),
        str(it.get('lead_in','')),
        *(str(opts.get(k,'')) for k in 'ABCDE'),
        str(it.get('tested_construct',''))
    ]).strip()

def stem_text(payload):
    it=payload.get('item') if isinstance(payload.get('item'),dict) else {}
    return ' '.join([str(it.get('vignette','')),str(it.get('lead_in',''))]).strip()

def criteria_defects(p):
    d=[]
    it=p.get('item') if isinstance(p.get('item'),dict) else {}
    ex=p.get('explanation') if isinstance(p.get('explanation'),dict) else {}
    bp=p.get('blueprint') if isinstance(p.get('blueprint'),dict) else {}
    aq=p.get('author_qa') if isinstance(p.get('author_qa'),dict) else {}
    src=p.get('sources') if isinstance(p.get('sources'),list) else []
    ev=p.get('evidence_map')
    opts=it.get('options') if isinstance(it.get('options'),dict) else {}
    key=it.get('intended_key')
    rats=ex.get('distractor_explanations') if isinstance(ex.get('distractor_explanations'),dict) else {}

    if not str(it.get('vignette','')).strip(): d.append('missing_vignette')
    if not str(it.get('lead_in','')).strip(): d.append('missing_lead_in')
    elif not str(it.get('lead_in','')).strip().endswith('?'): d.append('lead_in_not_question')
    if list(opts.keys())!=list('ABCDE'): d.append('options_not_exact_A_E')
    if len({norm(v) for v in opts.values()})!=5: d.append('options_not_unique')
    if key not in 'ABCDE': d.append('invalid_key')
    if not str(it.get('tested_construct','')).strip(): d.append('missing_tested_construct')
    if not str(it.get('difficulty','')).strip(): d.append('missing_difficulty')
    if not str(it.get('difficulty_basis','')).strip(): d.append('missing_difficulty_basis')

    if not str(ex.get('key_explanation','')).strip(): d.append('missing_key_explanation')
    if set(rats.keys())!=set('ABCDE'): d.append('missing_A_E_rationales')
    if not str(ex.get('educational_objective','')).strip(): d.append('missing_educational_objective')

    if not str(bp.get('primary_system','')).strip(): d.append('missing_primary_system')
    if not str(bp.get('primary_competency','')).strip(): d.append('missing_primary_competency')
    if not isinstance(bp.get('disciplines'),list) or not bp.get('disciplines'): d.append('missing_disciplines')
    if bp.get('official_outline_path') != [bp.get('primary_system')]: d.append('blueprint_path_mismatch')

    if not src: d.append('missing_sources')
    for i,s in enumerate(src):
        if not isinstance(s,dict):
            d.append(f'source_{i+1}_not_object'); continue
        if not str(s.get('source_id','')).strip(): d.append(f'source_{i+1}_missing_source_id')
        if not str(s.get('title','')).strip(): d.append(f'source_{i+1}_missing_title')
        url=str(s.get('url',''))
        if not url.startswith('https://'): d.append(f'source_{i+1}_noncanonical_url')
        loc=s.get('section_locator') or s.get('source_locator')
        if not str(loc or '').strip(): d.append(f'source_{i+1}_missing_locator')
        if not str(s.get('retrieved_at','')).strip() and not str(s.get('date_basis','')).strip(): d.append(f'source_{i+1}_missing_currentness')
        if 'dailymed.nlm.nih.gov' in url.casefold():
            setid=str(s.get('setid','')).casefold()
            if not setid: d.append(f'source_{i+1}_missing_setid')
            elif setid not in url.casefold(): d.append(f'source_{i+1}_setid_url_mismatch')
        if not is_sha256(s.get('source_page_sha256')): d.append(f'source_{i+1}_missing_page_hash')
        if not is_sha256(s.get('cited_section_sha256')): d.append(f'source_{i+1}_missing_cited_hash')

    if isinstance(ev,list):
        em=[e for e in ev if isinstance(e,dict) and isinstance(e.get('option'),str) and e.get('option') in 'ABCDE']
        if len(em)!=5 or {e.get('option') for e in em}!=set('ABCDE'):
            d.append('evidence_map_shape')
        else:
            strong=[e.get('option') for e in em if e.get('direct_or_inference') in {'direct','mixed'}]
            if strong!=[key]: d.append('evidence_key_not_unique')
            if any(e.get('direct_or_inference')!='inference' for e in em if e.get('option')!=key):
                d.append('distractor_evidence_not_inference')
            source_ids={s.get('source_id') for s in src if isinstance(s,dict)}
            for e in em:
                if e.get('source_ids') is not None and not set(e.get('source_ids',[])).issubset(source_ids):
                    d.append('evidence_source_binding')
                    break
    elif isinstance(ev,dict):
        if set(ev.keys())!=set('ABCDE'): d.append('evidence_map_shape')
    else:
        d.append('missing_evidence_map')

    attack=aq.get('second_answer_attack') if isinstance(aq.get('second_answer_attack'),dict) else {}
    alt=attack.get('strongest_alternative') or attack.get('option')
    if attack.get('status')!='PASS' or alt not in opts or alt==key or len(str(attack.get('resolution','')).strip())<30:
        d.append('second_answer_attack_missing_or_weak')
    if aq.get('unresolved_content_defects') not in ([],None):
        d.append('author_unresolved_defects')
    required_aq=['key_correctness','all_options_review','single_best_answer','hidden_assumptions','fabricated_distractors','blueprint','rationale','educational_objective','adversarial_second_pass']
    for k in required_aq:
        if k in aq and not str(aq.get(k,'')).startswith('PASS'):
            d.append(f'author_qa_{k}_not_pass')
    raw=canon(p).casefold()
    if '"ncjmm"' in raw: d.append('ncjmm_present_in_usmle')
    return sorted(set(d))

def main():
    if DB_BLOB:
        assert gitblob(DB)==DB_BLOB, (gitblob(DB),DB_BLOB)
    c=sqlite3.connect(DB)
    integrity=c.execute('pragma integrity_check').fetchone()[0]
    items=c.execute("select candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at from step2_final_items order by candidate_id").fetchall()
    reviews=c.execute("select candidate_id,review_json,review_sha256,final_status,finalized_at from step2_final_reviews").fetchall()
    fin=c.execute('select item_count from step2_finalization where id=1').fetchone()
    c.close()

    revmap={r[0]:r for r in reviews}
    records=[]
    consistency=[]
    qs=[]
    defect_counts=collections.Counter()
    defect_items=[]
    exact_full=collections.defaultdict(list)
    exact_stem=collections.defaultdict(list)
    construct_groups=collections.defaultdict(list)
    token_sets=[]

    for row in items:
        cid,pj,ps,ash,status,finalized=row
        q=qnum(cid); qs.append(q)
        try:
            p=json.loads(pj)
        except Exception:
            consistency.append({'candidate_id':cid,'defects':['payload_json_invalid']})
            continue
        cd=[]
        if hobj(p)!=ps: cd.append('payload_sha256_mismatch')
        rr=revmap.get(cid)
        if rr is None: cd.append('missing_review')
        else:
            try: robj=json.loads(rr[1])
            except Exception: robj={}
            if hobj(robj)!=rr[2] and robj.get('review_sha256')!=rr[2]: cd.append('review_sha256_mismatch')
            if rr[2]!=ash: cd.append('item_review_audit_hash_mismatch')
            if rr[3]!='FINAL_10_10_PASS' or status!='FINAL_10_10_PASS': cd.append('final_status_mismatch')
            if robj.get('verdict')!='FINAL_10_10_PASS': cd.append('review_verdict_not_final')
            if robj.get('defects') not in ([],None): cd.append('review_has_defects')
            if robj.get('suggested_changes') not in ([],None): cd.append('review_has_suggested_changes')
        if cd: consistency.append({'candidate_id':cid,'q':q,'defects':sorted(set(cd))})

        d=criteria_defects(p)
        for z in d: defect_counts[z]+=1
        if d: defect_items.append({'candidate_id':cid,'q':q,'defects':d})

        ft=norm(item_text(p)); st=norm(stem_text(p))
        if ft: exact_full[ft].append(cid)
        if st: exact_stem[st].append(cid)
        construct=norm((p.get('item') or {}).get('tested_construct',''))
        if construct: construct_groups[construct].append(cid)
        token_sets.append((cid,q,toks(item_text(p))))

    exact_full_groups=[v for v in exact_full.values() if len(v)>1]
    exact_stem_groups=[v for v in exact_stem.values() if len(v)>1]
    repeated_construct_groups=[v for v in construct_groups.values() if len(v)>1]

    near=[]
    n=len(token_sets)
    for i in range(n):
        cid1,q1,t1=token_sets[i]
        for j in range(i+1,n):
            cid2,q2,t2=token_sets[j]
            s=jac(t1,t2)
            if s>=0.45:
                near.append({'q1':q1,'q2':q2,'candidate_id_1':cid1,'candidate_id_2':cid2,'jaccard':round(s,5)})
    near.sort(key=lambda x:x['jaccard'],reverse=True)
    high=[x for x in near if x['jaccard']>=0.75]
    medium=[x for x in near if 0.60<=x['jaccard']<0.75]
    gate=[x for x in near if 0.45<=x['jaccard']<0.60]

    nums=[q for q in qs if q is not None]
    contig=(len(nums)==EXPECTED and len(set(nums))==EXPECTED and set(nums)==set(range(1,EXPECTED+1)))
    counts_ok=(len(items)==len(reviews)==EXPECTED and fin and fin[0]==EXPECTED)

    # Zero-trust verdict: exact/high near duplicate or any stored-contract defect blocks.
    verdict='PASS' if not exact_full_groups and not exact_stem_groups and not high and not defect_items and not consistency and integrity=='ok' and contig and counts_ok else 'BLOCKED'
    out={
      'audit_id':f'FULL-CANONICAL-Q0001-Q{EXPECTED}-COMPLIANCE-20260911',
      'scope':f'Q0001-Q{EXPECTED}',
      'production_db_blob':gitblob(DB),
      'production_db_modified':False,
      'sqlite_integrity':integrity,
      'item_count':len(items),
      'review_count':len(reviews),
      'finalization_count':fin[0] if fin else None,
      'counts_ok':counts_ok,
      'contiguous_unique_q_numbers':contig,
      'payload_review_consistency_failure_count':len(consistency),
      'payload_review_consistency_failures':consistency[:200],
      'criteria_contract':{
        'five_unique_options_A_E':True,
        'single_intended_key':True,
        'vignette_and_question_lead_in':True,
        'tested_construct_and_difficulty':True,
        'A_E_rationales_and_educational_objective':True,
        'blueprint_metadata':True,
        'source_identity_url_locator_currentness_hashes':True,
        'evidence_map_key_binding':True,
        'second_answer_attack':True,
        'NCJMM_not_applicable_USMLE':True,
        'final_review_no_defects_or_suggested_changes':True
      },
      'items_meeting_all_stored_generation_criteria':len(items)-len(defect_items),
      'items_with_generation_criteria_defects':len(defect_items),
      'generation_defect_counts':dict(defect_counts.most_common()),
      'generation_defect_items':defect_items[:500],
      'duplicate_analysis':{
        'exact_full_item_duplicate_group_count':len(exact_full_groups),
        'exact_full_item_duplicate_groups':exact_full_groups[:100],
        'exact_stem_duplicate_group_count':len(exact_stem_groups),
        'exact_stem_duplicate_groups':exact_stem_groups[:100],
        'repeated_tested_construct_group_count':len(repeated_construct_groups),
        'repeated_tested_construct_groups':repeated_construct_groups[:100],
        'near_duplicate_threshold':'token-set Jaccard on vignette + lead-in + A-E options + tested_construct',
        'pairs_jaccard_ge_0_75_count':len(high),
        'pairs_jaccard_0_60_to_0_75_count':len(medium),
        'pairs_jaccard_0_45_to_0_60_count':len(gate),
        'high_near_duplicate_pairs_ge_0_75':high[:200],
        'medium_similarity_pairs_0_60_to_0_75':medium[:200],
        'top_similarity_pairs_ge_0_45':near[:300]
      },
      'verdict':verdict,
      'verdict_note':'Read-only audit of stored canonical content and metadata. This verifies structural/evidence/source-metadata compliance and lexical duplicate risk; it does not independently re-adjudicate every medical claim against live external sources.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({
      'verdict':verdict,
      'items':len(items),
      'criteria_pass':out['items_meeting_all_stored_generation_criteria'],
      'criteria_defect_items':len(defect_items),
      'consistency_failures':len(consistency),
      'exact_item_duplicate_groups':len(exact_full_groups),
      'exact_stem_duplicate_groups':len(exact_stem_groups),
      'high_near_duplicate_pairs':len(high),
      'medium_similarity_pairs':len(medium),
      'jaccard_gate_pairs':len(gate)
    },sort_keys=True))

if __name__=='__main__':
    main()
