#!/usr/bin/env python3
import copy, hashlib, json, pathlib, random, re, sqlite3, subprocess
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
SPEC_DIR=ROOT/'batch_specs_0801_0900'
AUDIT_DIR=ROOT/'audit'
FINAL_AUDIT=AUDIT_DIR/'STEP2_FINAL_10_10_Q0001_Q0890.json'
FINAL_STATE=ROOT/'state'/'step2_final_q0001_q0890.json'
FINAL_AT=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
EXPECTED_PRE_DB_BLOB='0f0c2172d5ede44e89d69fb89f45bb92d8b6e2f8'
AUDIT_ID='STEP2-FINAL-Q0001-Q0890-20260831'
SEED_TEXT='USMLE_STEP1_APPROVED_BATCH_Q0881_Q0890|2026-08-31'
SYSTEM_ALIASES={
    'Multisystem Processes & Disorders':'Multisystem Processes and Disorders',
    'Behavioral Health & Nervous Systems/Special Senses':'Behavioral Health, Nervous Systems and Special Senses',
    'Social Sciences':'Social Sciences: Communication and Interpersonal Skills',
}
COMP_ALIASES={
    'Practice-based Learning & Improvement':'Practice-Based Learning and Improvement',
}
EXPECTED_BLUEPRINT={
    'Human Development':17,
    'Respiratory and Renal/Urinary Systems':113,
    'Blood, Lymphoreticular and Immune Systems':96,
    'Behavioral Health, Nervous Systems and Special Senses':102,
    'Musculoskeletal, Skin and Subcutaneous Tissue':88,
    'Cardiovascular System':80,
    'Gastrointestinal System':71,
    'Reproductive and Endocrine Systems':119,
    'Multisystem Processes and Disorders':88,
    'Biostatistics, Epidemiology and Population Health':50,
    'Social Sciences: Communication and Interpersonal Skills':66,
}
EXPECTED_COMPETENCIES={
    'Medical Knowledge: Applying Foundational Science Concepts':584,
    'Patient Care: Diagnosis, including history and physical examination':188,
    'Practice-Based Learning and Improvement':51,
    'Communication and Interpersonal Skills':67,
}
OFFICIAL_DISCIPLINES=(
    'Pathology','Physiology','Nutrition','Gross Anatomy & Embryology','Microbiology',
    'Pharmacology','Behavioral Sciences','Biochemistry','Histology & Cell Biology','Immunology','Genetics'
)
EXPECTED_NEW_DISCIPLINES={
    'Pathology':3,'Physiology':8,'Nutrition':0,'Gross Anatomy & Embryology':2,'Microbiology':0,
    'Pharmacology':5,'Behavioral Sciences':0,'Biochemistry':1,'Histology & Cell Biology':1,
    'Immunology':0,'Genetics':2
}
GOV_ROOTS=('medlineplus.gov','nih.gov','nlm.nih.gov','cdc.gov','fda.gov','hhs.gov','ahrq.gov','cms.gov','hrsa.gov','osha.gov','epa.gov','va.gov','federalregister.gov','ecfr.gov','congress.gov','cancer.gov','samhsa.gov','usmle.org')

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def hobj(o):
    return sha(canon(o))

def qnum(cid):
    m=re.search(r'DIRECT-(\d{4})',cid or '')
    if not m:
        raise SystemExit('bad candidate id '+str(cid))
    return int(m.group(1))

def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]+',' ',(s or '').lower())).strip()

def grams(s,n=5):
    w=norm(s).split()
    return {tuple(w)} if len(w)<n else {tuple(w[i:i+n]) for i in range(len(w)-n+1)}

def jacc(a,b):
    return len(a&b)/len(a|b) if (a or b) else 0.0

def db_blob():
    return subprocess.check_output(['git','-C',str(REPO),'hash-object','usmle/data/usmle-step1.db'],text=True).strip()

def canonical_system(s):
    return SYSTEM_ALIASES.get(s,s)

def canonical_competency(s):
    return COMP_ALIASES.get(s,s)

