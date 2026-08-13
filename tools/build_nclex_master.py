#!/usr/bin/env python3
from __future__ import annotations
import json, re, sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
NGN_DB = ROOT / 'nclex ngn bank 75of75 ALL7formats FINAL.db'
V2_DB = ROOT / 'nclex question bank v2 inprogress 5.db'
OVERRIDE_FILES = sorted((ROOT / 'data').glob('clinical_overrides_*.json'))
OUT_DB = ROOT / 'NCLEX_COMMERCIAL_MASTER_CURRENT.db'
OUT_REPORT = ROOT / 'NCLEX_COMMERCIAL_MASTER_CURRENT_AUDIT.md'

BLUEPRINT = [
    (2,'MGMT_CARE','Management of Care',15.0,21.0,18.0,1),
    (3,'SAFETY_INFECTION','Safety & Infection Prevention and Control',10.0,16.0,13.0,2),
    (4,'HEALTH_PROMO','Health Promotion and Maintenance',6.0,12.0,9.0,3),
    (5,'PSYCHOSOCIAL','Psychosocial Integrity',6.0,12.0,9.0,4),
    (7,'BASIC_CARE','Basic Care and Comfort',6.0,12.0,9.0,5),
    (8,'PHARM','Pharmacological and Parenteral Therapies',13.0,19.0,16.0,6),
    (9,'RISK_REDUCTION','Reduction of Risk Potential',9.0,15.0,12.0,7),
    (10,'PHYS_ADAPT','Physiological Adaptation',11.0,17.0,14.0,8),
]
BP_BY_ID = {x[0]: x for x in BLUEPRINT}
RENDERER = {
    'highlight': ('highlight',1,'A'),
    'extended_multiple_response': ('multiple_response',1,'B'),
    'matrix_grid': ('matrix',2,None),
    'bowtie': ('bow_tie',3,None),
    'cloze_dropdown': ('cloze',4,None),
    'extended_drag_drop': ('ordered_response',5,None),
    'trend': ('trend',6,None),
}


def jdump(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',',':'))

def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',(s or '').lower())).strip()

def rowdict(row):
    return {k: row[k] for k in row.keys()}

def open_row(path):
    c=sqlite3.connect(path); c.row_factory=sqlite3.Row; return c

