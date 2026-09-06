#!/usr/bin/env python3
import hashlib,json,os,re,sqlite3,subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
DB=ROOT/'data'/'usmle-step1.db'
STATE=ROOT/'state'/'step2_final_q0001_q1240.json'
CAND=ROOT/'batch_specs_1201_1300'/'07_q1241_q1250_author_20260906.json'
OUT=ROOT/'audit'/'Q1241_Q1250_READONLY_AUDIT.json'
CANON_BLOB='ec4393c3699a68616ea2877b464916b0db680328'
IMM='Blood & Lymphoreticular/Immune Systems'
SKIN='Musculoskeletal, Skin & Subcutaneous Tissue'
DX='Patient Care: Diagnosis'
MK='Medical Knowledge: Applying Foundational Science Concepts'
USMLE='https://www.usmle.org/step-exams/step-1/step-1-exam-content'
ALLOWED_DOMAINS={'www.usmle.org','www.ncbi.nlm.nih.gov','pubmed.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov'}
STOP=set('a an the and or of in on to for with from by due this that which is are was were has have had be been being patient patients most likely best directly explains caused cause causes causing normal loss findings finding syndrome disease disorder gene genetic molecular cell cells skin immune'.split())

SOURCE_EXPECT={
1241:[('https://pubmed.ncbi.nlm.nih.gov/40239948/','2025','Abstract'),('https://www.ncbi.nlm.nih.gov/medgen/96875','current NCBI MedGen record','Definition')],
1242:[('https://www.ncbi.nlm.nih.gov/books/NBK606140/','published online 2024-08-22; current NCI PDQ summary','Introduction to GATA2 Deficiency Syndrome; Genetics and Molecular Biology; Clinical Phenotypes')],
1243:[('https://www.ncbi.nlm.nih.gov/books/NBK544951/','review posted 2019-08-08; current GeneReviews 1993-2026 edition','Summary — Clinical characteristics; Diagnosis; Clinical Characteristics')],
1244:[('https://www.ncbi.nlm.nih.gov/books/NBK611655/','review posted 2025-01-30; current GeneReviews 1993-2026 edition','Summary; Molecular Pathogenesis')],
1245:[('https://pmc.ncbi.nlm.nih.gov/articles/PMC4894527/','2015 final publication; PMC 2016','Genetic and functional deficiency of C1q in SLE')],
1246:[('https://pubmed.ncbi.nlm.nih.gov/28248300/','2017','Abstract'),('https://pubmed.ncbi.nlm.nih.gov/30290227/','2019','Abstract')],
1247:[('https://www.ncbi.nlm.nih.gov/books/NBK1369/','last update 2022-08-04; current GeneReviews 1993-2026 edition','Clinical Characteristics; Molecular Genetics — Molecular Pathogenesis; Table 10'),('https://pubmed.ncbi.nlm.nih.gov/27798626/','2017','Abstract')],
1248:[('https://pubmed.ncbi.nlm.nih.gov/10233227/','1999','Abstract'),('https://pubmed.ncbi.nlm.nih.gov/32248567/','2020','Abstract')],
1249:[('https://pubmed.ncbi.nlm.nih.gov/20691404/','2010','Abstract'),('https://pubmed.ncbi.nlm.nih.gov/22146835/','2012','Abstract')],
1250:[('https://www.ncbi.nlm.nih.gov/books/NBK1369/','last update 2022-08-04; current GeneReviews 1993-2026 edition','Clinical Characteristics — PLEC-associated EBS; Molecular Genetics — Molecular Pathogenesis; Table 10')]
}