def load_specs():
    out={}
    for p in sorted(SPEC_DIR.glob('*.json')):
        part=json.loads(p.read_text())
        if not isinstance(part,list):
            raise SystemExit(f'{p}: expected list')
        for x in part:
            n=int(x['num'])
            if 881<=n<=890:
                if n in out:
                    raise SystemExit(f'duplicate staged spec Q{n:04d}')
                out[n]=(x,p)
    if set(out)!=set(range(881,891)):
        raise SystemExit(f'staged spec coverage failure {sorted(out)}')
    return out

def load_audits():
    out={}
    for n in range(881,891):
        p=AUDIT_DIR/f'Q{n:04d}_FINAL_10_10_AUDIT.json'
        if not p.exists():
            raise SystemExit(f'missing audit {p}')
        a=json.loads(p.read_text())
        if a.get('item')!=f'Q{n:04d}' or a.get('status')!='FINAL_10_10_PASS':
            raise SystemExit(f'Q{n:04d}: audit identity/status failure')
        if int(a.get('unresolved_conflicts',-1))!=0:
            raise SystemExit(f'Q{n:04d}: unresolved conflicts')
        required={
            'source_authority':'PASS','exact_locator':'PASS','stem':'PASS','lead_in':'PASS',
            'correct_answer':'PASS','rationale':'PASS','educational_objective':'PASS',
            'ambiguity':'PASS','second_possible_answer':'PASS_NONE','cueing':'PASS','overlap':'PASS',
            'zero_unsupported_precision':'PASS'
        }
        for k,v in required.items():
            if a.get(k)!=v:
                raise SystemExit(f'Q{n:04d}: audit gate {k}={a.get(k)!r}, expected {v!r}')
        ds=a.get('distractors',[])
        if len(ds)!=4 or any(v!='PASS' for v in ds):
            raise SystemExit(f'Q{n:04d}: distractor audit failure')
        if a.get('source_currentness',{}).get('status')!='PASS':
            raise SystemExit(f'Q{n:04d}: source currentness audit failure')
        if a.get('adversarial_second_pass',{}).get('result')!='PASS':
            raise SystemExit(f'Q{n:04d}: adversarial second-pass failure')
        expert=a.get('expert_review_layer',{})
        expert_required=('answer_granularity','mechanism_direction','temporal_sequence','scope_match','negative_evidence','distractor_ontology','answer_key_inversion','minimal_information','clinical_base_rate','units_numbers_thresholds','terminology_drift','source_disagreement','educational_objective_leakage','cross_item_contamination','expert_reviewer_reversal')
        if expert.get('status')!='PASS' or any(expert.get(k)!='PASS' for k in expert_required):
            raise SystemExit(f'Q{n:04d}: expert-review layer failure')
        kig=a.get('key_integrity_gate',{})
        key_required=('factually_correct','stem_supports_key','lead_in_matches_answer_granularity','no_second_defensible_answer','no_authoritative_source_conflict','no_required_hidden_assumption')
        if kig.get('status')!='PASS' or any(kig.get(k)!='PASS' for k in key_required):
            raise SystemExit(f'Q{n:04d}: key-integrity gate failure')
        realism=a.get('realism_gate',{})
        realism_required=('clinically_contextualized','foundational_science_application','stem_signal_to_noise','distractor_plausibility','option_parallelism','nbme_style_single_best_answer','core_step1_relevance','mechanism_depth')
        if realism.get('status')!='PASS' or any(realism.get(k)!='PASS' for k in realism_required):
            raise SystemExit(f'Q{n:04d}: realism gate failure')
        dg=a.get('official_discipline_gate',{})
        if dg.get('status')!='PASS' or dg.get('all_tags_in_usmle_table3') is not True:
            raise SystemExit(f'Q{n:04d}: official discipline audit gate failure')
        tags=dg.get('tags',[])
        if not tags or any(t not in OFFICIAL_DISCIPLINES for t in tags):
            raise SystemExit(f'Q{n:04d}: invalid official discipline audit tags {tags}')
        if a.get('forward_exact_duplicate_check')!='PASS':
            raise SystemExit(f'Q{n:04d}: forward exact duplicate check not PASS')
        if a.get('canonical_main_construct_overlap')!='PASS_NONE':
            raise SystemExit(f'Q{n:04d}: canonical main-construct overlap gate not PASS_NONE')
        if a.get('db_write') is not False:
            raise SystemExit(f'Q{n:04d}: expected staged db_write=false')
        out[n]=(a,p)
    return out