def create_schema(con):
    con.executescript('''
    PRAGMA foreign_keys=ON;
    CREATE TABLE bank_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE nclex_2026_blueprint(
      category_id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, client_need TEXT UNIQUE NOT NULL,
      weight_min REAL NOT NULL, weight_max REAL NOT NULL, midpoint REAL NOT NULL, official_order INTEGER NOT NULL);
    CREATE TABLE case_studies(
      case_uid TEXT PRIMARY KEY, source_case_id INTEGER UNIQUE NOT NULL, category_id INTEGER NOT NULL,
      client_need TEXT NOT NULL, specialty TEXT, setting TEXT, client_profile TEXT NOT NULL,
      stage1_scenario TEXT NOT NULL, stage2_scenario TEXT, stage3_scenario TEXT, difficulty TEXT,
      source_name TEXT, source_url TEXT, source_verified_flag INTEGER NOT NULL DEFAULT 0,
      source_licensing_status TEXT NOT NULL DEFAULT 'USER_DECLARED_OWNED_AI_CREATED',
      clinical_qa_status TEXT NOT NULL DEFAULT 'NOT_AUDITED', raw_json TEXT NOT NULL);
    CREATE TABLE questions(
      question_uid TEXT PRIMARY KEY, source_bank TEXT NOT NULL, source_table TEXT NOT NULL,
      source_id INTEGER NOT NULL, mode TEXT NOT NULL, case_uid TEXT, original_sequence INTEGER,
      official_case_slot INTEGER, slot_variant TEXT, category_id INTEGER NOT NULL, client_need TEXT NOT NULL,
      specialty TEXT, difficulty TEXT, cjmm_skill TEXT, item_type_raw TEXT NOT NULL, renderer_type TEXT NOT NULL,
      stem TEXT NOT NULL, item_data_json TEXT NOT NULL, correct_answer_json TEXT NOT NULL,
      rationale TEXT NOT NULL, scoring_rule TEXT, source_name TEXT, source_detail TEXT, source_url TEXT,
      source_verified_flag INTEGER NOT NULL DEFAULT 0, structural_status TEXT NOT NULL,
      clinical_qa_status TEXT NOT NULL DEFAULT 'NOT_AUDITED',
      source_licensing_status TEXT NOT NULL DEFAULT 'USER_DECLARED_OWNED_AI_CREATED',
      commercial_release_ready INTEGER NOT NULL DEFAULT 0, editorial_priority TEXT NOT NULL DEFAULT 'NORMAL',
      editorial_flags_json TEXT NOT NULL DEFAULT '[]', stable_sort_key TEXT NOT NULL, raw_json TEXT NOT NULL,
      FOREIGN KEY(case_uid) REFERENCES case_studies(case_uid));
    CREATE TABLE audit_issues(
      issue_id INTEGER PRIMARY KEY AUTOINCREMENT, question_uid TEXT, case_uid TEXT,
      severity TEXT NOT NULL, issue_code TEXT NOT NULL, detail TEXT NOT NULL);
    CREATE TABLE test_generation_rules(rule_key TEXT PRIMARY KEY,rule_value TEXT NOT NULL,note TEXT NOT NULL);
    CREATE TABLE option_length_qc(
      question_uid TEXT PRIMARY KEY, lengths_json TEXT NOT NULL, min_chars INTEGER NOT NULL,
      max_chars INTEGER NOT NULL, max_min_ratio REAL NOT NULL, correct_option TEXT NOT NULL,
      correct_length_rank INTEGER NOT NULL, correct_is_extreme INTEGER NOT NULL,
      qc_status TEXT NOT NULL, qc_note TEXT NOT NULL);
    CREATE TABLE clinical_audit_log(
      audit_id INTEGER PRIMARY KEY AUTOINCREMENT, question_uid TEXT NOT NULL, source_id INTEGER NOT NULL,
      audit_date TEXT NOT NULL, audit_version TEXT NOT NULL, old_stem TEXT NOT NULL,
      old_options_json TEXT NOT NULL, old_correct_answer_json TEXT NOT NULL, old_rationale TEXT NOT NULL,
      new_stem TEXT NOT NULL, new_options_json TEXT NOT NULL, new_correct_answer_json TEXT NOT NULL,
      new_rationale TEXT NOT NULL, source_name TEXT, source_url TEXT, source_detail TEXT,
      findings_json TEXT NOT NULL, reviewer TEXT NOT NULL);
    CREATE INDEX idx_questions_client_need ON questions(client_need);
    CREATE INDEX idx_questions_case ON questions(case_uid,official_case_slot,slot_variant);
    CREATE INDEX idx_questions_renderer ON questions(renderer_type);
    CREATE INDEX idx_questions_structural ON questions(structural_status);
    CREATE INDEX idx_questions_sort ON questions(stable_sort_key);
    ''')


def validate_ngn(item_type, data, ans):
    flags=[]
    if item_type=='highlight':
        if not isinstance(data.get('passage'),str) or not isinstance(ans.get('correct_phrases'),list): flags.append('INVALID_HIGHLIGHT_SCHEMA')
    elif item_type=='extended_multiple_response':
        selected = ans.get('correct_indices') if isinstance(ans,dict) else None
        if selected is None and isinstance(ans,dict): selected=ans.get('selected')
        if not isinstance(data.get('options'),list) or not isinstance(selected,list): flags.append('INVALID_MULTI_RESPONSE_SCHEMA')
    elif item_type=='matrix_grid':
        if not isinstance(data.get('rows'),list) or not isinstance(data.get('columns'),list) or not isinstance(ans,dict): flags.append('INVALID_MATRIX_SCHEMA')
    elif item_type=='bowtie':
        if not {'condition_options','left_options','right_options'}.issubset(data) or not {'condition','left','right'}.issubset(ans): flags.append('INVALID_BOWTIE_SCHEMA')
    elif item_type=='cloze_dropdown':
        if not isinstance(data.get('template'),str) or not isinstance(data.get('blanks'),dict) or not isinstance(ans,dict): flags.append('INVALID_CLOZE_SCHEMA')
    elif item_type=='extended_drag_drop':
        if not isinstance(data.get('items'),list) or not isinstance(ans.get('order'),list): flags.append('INVALID_ORDER_SCHEMA')
    elif item_type=='trend':
        if not isinstance(data.get('table'),dict) or not isinstance(ans.get('selected_findings'),list): flags.append('INVALID_TREND_SCHEMA')
        flags.append('TREND_NO_DISTRACTOR_OPTIONS')
    else: flags.append('UNKNOWN_ITEM_TYPE')
    return flags