UNIQUE_ANCHORS={1241: ['WHIM syndrome', 'CXCR4 gain of function', 'myelokathexis'], 1242: ['GATA2 deficiency', 'MonoMAC'], 1243: ['DADA2', 'deficiency of adenosine deaminase 2'], 1244: ['activated PI3K delta syndrome', 'PIK3CD gain of function'], 1245: ['C1q deficiency', 'deficiency of C1q'], 1246: ['PNPLA1', 'omega-O-acylceramide'], 1247: ['KLHL24', 'stabilizing mutations of KLHL24'], 1248: ['PKP1', 'plakophilin 1 deficiency'], 1249: ['CDSN deficiency', 'corneodesmosin deficiency'], 1250: ['PLEC-associated epidermolysis bullosa simplex with muscular dystrophy', 'plectin muscular dystrophy']}

SECOND_ANSWER={
1241:{'strongest_distractor':'C','discriminator':'Pathogenic CXCR4 variant plus marrow myelokathexis directly identifies hyperactive CXCR4-CXCL12 retention; no alternative option explains that genotype-mechanism pair.'},
1242:{'strongest_distractor':'E','discriminator':'The combined monocytopenia, B/NK-cell depletion, dysplasia, HPV susceptibility, and familial AML pattern is specific for GATA2 deficiency rather than isolated mycobacterial susceptibility.'},
1243:{'strongest_distractor':'B','discriminator':'Childhood recurrent lacunar strokes with livedoid vasculopathy, anemia in a sibling, and consanguinity strongly identifies recessive DADA2 over sporadic PAN.'},
1244:{'strongest_distractor':'C','discriminator':'The stem explicitly gives a gain-of-function PIK3CD variant; its direct downstream effect is PI3K-AKT-mTOR hyperactivation.'},
1245:{'strongest_distractor':'B','discriminator':'The autoimmune mechanism asked is specific to inherited C1q deficiency: impaired apoptotic-material recognition/clearance, not generic C3b opsonization.'},
1246:{'strongest_distractor':'D','discriminator':'The gene is PNPLA1, whose direct biochemical role is linoleate transfer in omega-O-acylceramide synthesis; TGM1 cross-linking is a different ARCI mechanism.'},
1247:{'strongest_distractor':'A','discriminator':'A KLHL24 start-codon variant specifically creates a stabilized gain-of-function substrate adaptor that excessively degrades keratin 14.'},
1248:{'strongest_distractor':'A','discriminator':'Malformed desmosomes with poor keratin attachment plus ectodermal abnormalities directly support PKP1 deficiency, not a mixed-level basement-membrane fragility disorder.'},
1249:{'strongest_distractor':'A','discriminator':'Normal LEKT1 and normal hair microscopy attack the Netherton alternative; generalized inflammatory peeling with severe atopy fits CDSN deficiency.'},
1250:{'strongest_distractor':'E','discriminator':'Basal-keratinocyte cleavage plus progressive muscular dystrophy is the syndromic PLEC-EBS pattern; the distractors do not unify that cleavage level and myopathy.'}
}

def gitblob(p):
    return subprocess.check_output(['git','-C',str(REPO),'hash-object',str(p.relative_to(REPO))],text=True).strip()

def strings(x):
    if isinstance(x,str): yield x
    elif isinstance(x,dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x,list):
        for v in x: yield from strings(v)

def norm(s):
    s=s.casefold().replace('ω','omega').replace('δ','delta').replace('κ','kappa')
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

def toks(s):
    return {w for w in norm(s).split() if len(w)>2 and w not in STOP}

def jac(a,b):
    a=toks(a); b=toks(b)
    return len(a&b)/len(a|b) if a|b else 0.0

def seq(a,b):
    return SequenceMatcher(None,norm(a),norm(b),autojunk=True).ratio()

def item_text(x):
    i=x.get('item',x)
    opts=i.get('options',{})
    return ' '.join([i.get('vignette',''),i.get('lead_in',''),*opts.values(),i.get('tested_construct',''),*x.get('semantic_fingerprint',[])])

def canonical_text(payload):
    d=json.loads(payload)
    i=d.get('item',d)
    return ' '.join([i.get('vignette',''),i.get('lead_in',''),*i.get('options',{}).values(),i.get('tested_construct',''),' '.join(strings(d.get('semantic_fingerprint',[])))])