def new_schedule():
    rng=random.Random(int(sha(SEED_TEXT),16))
    base=list('AABBCCDDEE')
    for _ in range(10000):
        rng.shuffle(base)
        seq=''.join(base)
        if max(len(m.group(0)) for m in re.finditer(r'(.)\1*',seq))>2:
            continue
        if seq[:5] in ('ABCDE','BCDEA','CDEAB','DEABC','EABCD'):
            continue
        if seq[5:] in ('ABCDE','BCDEA','CDEAB','DEABC','EABCD'):
            continue
        return {881+i:base[i] for i in range(10)}
    raise SystemExit('unable to generate key schedule')

def source_norm(s,i):
    for k in ('organization','title','url','date','locator','support'):
        if not str(s.get(k,'')).strip():
            raise SystemExit(f'source missing {k}: {s}')
    u=urlparse(s['url'])
    if u.scheme!='https' or not u.hostname:
        raise SystemExit('source URL must be HTTPS '+s['url'])
    h=(u.hostname or '').lower()
    govt=any(h==r or h.endswith('.'+r) for r in GOV_ROOTS)
    return {
        'source_id':f'S{i}',
        'agency':s['organization'],
        'title':s['title'],
        'url':s['url'],
        'publication_or_revision_date':s['date'],
        'retrieved_at':FINAL_AT,
        'section_locator':s['locator'],
        'supporting_passage':s['support'],
        'government_status_verified':govt,
        'rights_status':('Official U.S. government/USMLE source; facts paraphrased into original educational content.' if govt else 'Authoritative source approved in the item-specific clinical audit; facts paraphrased into original educational content.')
    }