def main():
    for p in (NGN_DB,V2_DB):
        if not p.exists(): raise SystemExit(f'Missing required input: {p.name}')
    if not OVERRIDE_FILES:
        raise SystemExit('Missing clinical override chunks in data/clinical_overrides_*.json')
    if OUT_DB.exists(): OUT_DB.unlink()
    out=sqlite3.connect(OUT_DB); out.row_factory=sqlite3.Row
    create_schema(out)
    out.executemany('INSERT INTO nclex_2026_blueprint VALUES(?,?,?,?,?,?,?)',BLUEPRINT)
    metadata={
      'created_at':datetime.now(timezone.utc).isoformat(),
      'purpose':'Normalized commercial NCLEX-RN practice-bank master',
      'content_provenance':'User declares all question-bank content is their own AI-created content and not copied from third-party commercial question banks.',
      'audit_scope':'Structural normalization plus source-verified clinical overrides. Items not explicitly source-verified remain NOT_AUDITED.',
      'official_case_rule':'Serve six NCJMM slots per case. Each source case contains two Recognize Cues alternatives; choose A or B, never both in the same six-item case.',
    }
    out.executemany('INSERT INTO bank_metadata(key,value) VALUES(?,?)',metadata.items())
    out.executemany('INSERT INTO test_generation_rules VALUES(?,?,?)',[
      ('exam_length','85-150','Practice generator supports NCLEX-style variable-length tests; do not claim CAT equivalence.'),
      ('minimum_case_studies','3','Minimum-length simulation includes at least three six-item clinical-judgment case studies.'),
      ('case_items_per_study','6','One item per six NCJMM steps.'),
      ('recognize_cues_variant_rule','choose_one_of_A_or_B','Do not serve both Recognize Cues variants in the same case.'),
      ('standalone_sampling','sample_by_client_need_blueprint','Never generate tests by consecutive database row order.')])

    ngn=open_row(NGN_DB)
    ngn_cats={r['id']:r['name'] for r in ngn.execute('SELECT * FROM categories')}
    cases={}
    for r in ngn.execute('SELECT * FROM case_studies ORDER BY id'):
        cases[r['id']]=r
        uid=f"NGN-CS{r['id']:03d}"
        out.execute('''INSERT INTO case_studies(
          case_uid,source_case_id,category_id,client_need,specialty,setting,client_profile,
          stage1_scenario,stage2_scenario,stage3_scenario,difficulty,source_name,source_url,
          source_verified_flag,raw_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
          uid,r['id'],r['category_id'],ngn_cats.get(r['category_id'],'UNMAPPED'),r['specialty'],r['setting'],r['client_profile'],
          r['stage1_scenario'],r['stage2_scenario'],r['stage3_scenario'],r['difficulty'],r['source_name'],r['source_url'],
          int(r['verified'] or 0),jdump(rowdict(r))))
    for r in ngn.execute('SELECT * FROM case_study_items ORDER BY case_study_id,sequence,id'):
        case=cases[r['case_study_id']]; case_uid=f"NGN-CS{case['id']:03d}"
        renderer,slot,variant=RENDERER.get(r['item_type'],('unknown',99,None))
        try: data=json.loads(r['item_data_json']); ans=json.loads(r['correct_answer_json']); flags=validate_ngn(r['item_type'],data,ans)
        except Exception: flags=['INVALID_JSON']
        structural='REVIEW' if flags else 'PASS'
        uid=f"{case_uid}-Q{r['sequence']:02d}"
        rank=BP_BY_ID.get(case['category_id'],(0,'','',0,0,0,99))[6]
        sort=f"{rank:02d}-CASE-{case['id']:03d}-{slot:02d}-{variant or 'Z'}"
        out.execute('''INSERT INTO questions(
          question_uid,source_bank,source_table,source_id,mode,case_uid,original_sequence,official_case_slot,slot_variant,
          category_id,client_need,specialty,difficulty,cjmm_skill,item_type_raw,renderer_type,stem,item_data_json,
          correct_answer_json,rationale,scoring_rule,source_name,source_url,source_verified_flag,structural_status,
          stable_sort_key,raw_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
          uid,'ngn75','case_study_items',r['id'],'case_study',case_uid,r['sequence'],slot,variant,
          case['category_id'],ngn_cats.get(case['category_id'],'UNMAPPED'),case['specialty'],case['difficulty'],r['cjmm_skill'],
          r['item_type'],renderer,r['stem'],r['item_data_json'],r['correct_answer_json'],r['rationale'],r['scoring_rule'],
          case['source_name'],case['source_url'],int(case['verified'] or 0),structural,sort,jdump(rowdict(r))))
        for f in flags:
            sev='HIGH' if f.startswith('INVALID') or f=='TREND_NO_DISTRACTOR_OPTIONS' else 'MEDIUM'
            out.execute('INSERT INTO audit_issues(question_uid,case_uid,severity,issue_code,detail) VALUES(?,?,?,?,?)',(uid,case_uid,sev,f,f))
    ngn.close()

    v2=open_row(V2_DB)
    v2_cats={r['id']:r['name'] for r in v2.execute('SELECT * FROM categories') if r['id'] in BP_BY_ID}
    src_rows=list(v2.execute('SELECT * FROM questions ORDER BY id'))
    stem_groups=defaultdict(list)
    for r in src_rows: stem_groups[norm(r['question_text'])].append(r['id'])
    dup={k:v for k,v in stem_groups.items() if k and len(v)>1}
    for r in src_rows:
        opts={'A':r['option_a'],'B':r['option_b'],'C':r['option_c'],'D':r['option_d']}
        flags=[]
        if not (r['question_text'] or '').strip(): flags.append('MISSING_STEM')
        if any(not (v or '').strip() for v in opts.values()): flags.append('MISSING_OPTION')
        if r['correct_option'] not in ('A','B','C','D'): flags.append('INVALID_CORRECT_OPTION')
        if not (r['explanation'] or '').strip(): flags.append('MISSING_RATIONALE')
        if not (r['source_name'] or '').strip(): flags.append('MISSING_SOURCE_NAME')
        if not (r['source_url'] or '').strip(): flags.append('MISSING_SOURCE_URL')
        if len({norm(v) for v in opts.values()})<4: flags.append('DUPLICATE_OPTIONS')
        if norm(r['question_text']) in dup: flags.append('DUPLICATE_STEM_DIFFERENT_OPTIONS')
        structural='REVIEW' if any(f not in ('DUPLICATE_STEM_DIFFERENT_OPTIONS',) for f in flags) else 'PASS'
        uid=f"V2-Q{r['id']:04d}"
        rank=BP_BY_ID.get(r['category_id'],(0,'','',0,0,0,99))[6]
        out.execute('''INSERT INTO questions(
          question_uid,source_bank,source_table,source_id,mode,category_id,client_need,difficulty,item_type_raw,renderer_type,
          stem,item_data_json,correct_answer_json,rationale,source_name,source_detail,source_url,source_verified_flag,
          structural_status,editorial_priority,editorial_flags_json,stable_sort_key,raw_json)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
          uid,'v2','questions',r['id'],'standalone',r['category_id'],v2_cats.get(r['category_id'],'UNMAPPED'),r['difficulty'],
          r['item_type'],'multiple_choice',r['question_text'],jdump({'options':opts}),jdump({'correct_option':r['correct_option']}),
          r['explanation'],r['source_name'],r['source_detail'],r['source_url'],int(r['verified'] or 0),structural,
          'MEDIUM' if 'DUPLICATE_STEM_DIFFERENT_OPTIONS' in flags else ('HIGH' if flags else 'NORMAL'),jdump(flags),
          f"{rank:02d}-STANDALONE-{r['id']:05d}",jdump(rowdict(r))))
        for f in flags:
            out.execute('INSERT INTO audit_issues(question_uid,severity,issue_code,detail) VALUES(?,?,?,?)',(uid,'MEDIUM',f,f))
    v2.close()

    override_items=[]
    override_versions=[]
    for override_path in OVERRIDE_FILES:
        override_doc=json.loads(override_path.read_text(encoding='utf-8'))
        override_versions.append(override_doc.get('version',override_path.name))
        override_items.extend(override_doc['questions'])
    version=' + '.join(sorted(set(override_versions)))
    for item in override_items:
        uid=item['question_uid']
        old=out.execute('SELECT stem,item_data_json,correct_answer_json,rationale FROM questions WHERE question_uid=?',(uid,)).fetchone()
        out.execute('''UPDATE questions SET stem=?,item_data_json=?,correct_answer_json=?,rationale=?,source_name=?,source_detail=?,source_url=?,
          clinical_qa_status=?,editorial_priority=?,editorial_flags_json=? WHERE question_uid=?''',(
          item['stem'],item['item_data_json'],item['correct_answer_json'],item['rationale'],item['source_name'],item['source_detail'],item['source_url'],
          item['clinical_qa_status'],item['editorial_priority'],item['editorial_flags_json'],uid))
        qc=item.get('qc')
        if qc:
            out.execute('''INSERT OR REPLACE INTO option_length_qc(question_uid,lengths_json,min_chars,max_chars,max_min_ratio,correct_option,
              correct_length_rank,correct_is_extreme,qc_status,qc_note) VALUES(?,?,?,?,?,?,?,?,?,?)''',(
              uid,qc['lengths_json'],qc['min_chars'],qc['max_chars'],qc['max_min_ratio'],qc['correct_option'],qc['correct_length_rank'],
              qc['correct_is_extreme'],qc['qc_status'],qc['qc_note']))
        out.execute('''INSERT INTO clinical_audit_log(question_uid,source_id,audit_date,audit_version,old_stem,old_options_json,
          old_correct_answer_json,old_rationale,new_stem,new_options_json,new_correct_answer_json,new_rationale,source_name,source_url,
          source_detail,findings_json,reviewer) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
          uid,item['source_id'],datetime.now(timezone.utc).isoformat(),version,old['stem'],old['item_data_json'],old['correct_answer_json'],old['rationale'],
          item['stem'],item['item_data_json'],item['correct_answer_json'],item['rationale'],item['source_name'],item['source_url'],item['source_detail'],
          jdump({'status':'source_verified_override','option_qc':qc['qc_status'] if qc else None}),'OpenAI clinical/source audit'))

    out.execute('''UPDATE questions SET commercial_release_ready=CASE WHEN structural_status='PASS'
      AND clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%'
      AND source_licensing_status='USER_DECLARED_OWNED_AI_CREATED'
      AND question_uid IN (SELECT question_uid FROM option_length_qc WHERE qc_status='PASS') THEN 1 ELSE 0 END''')
    out.commit()
    integrity=out.execute('PRAGMA integrity_check').fetchone()[0]
    total=out.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    stand=out.execute("SELECT COUNT(*) FROM questions WHERE mode='standalone'").fetchone()[0]
    ngnq=out.execute("SELECT COUNT(*) FROM questions WHERE mode='case_study'").fetchone()[0]
    cases_n=out.execute('SELECT COUNT(*) FROM case_studies').fetchone()[0]
    verified=out.execute("SELECT COUNT(*) FROM questions WHERE clinical_qa_status LIKE 'SOURCE_VERIFIED_2026_%'").fetchone()[0]
    ready=out.execute('SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1').fetchone()[0]
    review=out.execute("SELECT COUNT(*) FROM questions WHERE structural_status='REVIEW'").fetchone()[0]
    out.close()
    OUT_REPORT.write_text(f'''# NCLEX Commercial Master — Build Audit\n\n- SQLite integrity: **{integrity}**\n- Total items: **{total}**\n- Standalone items: **{stand}**\n- NGN case-study items: **{ngnq}**\n- Case studies: **{cases_n}**\n- Structural REVIEW: **{review}**\n- Source-verified clinical items: **{verified}**\n- Current commercial-gate-ready items: **{ready}**\n- Override package: `{version}`\n\nThe two source databases are preserved unchanged. The master is regenerated from them plus the versioned clinical override package.\n''',encoding='utf-8')
    print(f'Built {OUT_DB.name}: total={total}, verified={verified}, ready={ready}, integrity={integrity}')

if __name__=='__main__': main()