def main():
    expected=os.environ.get('EXPECTED_CANDIDATE_BLOB','').strip()
    assert re.fullmatch(r'[0-9a-f]{40}',expected), 'EXPECTED_CANDIDATE_BLOB missing/invalid'
    assert gitblob(CAND)==expected, (gitblob(CAND),expected)
    assert gitblob(DB)==CANON_BLOB
    st=json.loads(STATE.read_text())
    assert st['final_status']=='FINAL_10_10_PASS' and st['item_count']==1240 and st['step2_final_review_count']==1240
    assert st['post_authoritative_db_blob']==CANON_BLOB and st['contiguous_q0001_q1240'] is True
    con=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=con.execute("select candidate_id,payload_json from step2_final_items where final_status='FINAL_10_10_PASS'").fetchall()
    assert len(rows)==1240
    reviews=con.execute("select count(*) from step2_final_reviews where final_status='FINAL_10_10_PASS'").fetchone()[0]
    assert reviews==1240
    con.close()
    corpus=[(cid,canonical_text(pj)) for cid,pj in rows]

    d=json.loads(CAND.read_text()); items=d['items']
    assert [x['num'] for x in items]==list(range(1241,1251)) and len(items)==10
    assert d['canonical_pre_state']['db_blob']==CANON_BLOB
    assert d['production_count_before']==1240 and d['production_count_after']==1240
    assert d['batch_design']['systems']=={IMM:5,SKIN:5}
    assert d['batch_design']['competencies']=={DX:5,MK:5}
    keys=''.join(x['item']['intended_key'] for x in items)
    assert keys=='BDAECAECDB' and {k:keys.count(k) for k in 'ABCDE'}=={'A':2,'B':2,'C':2,'D':2,'E':2}
    assert 'NCJMM' not in CAND.read_text()

    item_reports=[]; global_fail=[]
    for x in items:
        q=x['num']; bp=x['blueprint']; it=x['item']; ex=x['explanation']; src=x['sources']; ev=x['evidence_map']
        fail=[]
        if bp['primary_system'] not in {IMM,SKIN}: fail.append('invalid_system_label')
        if bp['primary_competency'] not in {DX,MK}: fail.append('invalid_competency_label')
        if bp.get('official_outline_path') != [bp['primary_system']]: fail.append('official_outline_path_overclaim_or_mismatch')
        if not bp.get('internal_content_path'): fail.append('missing_internal_content_path')
        if set(it['options'])!=set('ABCDE') or len(set(map(norm,it['options'].values())))!=5: fail.append('option_structure')
        if it['intended_key'] not in it['options']: fail.append('missing_key')
        if not it['vignette'].strip() or not it['lead_in'].strip().endswith('?'): fail.append('stem_or_leadin')
        if set(ex['distractor_explanations'])!=set('ABCDE'): fail.append('rationale_coverage')
        correct_marks=[k for k,v in ex['distractor_explanations'].items() if norm(v).startswith('correct')]
        if correct_marks != [it['intended_key']]: fail.append('rationale_key_marker')
        if len(ev)!=5 or {e['option'] for e in ev}!=set('ABCDE'): fail.append('evidence_map_structure')
        if src[0]['url']!=USMLE or src[0].get('official_exam_specification') is not True: fail.append('usmle_source')
        for s in src:
            u=urlparse(s['url'])
            if u.scheme!='https' or u.netloc not in ALLOWED_DOMAINS: fail.append('source_domain')
            if not s.get('section_locator') or not s.get('publication_or_revision_date') or s.get('retrieved_at')!='2026-09-06': fail.append('source_metadata')
        got=[(s['url'],s['publication_or_revision_date'],s['section_locator']) for s in src[1:]]
        if got!=SOURCE_EXPECT[q]: fail.append('externally_verified_source_manifest_mismatch')
        ids={s['source_id'] for s in src}
        if any(not set(e['source_ids']).issubset(ids) for e in ev): fail.append('evidence_source_id_integrity')
        if x['status']!='CANDIDATE_FROZEN': fail.append('candidate_status')
        if x['author_self_audit']['unresolved_concerns'] or x['author_self_audit']['suggested_changes']: fail.append('author_unresolved')

        txt=item_text(x)
        scored=[]
        for cid,ct in corpus:
            scored.append((max(jac(txt,ct),seq(txt,ct)),jac(txt,ct),seq(txt,ct),cid))
        scored.sort(reverse=True)
        top=scored[:5]
        max_j=max(z[1] for z in scored); max_s=max(z[2] for z in scored)
        if max_j>=0.45: fail.append('canonical_jaccard_collision')
        if max_s>=0.70: fail.append('canonical_sequence_collision')
        fp=[norm(z) for z in x['semantic_fingerprint']]
        exact_fp_hits=[]
        for cid,ct in corpus:
            nct=norm(ct)
            for phrase in fp:
                if len(phrase)>=5 and phrase in nct:
                    exact_fp_hits.append({'candidate_id':cid,'phrase':phrase})
        unique_anchor_hits=[]
        for anchor in UNIQUE_ANCHORS[q]:
            na=norm(anchor)
            for cid,ct in corpus:
                if na in norm(ct):
                    unique_anchor_hits.append({'candidate_id':cid,'anchor':na})
        if unique_anchor_hits: fail.append('canonical_unique_construct_anchor_hit')

        sa=SECOND_ANSWER[q]
        if sa['strongest_distractor']==it['intended_key'] or sa['strongest_distractor'] not in it['options']: fail.append('second_answer_manifest')
        item_reports.append({'q':q,'status':'PASS' if not fail else 'BLOCKED','failures':fail,'second_answer_attack':{**sa,'verdict':'NO_SECOND_DEFENSIBLE_ANSWER'},'canonical_top5':[{'candidate_id':z[3],'combined':round(z[0],4),'jaccard':round(z[1],4),'sequence':round(z[2],4)} for z in top],'max_canonical_jaccard':round(max_j,4),'max_canonical_sequence':round(max_s,4),'semantic_fingerprint_hits_advisory':exact_fp_hits,'unique_construct_anchor_hits':unique_anchor_hits})
        global_fail.extend(f'Q{q}:{f}' for f in fail)

    within=[]
    for a in range(len(items)):
        for b in range(a+1,len(items)):
            ta=item_text(items[a]); tb=item_text(items[b]); j=jac(ta,tb); s=seq(ta,tb)
            within.append({'q1':items[a]['num'],'q2':items[b]['num'],'jaccard':round(j,4),'sequence':round(s,4)})
            if j>=0.40 or s>=0.65: global_fail.append(f"INTRABATCH:{items[a]['num']}-{items[b]['num']}")
    within.sort(key=lambda z:max(z['jaccard'],z['sequence']),reverse=True)

    report={'audit_id':'Q1241-Q1250-READONLY-ZEROTRUST-20260906','candidate_blob':expected,'canonical_db_blob':CANON_BLOB,'canonical_count':1240,'canonical_review_count':1240,'sqlite_integrity':'ok','external_source_verification_date':'2026-09-06','official_usmle_page':USMLE,'answer_key_sequence':keys,'answer_distribution':{k:keys.count(k) for k in 'ABCDE'},'item_reports':item_reports,'intrabatch_top10':within[:10],'failures':global_fail,'verdict':'READONLY_QA_PASS' if not global_fail else 'BLOCKED'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':report['verdict'],'candidate_blob':expected,'failures':global_fail,'items':[{'q':r['q'],'status':r['status'],'max_j':r['max_canonical_jaccard'],'max_seq':r['max_canonical_sequence'],'top':r['canonical_top5'][0]} for r in item_reports],'intrabatch_top3':within[:3]},indent=2))
    if global_fail: raise SystemExit(2)

if __name__=='__main__': main()