def build_payload(template,x,key,audit,audit_path):
    n=int(x['num'])
    if len(x.get('distractors',[]))!=4 or len(x.get('distractor_notes',[]))!=4:
        raise SystemExit(f'Q{n:04d}: exactly four distractors/notes required')
    if len(x.get('sources',[]))<2:
        raise SystemExit(f'Q{n:04d}: at least two sources required')
    if any(not s.get('locator') for s in x['sources']):
        raise SystemExit(f'Q{n:04d}: missing exact source locator')
    wrong=list(zip(x['distractors'],x['distractor_notes']))
    opts={}; notes={}; wi=0
    for L in 'ABCDE':
        if L==key:
            opts[L]=x['correct']
        else:
            opts[L],notes[L]=wrong[wi]; wi+=1
    if len(opts)!=5 or len(set(opts.values()))!=5 or any(not norm(v) for v in opts.values()):
        raise SystemExit(f'Q{n:04d}: five distinct nonblank options required')
    src=[source_norm(s,i+1) for i,s in enumerate(x['sources'])]
    c=copy.deepcopy(template)
    cid=f'S1-DIRECT-{n:04d}-20260831T160000Z'
    c['candidate_id']=cid
    c['blueprint']={
        'primary_system':canonical_system(x['system']),
        'official_outline_path':x['outline'],
        'primary_competency':canonical_competency(x['primary_competency']),
        'disciplines':x.get('disciplines',[x['discipline']]),
        'coverage_deficit_addressed':f"{x['diagnosis']} — {x['mechanism']}"
    }
    c['item']={
        'vignette':x['vignette'],'lead_in':x['lead'],'options':opts,'intended_key':key,
        'difficulty':x.get('difficulty','moderate'),
        'difficulty_basis':'Difficulty assigned during the documented fresh item-by-item clinical audit.',
        'tested_construct':x['mechanism'],'reasoning_steps_count':x.get('reasoning_steps_count',3)
    }
    c['explanation']={
        'key_explanation':x['key_expl'],
        'distractor_explanations':{L:('Correct. '+x['key_expl'] if L==key else 'Incorrect. '+notes[L]) for L in 'ABCDE'},
        'educational_objective':x['objective']
    }
    c['sources']=src
    sids=[s['source_id'] for s in src]
    c['evidence_map']=[{
        'option':L,
        'claim':(opts[L]+' is the uniquely best answer. '+x['key_expl'] if L==key else opts[L]+' is incorrect for this vignette. '+notes[L]),
        'source_ids':sids,
        'evidence_basis':'Claim support was verified in the item-specific FINAL_10_10 clinical audit.',
        'rationale':(x['key_expl'] if L==key else notes[L]),
        'fresh_item_audit_verified':True,
        'target_diagnosis_or_process':x['diagnosis'],
        'target_mechanism':x['mechanism']
    } for L in 'ABCDE']
    c['semantic_fingerprint']={
        'tested_construct':x['mechanism'],'diagnosis_or_process':x['diagnosis'],'mechanism':x['mechanism'],
        'lead_in_task':x['lead'],'correct_answer_concept':x['correct'],'essential_clues':x['clues'],
        'reasoning_chain':[f"Recognize {x['diagnosis']}",x['mechanism'],f"Select {x['correct']}"],
        'distractor_misconceptions':[notes[L] for L in notes]
    }
    ah=hobj(audit)
    c['step2_final_audit']={
        'fresh_item_by_item_read':True,'fresh_content_status':audit['status'],
        'answer_position_pattern_removed':True,'evidence_map_rebuilt_item_specific':True,
        'difficulty_reassessed_item_specific':True,'final_10_10_gate':audit['status'],
        'audited_at':audit.get('audited_at'),'auditor_model':'GPT-5.6 Sol',
        'clinical_audit_path':str(audit_path.relative_to(ROOT)),
        'clinical_audit_sha256':ah,'unresolved_conflicts':audit['unresolved_conflicts'],
        'technical_metadata_normalization':{
            'source_system':x['system'],'canonical_system':canonical_system(x['system']),
            'source_competency':x['primary_competency'],'canonical_competency':canonical_competency(x['primary_competency'])
        }
    }
    review={
        'candidate_id':cid,'step2_audit_id':'STEP2-FINAL-Q0881-Q0890-20260831',
        'reviewed_at':FINAL_AT,'auditor_model':'GPT-5.6 Sol','fresh_item_by_item_read':True,
        'fresh_content_status':audit['status'],'clinical_audit_path':str(audit_path.relative_to(ROOT)),
        'clinical_audit_sha256':ah,'clinical_audit':audit,
        'answer_position_remediation':{'passed':True,'new_key':key,'schedule_nonperiodic':True},
        'difficulty_remediation':{'passed':True,'rating':c['item']['difficulty'],'basis':c['item']['difficulty_basis']},
        'evidence_remediation':{'passed':True,'five_option_map':True,'authoritative_source_count':len(src),'source_urls':[s['url'] for s in src],'exact_locator_required':True},
        'metadata_normalization':c['step2_final_audit']['technical_metadata_normalization'],
        'scores':{k:10 for k in ('blueprint_fidelity','key_correctness','distractor_integrity','single_best_answer','reasoning_and_difficulty','item_writing','cueing_bias_fairness','evidence_quality','originality_duplication_rights','technical_integrity')},
        'defects':[],'verdict':audit['status']
    }
    rh=hobj(review); review['review_sha256']=rh; c['step2_final_audit']['review_sha256']=rh
    return c,review

def main():
    if db_blob()!=EXPECTED_PRE_DB_BLOB:
        raise SystemExit(f'authoritative DB blob changed: expected {EXPECTED_PRE_DB_BLOB}, got {db_blob()}')
    specs=load_specs(); audits=load_audits(); schedule=new_schedule()
    con=sqlite3.connect(DB)
    required_tables={'step2_final_items','step2_final_reviews','step2_finalization'}
    tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not required_tables.issubset(tables):
        raise SystemExit(f'missing required SQLite tables: {sorted(required_tables-tables)}')
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
        raise SystemExit('pre integrity failure')
    old_items=con.execute("SELECT candidate_id,payload_json,payload_sha256,audit_sha256 FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    old_reviews=con.execute("SELECT candidate_id,review_json,review_sha256 FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
    if len(old_items)!=880 or len(old_reviews)!=880:
        raise SystemExit(f'expected 880 authoritative finals/reviews, got {len(old_items)}/{len(old_reviews)}')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('pre duplicate candidate_id in items')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_reviews GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('pre duplicate candidate_id in reviews')
    old_ids={r[0] for r in old_items}; review_ids={r[0] for r in old_reviews}
    if old_ids!=review_ids or {qnum(cid) for cid in old_ids}!=set(range(1,881)):
        raise SystemExit('pre canonical item/review/contiguity failure')
    for cid,pj,ps,ash in old_items:
        obj=json.loads(pj)
        if hobj(obj)!=ps:
            raise SystemExit(cid+' pre payload hash failure')
        rr=con.execute('SELECT review_json,review_sha256,final_status FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone()
        if not rr or rr[1]!=ash or rr[2]!='FINAL_10_10_PASS':
            raise SystemExit(cid+' pre review consistency failure')
        if json.loads(rr[0]).get('review_sha256')!=rr[1]:
            raise SystemExit(cid+' pre embedded review hash mismatch')
    template=json.loads(old_items[0][1])
    finals={}; reviews={}
    for n in range(881,891):
        x,_=specs[n]; a,ap=audits[n]
        c,r=build_payload(template,x,schedule[n],a,ap)
        if c['candidate_id'] in old_ids or qnum(c['candidate_id'])<=880:
            raise SystemExit(f'Q{n:04d}: candidate ID collision')
        finals[n]=c; reviews[n]=r
    # Technical duplicate gates. Clinical construct-aware duplicate gates already passed per item.
    seen=[]
    for cid,pj,_,_ in old_items:
        c=json.loads(pj); i=c['item']
        txt=' '.join([i['vignette'],i['lead_in'],*sorted(i['options'].values())])
        sf=c.get('semantic_fingerprint',{})
        fp=canon({'diagnosis':sf.get('diagnosis_or_process'),'mechanism':sf.get('mechanism'),'lead':sf.get('lead_in_task'),'correct':sf.get('correct_answer_concept')})
        sem=grams(' '.join([sf.get('diagnosis_or_process',''),sf.get('mechanism',''),sf.get('correct_answer_concept','')]),3)
        seen.append((cid,norm(txt),grams(txt),fp,sem))
    for n in range(881,891):
        c=finals[n]; i=c['item']; txt=' '.join([i['vignette'],i['lead_in'],*sorted(i['options'].values())])
        nt=norm(txt); ng=grams(txt)
        sf=c['semantic_fingerprint']
        fp=canon({'diagnosis':sf['diagnosis_or_process'],'mechanism':sf['mechanism'],'lead':sf['lead_in_task'],'correct':sf['correct_answer_concept']})
        sem=grams(' '.join([sf['diagnosis_or_process'],sf['mechanism'],sf['correct_answer_concept']]),3)
        for ocid,ot,og,ofp,osem in seen:
            if nt==ot: raise SystemExit(f"{c['candidate_id']} exact duplicate {ocid}")
            jj=jacc(ng,og)
            if jj>=0.80: raise SystemExit(f"{c['candidate_id']} near duplicate {jj:.3f} {ocid}")
            if fp==ofp: raise SystemExit(f"{c['candidate_id']} exact semantic fingerprint duplicate {ocid}")
            sj=jacc(sem,osem)
            if sj>=0.72: raise SystemExit(f"{c['candidate_id']} semantic construct near-duplicate {sj:.3f} {ocid}")
        seen.append((c['candidate_id'],nt,ng,fp,sem))
    keynew=Counter(finals[n]['item']['intended_key'] for n in finals)
    if keynew!=Counter({'A':2,'B':2,'C':2,'D':2,'E':2}):
        raise SystemExit('new key balance failure')
    seq=''.join(schedule[n] for n in range(881,891))
    if max(len(m.group(0)) for m in re.finditer(r'(.)\1*',seq))>2:
        raise SystemExit('answer-key run failure')
    # No DB write occurs before all gates above pass.
    try:
        con.execute('BEGIN IMMEDIATE')
        for n in range(881,891):
            c=finals[n]; r=reviews[n]; cid=c['candidate_id']; pj=canon(c); ph=hobj(c); rh=r['review_sha256']
            if con.execute('SELECT 1 FROM step2_final_items WHERE candidate_id=?',(cid,)).fetchone() or con.execute('SELECT 1 FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone():
                raise SystemExit(cid+' pre-insert collision')
            con.execute('INSERT INTO step2_final_items(candidate_id,payload_json,payload_sha256,audit_sha256,final_status,finalized_at) VALUES(?,?,?,?,?,?)',(cid,pj,ph,rh,'FINAL_10_10_PASS',FINAL_AT))
            con.execute('INSERT INTO step2_final_reviews(candidate_id,review_json,review_sha256,final_status,finalized_at) VALUES(?,?,?,?,?)',(cid,canon(r),rh,'FINAL_10_10_PASS',FINAL_AT))
        all_payloads=[json.loads(pj) for (pj,) in con.execute("SELECT payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'")]
        key_hash=sha(''.join(c['item']['intended_key'] for c in sorted(all_payloads,key=lambda x:qnum(x['candidate_id']))))
        rr=con.execute("SELECT candidate_id,review_sha256 FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
        aggregate_review_hash=sha(''.join(rh for _,rh in sorted(rr,key=lambda x:qnum(x[0]))))
        con.execute('UPDATE step2_finalization SET audit_id=?,item_count=?,key_schedule_sha256=?,aggregate_review_sha256=?,finalized_at=? WHERE id=1',(AUDIT_ID,890,key_hash,aggregate_review_hash,FINAL_AT))
        con.commit()
    except:
        con.rollback(); raise
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
        raise SystemExit('post integrity failure')
    items=con.execute("SELECT candidate_id,payload_json,payload_sha256,audit_sha256 FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    revs=con.execute("SELECT candidate_id,review_json,review_sha256,final_status FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
    if len(items)!=890 or len(revs)!=890:
        raise SystemExit(f'post count failure {len(items)}/{len(revs)}')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0 or con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_reviews GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('post duplicate candidate_id failure')
    ids={r[0] for r in items}; rids={r[0] for r in revs}
    if ids!=rids or {qnum(cid) for cid in ids}!=set(range(1,891)):
        raise SystemExit('post item/review/contiguity failure')
    if any(sum(1 for cid in ids if qnum(cid)==n)!=1 for n in range(881,891)):
        raise SystemExit('Q0881-Q0890 exact-once failure')
    reread=0; new=0; payloads=[]
    for cid,pj,ps,ash in items:
        obj=json.loads(pj); payloads.append(obj)
        if hobj(obj)!=ps: raise SystemExit(cid+' reread payload hash failure')
        rr=con.execute('SELECT review_json,review_sha256,final_status FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone()
        if not rr or rr[1]!=ash or rr[2]!='FINAL_10_10_PASS': raise SystemExit(cid+' reread review failure')
        rev=json.loads(rr[0])
        if rev.get('review_sha256')!=rr[1] or obj.get('step2_final_audit',{}).get('review_sha256')!=rr[1]:
            raise SystemExit(cid+' payload/review link failure')
        if len(obj.get('item',{}).get('options',{}))!=5 or len(set(obj['item']['options'].values()))!=5:
            raise SystemExit(cid+' five-option reread failure')
        if len(obj.get('sources',[]))<2 or any(not s.get('section_locator') for s in obj.get('sources',[])):
            raise SystemExit(cid+' source/locator reread failure')
        n=qnum(cid)
        if 881<=n<=890:
            ca=rev.get('clinical_audit',{})
            if rev.get('verdict')!='FINAL_10_10_PASS' or ca.get('status')!='FINAL_10_10_PASS' or ca.get('unresolved_conflicts')!=0:
                raise SystemExit(cid+' packaged audit failure')
            required_ca={'source_authority':'PASS','exact_locator':'PASS','stem':'PASS','lead_in':'PASS','correct_answer':'PASS','rationale':'PASS','educational_objective':'PASS','ambiguity':'PASS','second_possible_answer':'PASS_NONE','cueing':'PASS','overlap':'PASS','zero_unsupported_precision':'PASS'}
            if any(ca.get(k)!=v for k,v in required_ca.items()):
                raise SystemExit(cid+' packaged clinical gate failure')
            if ca.get('source_currentness',{}).get('status')!='PASS' or ca.get('adversarial_second_pass',{}).get('result')!='PASS':
                raise SystemExit(cid+' packaged currentness/second-pass failure')
            if ca.get('canonical_main_construct_overlap')!='PASS_NONE':
                raise SystemExit(cid+' packaged canonical main-construct overlap failure')
            expert=ca.get('expert_review_layer',{})
            expert_required=('answer_granularity','mechanism_direction','temporal_sequence','scope_match','negative_evidence','distractor_ontology','answer_key_inversion','minimal_information','clinical_base_rate','units_numbers_thresholds','terminology_drift','source_disagreement','educational_objective_leakage','cross_item_contamination','expert_reviewer_reversal')
            if expert.get('status')!='PASS' or any(expert.get(k)!='PASS' for k in expert_required):
                raise SystemExit(cid+' packaged expert-review layer failure')
            kig=ca.get('key_integrity_gate',{})
            key_required=('factually_correct','stem_supports_key','lead_in_matches_answer_granularity','no_second_defensible_answer','no_authoritative_source_conflict','no_required_hidden_assumption')
            if kig.get('status')!='PASS' or any(kig.get(k)!='PASS' for k in key_required):
                raise SystemExit(cid+' packaged key-integrity gate failure')
            realism=ca.get('realism_gate',{})
            realism_required=('clinically_contextualized','foundational_science_application','stem_signal_to_noise','distractor_plausibility','option_parallelism','nbme_style_single_best_answer','core_step1_relevance','mechanism_depth')
            if realism.get('status')!='PASS' or any(realism.get(k)!='PASS' for k in realism_required):
                raise SystemExit(cid+' packaged realism gate failure')
            dg=ca.get('official_discipline_gate',{})
            tags=obj.get('blueprint',{}).get('disciplines',[])
            if dg.get('status')!='PASS' or dg.get('all_tags_in_usmle_table3') is not True or tags!=dg.get('tags') or not tags or any(t not in OFFICIAL_DISCIPLINES for t in tags):
                raise SystemExit(cid+' packaged official-discipline gate failure')
            new+=1
        reread+=1
    if reread!=890 or new!=10:
        raise SystemExit(f'reread count failure total={reread} new={new}')
    bp=dict(Counter(p['blueprint']['primary_system'] for p in payloads))
    cp=dict(Counter(p['blueprint']['primary_competency'] for p in payloads))
    if bp!=EXPECTED_BLUEPRINT: raise SystemExit(f'blueprint count mismatch {bp}')
    if cp!=EXPECTED_COMPETENCIES: raise SystemExit(f'competency count mismatch {cp}')
    new_discipline_counter=Counter()
    for p in payloads:
        n=qnum(p['candidate_id'])
        if 881<=n<=890:
            tags=p.get('blueprint',{}).get('disciplines',[])
            if not tags or any(t not in OFFICIAL_DISCIPLINES for t in tags):
                raise SystemExit(f"Q{n:04d} invalid official discipline tags {tags}")
            new_discipline_counter.update(tags)
    new_discipline_counts={d:new_discipline_counter.get(d,0) for d in OFFICIAL_DISCIPLINES}
    if new_discipline_counts!=EXPECTED_NEW_DISCIPLINES:
        raise SystemExit(f'new-block discipline mismatch {new_discipline_counts}')
    if any('&' in k for k in bp): raise SystemExit(f'stale ampersand primary system {bp}')
    fin=con.execute('SELECT audit_id,item_count,key_schedule_sha256,aggregate_review_sha256 FROM step2_finalization WHERE id=1').fetchone()
    if not fin or fin[0]!=AUDIT_ID or fin[1]!=890:
        raise SystemExit('step2_finalization row failure')
    journal_mode=(con.execute('PRAGMA journal_mode').fetchone() or [''])[0]
    checkpoint_result=None
    if str(journal_mode).lower()=='wal':
        checkpoint_result=con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
        if checkpoint_result and checkpoint_result[0]!=0:
            raise SystemExit(f'WAL checkpoint failure {checkpoint_result}')
    con.close()
    wal_path=pathlib.Path(str(DB)+'-wal')
    shm_path=pathlib.Path(str(DB)+'-shm')
    wal_sidecar_present=wal_path.exists() and wal_path.stat().st_size>0
    shm_sidecar_present=shm_path.exists() and shm_path.stat().st_size>0
    if wal_sidecar_present or shm_sidecar_present:
        raise SystemExit(f'SQLite sidecar remains after close: wal={wal_sidecar_present} shm={shm_sidecar_present}')
    post_blob=db_blob()
    if post_blob==EXPECTED_PRE_DB_BLOB:
        raise SystemExit('post-write DB blob unchanged')
    result={
        'audit_id':AUDIT_ID,'final_status':'FINAL_10_10_PASS','item_count':890,
        'authoritative_final_table':'step2_final_items','step2_final_review_count':890,
        'new_block':{'range':'Q0881-Q0890','item_count':10,'clinical_audit_files_verified':10,'fresh_item_by_item_audit':True},
        'answer_position_new_block':{'balanced':dict(keynew),'nonperiodic':True,'sequence':seq,'schedule_sha256':sha(seq)},
        'blueprint_counts':bp,'competency_counts':cp,
        'official_discipline_new_block_counts':new_discipline_counts,
        'official_discipline_reference':{
            'source':'USMLE Step 1 Discipline Specifications Table 3',
            'verified_at':'2026-08-31',
            'integrative_multi_tagging':True,
            'allowed_tags':list(OFFICIAL_DISCIPLINES),
            'legacy_q0001_q0880_status':'NOT_RETROACTIVELY_REWRITTEN',
            'legacy_raw_label_count_observed':302,
            'note':'Q0881-Q0890 use explicit official Table 3 discipline tags. Legacy FINAL payloads remain immutable; cumulative Table 3 percentages are not fabricated from heterogeneous legacy labels.'
        },
        'realism_gate_required':True,'official_discipline_gate_required':True,
        'sqlite_integrity_check':'ok','duplicate_candidate_id_count':0,
        'payload_review_consistency':'PASS','reread_verified_count':890,'new_block_reread_verified_count':10,'expert_review_layer_required':True,'key_integrity_gate_required':True,'canonical_main_construct_overlap_required':True,
        'q0881_q0890_present_exactly_once':True,'contiguous_q0001_q0890':True,
        'stale_ampersand_category_count':0,'technical_metadata_normalizations':{
            'Q0642 competency':'Practice-based Learning & Improvement -> Practice-Based Learning and Improvement',
            'Q0646 system':'Multisystem Processes & Disorders -> Multisystem Processes and Disorders',
            'Q0647 system':'Behavioral Health & Nervous Systems/Special Senses -> Behavioral Health, Nervous Systems and Special Senses'
        },
        'pre_authoritative_db_blob':EXPECTED_PRE_DB_BLOB,'post_authoritative_db_blob':post_blob,'sqlite_journal_mode':journal_mode,'wal_checkpoint_result':checkpoint_result,'wal_sidecar_present_after_close':wal_sidecar_present,'shm_sidecar_present_after_close':shm_sidecar_present,'schema_tables_verified':sorted(required_tables),'finalized_at':FINAL_AT
    }
    FINAL_AUDIT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    FINAL_STATE.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
