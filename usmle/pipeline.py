#!/usr/bin/env python3
import argparse, copy, datetime as dt, hashlib, json, os, re, sqlite3, subprocess, sys, tempfile, uuid
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "usmle-step1.db"
STATE = ROOT / "state"
RUN_DIR = ROOT / "runs"

TOTAL = 5040

SYSTEM_TARGETS = {
    "Human Development": 99,
    "Blood, Lymphoreticular and Immune Systems": 546,
    "Behavioral Health, Nervous Systems and Special Senses": 596,
    "Musculoskeletal, Skin and Subcutaneous Tissue": 497,
    "Cardiovascular System": 447,
    "Respiratory and Renal/Urinary Systems": 646,
    "Gastrointestinal System": 397,
    "Reproductive and Endocrine Systems": 695,
    "Multisystem Processes and Disorders": 497,
    "Biostatistics, Epidemiology and Population Health": 248,
    "Social Sciences: Communication and Interpersonal Skills": 372,
}
COMPETENCY_TARGETS = {
    "Medical Knowledge: Applying Foundational Science Concepts": 3276,
    "Patient Care: Diagnosis, including history and physical examination": 1134,
    "Communication and Interpersonal Skills": 378,
    "Practice-Based Learning and Improvement": 252,
}
DISCIPLINE_TARGETS = {
    "Pathology": 2520, "Physiology": 1764, "Nutrition": 882,
    "Gross Anatomy and Embryology": 756, "Microbiology": 756,
    "Pharmacology": 756, "Behavioral Sciences": 630, "Biochemistry": 504,
    "Histology and Cell Biology": 504, "Immunology": 504, "Genetics": 378,
}

SPEC_URLS = [
    ("USMLE Step 1 Content Outline and Specifications",
     "https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications"),
    ("USMLE Step 1 Test Question Formats",
     "https://www.usmle.org/exam-resources/step-1-materials/step-1-test-question-formats"),
    ("Official USMLE Step 1 Sample Questions",
     "https://www.usmle.org/exam-resources/step-1-materials/step-1-sample-test-questions"),
    ("Current USMLE Bulletin of Information",
     "https://www.usmle.org/bulletin-information"),
    ("Current NBME Item-Writing Guide",
     "https://www.nbme.org/institutions/nbme-item-writing-guide/"),
]

ALLOWED_DOMAINS = {
    "usmle.org", "www.usmle.org", "nbme.org", "www.nbme.org", "fsmb.org", "www.fsmb.org",
    "nih.gov", "www.nih.gov", "ncbi.nlm.nih.gov", "nlm.nih.gov", "www.nlm.nih.gov",
    "medlineplus.gov", "www.medlineplus.gov", "cdc.gov", "www.cdc.gov",
    "fda.gov", "www.fda.gov", "accessdata.fda.gov", "dailymed.nlm.nih.gov",
    "hhs.gov", "www.hhs.gov", "ahrq.gov", "www.ahrq.gov", "cms.gov", "www.cms.gov",
    "hrsa.gov", "www.hrsa.gov", "osha.gov", "www.osha.gov", "epa.gov", "www.epa.gov",
    "va.gov", "www.va.gov", "federalregister.gov", "www.federalregister.gov",
    "ecfr.gov", "www.ecfr.gov", "congress.gov", "www.congress.gov",
}

URL_ALLOW_ARGS = [
    "https://www.usmle.org/*", "https://www.nbme.org/*", "https://www.fsmb.org/*",
    "https://*.nih.gov/*", "https://*.nlm.nih.gov/*", "https://medlineplus.gov/*",
    "https://*.cdc.gov/*", "https://*.fda.gov/*", "https://*.hhs.gov/*",
    "https://*.ahrq.gov/*", "https://*.cms.gov/*", "https://*.hrsa.gov/*",
    "https://*.osha.gov/*", "https://*.epa.gov/*", "https://*.va.gov/*",
    "https://*.federalregister.gov/*", "https://*.ecfr.gov/*", "https://*.congress.gov/*",
]

SCHEMA = r"""
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta(
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates(
  candidate_id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL UNIQUE,
  author_input_sha256 TEXT NOT NULL,
  author_model TEXT NOT NULL,
  author_execution_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS candidates_no_update BEFORE UPDATE ON candidates BEGIN
  SELECT RAISE(ABORT,'candidates are immutable');
END;
CREATE TRIGGER IF NOT EXISTS candidates_no_delete BEFORE DELETE ON candidates BEGIN
  SELECT RAISE(ABORT,'candidates are immutable');
END;

CREATE TABLE IF NOT EXISTS executions(
  candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id),
  role TEXT NOT NULL CHECK(role IN ('AUTHOR_EXECUTION','AUDITOR_EXECUTION_PASS_A','AUDITOR_EXECUTION_PASS_B')),
  execution_id TEXT NOT NULL UNIQUE,
  model TEXT NOT NULL,
  prompt_sha256 TEXT NOT NULL,
  context_namespace_sha256 TEXT NOT NULL UNIQUE,
  completed_at TEXT NOT NULL,
  PRIMARY KEY(candidate_id,role)
);
CREATE TRIGGER IF NOT EXISTS executions_no_update BEFORE UPDATE ON executions BEGIN
  SELECT RAISE(ABORT,'execution records are immutable');
END;
CREATE TRIGGER IF NOT EXISTS executions_no_delete BEFORE DELETE ON executions BEGIN
  SELECT RAISE(ABORT,'execution records are immutable');
END;

CREATE TABLE IF NOT EXISTS blind_audits(
  candidate_id TEXT PRIMARY KEY REFERENCES candidates(candidate_id),
  blind_json TEXT NOT NULL,
  blind_sha256 TEXT NOT NULL UNIQUE,
  auditor_model TEXT NOT NULL,
  auditor_execution_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS blind_no_update BEFORE UPDATE ON blind_audits BEGIN
  SELECT RAISE(ABORT,'blind audits are immutable');
END;
CREATE TRIGGER IF NOT EXISTS blind_no_delete BEFORE DELETE ON blind_audits BEGIN
  SELECT RAISE(ABORT,'blind audits are immutable');
END;

CREATE TABLE IF NOT EXISTS audits(
  candidate_id TEXT PRIMARY KEY REFERENCES candidates(candidate_id),
  audit_json TEXT NOT NULL,
  audit_sha256 TEXT NOT NULL UNIQUE,
  auditor_model TEXT NOT NULL,
  auditor_execution_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS audits_no_update BEFORE UPDATE ON audits BEGIN
  SELECT RAISE(ABORT,'audits are immutable');
END;
CREATE TRIGGER IF NOT EXISTS audits_no_delete BEFORE DELETE ON audits BEGIN
  SELECT RAISE(ABORT,'audits are immutable');
END;

CREATE TABLE IF NOT EXISTS decisions(
  candidate_id TEXT PRIMARY KEY REFERENCES candidates(candidate_id),
  verdict TEXT NOT NULL CHECK(verdict IN ('REJECTED','PRODUCTION_READY')),
  decided_at TEXT NOT NULL,
  importer_version TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS decisions_no_update BEFORE UPDATE ON decisions BEGIN
  SELECT RAISE(ABORT,'decisions are immutable');
END;
CREATE TRIGGER IF NOT EXISTS decisions_no_delete BEFORE DELETE ON decisions BEGIN
  SELECT RAISE(ABORT,'decisions are immutable');
END;

CREATE TABLE IF NOT EXISTS items(
  item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL UNIQUE REFERENCES candidates(candidate_id),
  payload_json TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL UNIQUE,
  audit_sha256 TEXT NOT NULL,
  blind_sha256 TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status='PRODUCTION_READY'),
  committed_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS items_no_update BEFORE UPDATE ON items BEGIN
  SELECT RAISE(ABORT,'production items are immutable');
END;
CREATE TRIGGER IF NOT EXISTS items_no_delete BEFORE DELETE ON items BEGIN
  SELECT RAISE(ABORT,'production items are immutable');
END;

CREATE TABLE IF NOT EXISTS history(
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  previous_status TEXT,
  new_status TEXT NOT NULL,
  event_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  input_sha256 TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  previous_event_sha256 TEXT,
  event_sha256 TEXT NOT NULL UNIQUE
);
CREATE TRIGGER IF NOT EXISTS history_no_update BEFORE UPDATE ON history BEGIN
  SELECT RAISE(ABORT,'history is append-only');
END;
CREATE TRIGGER IF NOT EXISTS history_no_delete BEFORE DELETE ON history BEGIN
  SELECT RAISE(ABORT,'history is append-only');
END;
"""

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def hash_obj(obj):
    return sha_text(canonical(obj))

def candidate_hash(obj):
    tmp = copy.deepcopy(obj)
    tmp.setdefault("hashes", {})["candidate_payload_sha256"] = ""
    return hash_obj(tmp)

def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model output did not contain a JSON object")
        return json.loads(text[start:end+1])

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('bank','INDEPENDENT_USMLE_STEP1_USA')")
    con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('target','5040')")
    con.commit()
    return con

def integrity(con):
    row = con.execute("PRAGMA integrity_check").fetchone()
    if not row or row[0] != "ok":
        raise RuntimeError(f"integrity_check failed: {row}")

def production_count(con):
    return con.execute("SELECT COUNT(*) FROM items WHERE status='PRODUCTION_READY'").fetchone()[0]

def get_payloads(con, include_rejected=True):
    if include_rejected:
        rows = con.execute("SELECT candidate_id,payload_json FROM candidates ORDER BY rowid").fetchall()
    else:
        rows = con.execute("""
          SELECT c.candidate_id,c.payload_json FROM candidates c
          JOIN items i ON i.candidate_id=c.candidate_id ORDER BY i.item_id
        """).fetchall()
    return [(cid, json.loads(p)) for cid,p in rows]

def add_event(con, cid, prev, new, actor, input_hash, payload_hash):
    last = con.execute("SELECT event_sha256 FROM history WHERE candidate_id=? ORDER BY seq DESC LIMIT 1",(cid,)).fetchone()
    prev_event = last[0] if last else None
    evt = {
        "candidate_id": cid, "previous_status": prev, "new_status": new,
        "event_at": now(), "actor": actor, "input_sha256": input_hash,
        "payload_sha256": payload_hash, "previous_event_sha256": prev_event,
    }
    eh = hash_obj(evt)
    con.execute("""INSERT INTO history(candidate_id,previous_status,new_status,event_at,actor,input_sha256,payload_sha256,previous_event_sha256,event_sha256)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (cid,prev,new,evt["event_at"],actor,input_hash,payload_hash,prev_event,eh))
    return eh

def fetch_specs():
    out=[]
    session=requests.Session()
    session.headers["User-Agent"]="USMLE-independent-bank-pipeline/1.0"
    for title,url in SPEC_URLS:
        r=session.get(url,timeout=30,allow_redirects=True)
        if r.status_code != 200 or len(r.content) < 1000:
            raise RuntimeError(f"official specification unavailable: {title} {r.status_code}")
        out.append({
            "title": title, "url": r.url, "retrieved_at": now(),
            "http_status": r.status_code, "sha256": hashlib.sha256(r.content).hexdigest(),
            "content_type": r.headers.get("content-type",""),
            "last_modified": r.headers.get("last-modified"),
        })
    return out

def coverage(con):
    sysc={k:0 for k in SYSTEM_TARGETS}
    compc={k:0 for k in COMPETENCY_TARGETS}
    disc={k:0 for k in DISCIPLINE_TARGETS}
    rows=con.execute("SELECT payload_json FROM items WHERE status='PRODUCTION_READY'").fetchall()
    for (p,) in rows:
        j=json.loads(p); b=j.get("blueprint",{})
        s=b.get("primary_system"); c=b.get("primary_competency")
        if s in sysc: sysc[s]+=1
        if c in compc: compc[c]+=1
        for d in b.get("disciplines",[]):
            if d in disc: disc[d]+=1
    return sysc,compc,disc

def select_cell(con):
    sysc,compc,disc=coverage(con)
    system=max(SYSTEM_TARGETS, key=lambda k:(SYSTEM_TARGETS[k]-sysc[k])/SYSTEM_TARGETS[k])
    competency=max(COMPETENCY_TARGETS, key=lambda k:(COMPETENCY_TARGETS[k]-compc[k])/COMPETENCY_TARGETS[k])
    discipline=max(DISCIPLINE_TARGETS, key=lambda k:(DISCIPLINE_TARGETS[k]-disc[k])/DISCIPLINE_TARGETS[k])
    return {
        "primary_system": system,
        "primary_competency": competency,
        "priority_discipline": discipline,
        "system_remaining": SYSTEM_TARGETS[system]-sysc[system],
        "competency_remaining": COMPETENCY_TARGETS[competency]-compc[competency],
        "discipline_remaining": DISCIPLINE_TARGETS[discipline]-disc[discipline],
    }

SOURCE_POLICY = """
FINAL EVIDENCE POLICY:
Exam design/blueprint/item-writing: only usmle.org, nbme.org, fsmb.org.
Medical claims: only official U.S. government sources on NIH/NLM/NCBI official databases,
MedlinePlus, CDC, FDA/Drugs@FDA/DailyMed, HHS/OHRP, AHRQ, CMS, HRSA, NIOSH,
OSHA, EPA, VA, or official U.S. laws/regulations/data.
NCBI hosting alone is insufficient: reject third-party-authored material such as StatPearls.
Reject commercial textbooks, UWorld, AMBOSS, UpToDate, Osmosis, Lecturio, Wikipedia,
blogs, forums, Reddit, YouTube summaries, search snippets, AI summaries, third-party journal
articles, PubMed indexing alone, and any source whose official governmental status is uncertain.
Search may locate an official page, but a search snippet is never evidence. Open the official source.
If key or any distractor lacks sufficient permitted evidence, return a rejected-quality candidate
rather than inventing support.
"""

def author_prompt(cid, cell, specs):
    return f"""You are AUTHOR_EXECUTION in an independent USMLE Step 1 pipeline.
This is a fresh execution. You receive ONLY the blueprint cell, official-spec metadata, and source policy below.
Create exactly ONE entirely original candidate. Do not copy, paraphrase, translate, reconstruct,
or imitate any official sample or commercial question. Do not assume any prior conversation.
Do not write or modify files. Research using the allowed web tools only.
Return ONE JSON object and no prose.

CANDIDATE_ID: {cid}
BLUEPRINT_CELL:
{json.dumps(cell,indent=2)}
CURRENT_OFFICIAL_SPEC_METADATA:
{json.dumps(specs,indent=2)}
{SOURCE_POLICY}

Requirements:
- single-best-answer Step 1 item, patient-centered when appropriate;
- normally A-E, minimum 4 homogeneous options; use A-E here;
- meaningful foundational-science reasoning, generally 2-4 defensible links;
- exact current official outline path must be recorded after checking the official outline;
- clinically coherent ages, time course, labs/units and mechanisms;
- key directly supported by at least two permitted official sources when available;
- each distractor independently supported for its factual premise and clearly wrong in this vignette;
- every material numeric value and explanatory claim must be evidence-traceable;
- precise section locator/supporting passage for each source;
- no ambiguity, cueing, stereotypes, hidden assumptions, or management-heavy Step 2 framing;
- explanations and educational objective must be original synthesis.

Return schema:
{{
 "candidate_id":"{cid}",
 "bank":"INDEPENDENT_USMLE_STEP1_USA",
 "country_scope":"USA",
 "specification_version":{{"usmle_retrieved_at":"","nbme_retrieved_at":"","document_hashes":[]}},
 "blueprint":{{"primary_system":"","official_outline_path":[],"primary_competency":"","disciplines":[],"coverage_deficit_addressed":""}},
 "item":{{"vignette":"","lead_in":"","options":{{"A":"","B":"","C":"","D":"","E":""}},"intended_key":"","difficulty":"","tested_construct":"","reasoning_steps_count":0}},
 "explanation":{{"key_explanation":"","distractor_explanations":{{"A":"","B":"","C":"","D":"","E":""}},"educational_objective":""}},
 "evidence_map":[{{"claim_id":"","option":"","claim":"","source_ids":[],"direct_or_inference":"","item_specific_application":""}}],
 "sources":[{{"source_id":"","agency":"","title":"","url":"","publication_or_revision_date":"","retrieved_at":"","section_locator":"","supporting_passage":"","government_status_verified":true,"rights_status":""}}],
 "semantic_fingerprint":{{"tested_construct":"","diagnosis_or_process":"","mechanism":"","lead_in_task":"","correct_answer_concept":"","essential_clues":[],"reasoning_chain":[],"distractor_misconceptions":[]}},
 "author_self_audit":{{"scores":{{"blueprint":10,"key":10,"distractors":10,"single_best_answer":10,"reasoning":10,"item_writing":10,"fairness":10,"evidence":10,"originality":10,"technical_integrity":10}},"unresolved_concerns":[]}},
 "hashes":{{"author_input_sha256":"","candidate_payload_sha256":""}},
 "status":"CANDIDATE_FROZEN"
}}
Do not fabricate a 10. If any domain is not genuinely 10, put its true score below 10 and describe the concern.
"""

def blind_prompt(candidate):
    item=candidate["item"]
    return f"""You are AUDITOR_EXECUTION PASS A (blind solution), a brand-new model execution with no shared session/history.
You are NOT given the Author's intended key, rationale, evidence packet, self-audit, hashes, or feedback.
Solve independently. Do not repair or rewrite the item. Return JSON only.

VIGNETTE:
{item['vignette']}

LEAD-IN:
{item['lead_in']}

OPTIONS:
{json.dumps(item['options'],indent=2)}

{SOURCE_POLICY}

Return:
{{
 "candidate_id":"{candidate['candidate_id']}",
 "selected_key":"",
 "tested_construct":"",
 "concise_reasoning_summary":"",
 "alternative_defensible_options":[],
 "missing_assumptions":[],
 "cueing_findings":[],
 "blind_verdict":"UNIQUE_BEST_ANSWER_OR_REJECT"
}}
If you cannot reach exactly one uniquely best answer without unstated assumptions, set blind_verdict="REJECT".
If there is exactly one uniquely best answer, set blind_verdict="UNIQUE_BEST_ANSWER".
"""

def normalized_text(c):
    i=c.get("item",{})
    return " ".join([i.get("vignette",""), i.get("lead_in","")] + list(i.get("options",{}).values())).lower()

def ngrams(s,n=5):
    toks=re.findall(r"[a-z0-9]+",s.lower())
    if len(toks)<n: return set(tuple(toks)) if toks else set()
    return {tuple(toks[i:i+n]) for i in range(len(toks)-n+1)}

def deterministic_duplicate_report(con, candidate):
    """Fast deterministic duplicate gate; semantic judgment remains with the independent auditor."""
    text = normalized_text(candidate)
    ng = ngrams(text)
    others = [(cid, other) for cid, other in get_payloads(con, include_rejected=True)
              if cid != candidate["candidate_id"]]
    best = {"candidate_id": None, "ngram_jaccard": 0.0, "exact": False}
    fpkey = canonical(candidate.get("semantic_fingerprint", {}))
    fpdup = []

    for cid, other in others:
        ot = normalized_text(other)
        exact = re.sub(r"\s+", " ", text).strip() == re.sub(r"\s+", " ", ot).strip()
        ong = ngrams(ot)
        jac = (len(ng & ong) / len(ng | ong)) if (ng or ong) else 0.0
        if exact or jac > best["ngram_jaccard"]:
            best = {"candidate_id": cid, "ngram_jaccard": jac, "exact": exact}
        if canonical(other.get("semantic_fingerprint", {})) == fpkey:
            fpdup.append(cid)

    threshold_pass = (
        not best["exact"]
        and best["ngram_jaccard"] < 0.72
        and not fpdup
    )
    return {
        "exact_match": bool(best["exact"]),
        "closest_candidate_id": best["candidate_id"],
        "max_stem_option_ngram_jaccard": round(best["ngram_jaccard"], 6),
        "fingerprint_exact_duplicates": fpdup,
        "embedding_checked": False,
        "semantic_duplicate_review": "independent_auditor_required",
        "threshold_pass": threshold_pass,
    }

def passb_prompt(candidate, blind, blind_hash, dup_report):
    safe=copy.deepcopy(candidate)
    safe.pop("author_self_audit",None)
    return f"""You are AUDITOR_EXECUTION PASS B, an independent fresh model execution.
You have no Author conversation, hidden reasoning, self-audit, or repair instructions.
A separate blind execution already solved the item. Its immutable result and SHA-256 are below.
Do NOT repair the candidate. If ANY wording, source, option, unit, grammar, explanation, locator,
blueprint, originality, or technical change is advisable, REJECT.

BLIND_RESULT_SHA256: {blind_hash}
BLIND_RESULT:
{json.dumps(blind,indent=2)}

FROZEN_CANDIDATE_WITHOUT_AUTHOR_SELF_AUDIT:
{json.dumps(safe,indent=2)}

DETERMINISTIC_FULL-CORPUS_PRECHECK:
{json.dumps(dup_report,indent=2)}

{SOURCE_POLICY}

Audit requirements:
- Independently open and check every cited source using web tools.
- Verify official/government status, recency/applicability, exact locator, and each claim.
- Search permitted official sources for stronger contradictory evidence.
- Re-derive key; verify each A-E option independently.
- Reject a second defensible answer, hidden assumption, cueing, bias, unfairness, or Step 1 mismatch.
- Verify the exact current USMLE outline mapping and current NBME/USMLE format.
- Assess semantic duplication against the supplied corpus precheck plus candidate fingerprint; also inspect current official sample materials for prohibited derivation/similarity.
- Verify rights/provenance and that explanations do not overclaim.
- Technical score 10 only if candidate/blind hashes and immutable execution metadata can be validated by deterministic importer.

Return JSON only:
{{
 "candidate_id":"{candidate['candidate_id']}",
 "candidate_payload_sha256_verified":true,
 "blind_result_sha256":"{blind_hash}",
 "blind_audit":{{"selected_key":"{blind.get('selected_key','')}","tested_construct":"","concise_reasoning_summary":"","alternative_defensible_options":[],"missing_assumptions":[],"cueing_findings":[]}},
 "source_verification":[{{"source_id":"","opened_and_checked":true,"government_status_verified":true,"claim_supported":true,"current_and_applicable":true,"conflict_found":false,"notes":""}}],
 "option_audit":{{
   "A":{{"factual_claim_verified":true,"item_specific_status_verified":true,"uniquely_correct_or_incorrect":true}},
   "B":{{"factual_claim_verified":true,"item_specific_status_verified":true,"uniquely_correct_or_incorrect":true}},
   "C":{{"factual_claim_verified":true,"item_specific_status_verified":true,"uniquely_correct_or_incorrect":true}},
   "D":{{"factual_claim_verified":true,"item_specific_status_verified":true,"uniquely_correct_or_incorrect":true}},
   "E":{{"factual_claim_verified":true,"item_specific_status_verified":true,"uniquely_correct_or_incorrect":true}}
 }},
 "duplicate_audit":{{"exact_match":false,"lexical_duplicate":false,"semantic_duplicate":false,"mechanism_duplicate":false,"closest_existing_item_id":null,"similarity_explanation":""}},
 "rights_audit":{{"originality_verified":true,"prohibited_derivation_found":false,"asset_rights_verified":true}},
 "scores":{{"blueprint_fidelity":0,"key_correctness":0,"distractor_integrity":0,"single_best_answer":0,"reasoning_and_difficulty":0,"item_writing":0,"cueing_bias_fairness":0,"evidence_quality":0,"originality_duplication_rights":0,"technical_integrity":0}},
 "defects":[],
 "suggested_changes":[],
 "verdict":"PASS_WITH_NO_CHANGES_OR_REJECT",
 "auditor_model":"",
 "audited_at":"",
 "audit_record_sha256":""
}}
Every score must be an integer. PASS_WITH_NO_CHANGES is allowed only if all ten are exactly 10 and there is positive evidence for every domain.
"""

def run_copilot(prompt, model, phase, execution_id):
    home=Path(tempfile.mkdtemp(prefix=f"copilot-{phase}-"))
    work=Path(tempfile.mkdtemp(prefix=f"work-{phase}-"))
    env=os.environ.copy()
    env["COPILOT_HOME"]=str(home)
    env["COPILOT_AUTO_UPDATE"]="false"
    cmd=[
        "copilot","-p",prompt,"-s","--no-ask-user",
        "--model",model,"--reasoning-effort","high",
        "--available-tools=web_search,web_fetch",
        "--allow-tool=web_search","--allow-tool=web_fetch",
        "--disable-builtin-mcps","-C",str(work)
    ]
    for u in URL_ALLOW_ARGS:
        cmd += ["--allow-url",u]
    p=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=1200)
    if p.returncode!=0:
        raise RuntimeError(f"{phase} execution failed rc={p.returncode}: {p.stderr[-2000:]}")
    result=extract_json(p.stdout)
    return result, {"execution_id":execution_id,"model":model,"copilot_home":str(home),"workdir":str(work),
                    "prompt_sha256":sha_text(prompt),"completed_at":now()}

def validate_author(candidate, cid, cell):
    if candidate.get("candidate_id")!=cid: raise ValueError("candidate_id mismatch")
    if candidate.get("status")!="CANDIDATE_FROZEN": raise ValueError("candidate not frozen")
    b=candidate.get("blueprint",{})
    if b.get("primary_system")!=cell["primary_system"]: raise ValueError("primary_system mismatch")
    if b.get("primary_competency")!=cell["primary_competency"]: raise ValueError("primary_competency mismatch")
    i=candidate.get("item",{})
    opts=i.get("options",{})
    if set(opts.keys())!=set("ABCDE") or any(not str(opts[k]).strip() for k in "ABCDE"):
        raise ValueError("A-E options required")
    if len(set(opts.values()))!=5: raise ValueError("options must be unique")
    if i.get("intended_key") not in opts: raise ValueError("invalid key")
    if not str(i.get("vignette","")).strip() or not str(i.get("lead_in","")).strip(): raise ValueError("missing item text")
    if not b.get("official_outline_path"): raise ValueError("missing official outline path")
    scores=candidate.get("author_self_audit",{}).get("scores",{})
    expected={"blueprint","key","distractors","single_best_answer","reasoning","item_writing","fairness","evidence","originality","technical_integrity"}
    if set(scores)!=expected or any(not isinstance(v,int) or v<0 or v>10 for v in scores.values()):
        raise ValueError("author scores invalid")
    return True

def domain_ok(url):
    host=(urlparse(url).hostname or "").lower()
    if host in ALLOWED_DOMAINS: return True
    roots=["nih.gov","nlm.nih.gov","cdc.gov","fda.gov","hhs.gov","ahrq.gov","cms.gov","hrsa.gov","osha.gov","epa.gov","va.gov","federalregister.gov","ecfr.gov","congress.gov"]
    return any(host==r or host.endswith("."+r) for r in roots)

def verify_sources(candidate):
    sources=candidate.get("sources",[])
    if len(sources)<2: return False,["fewer than two sources"]
    errors=[]
    ids=set()
    sess=requests.Session(); sess.headers["User-Agent"]="USMLE-independent-bank-pipeline/1.0"
    for s in sources:
        sid=s.get("source_id")
        if not sid or sid in ids: errors.append("invalid/duplicate source_id"); continue
        ids.add(sid)
        url=s.get("url","")
        if not domain_ok(url): errors.append(f"disallowed source domain {url}"); continue
        if not s.get("government_status_verified"): errors.append(f"government status false {sid}")
        if not str(s.get("section_locator","")).strip(): errors.append(f"missing locator {sid}")
        if not str(s.get("supporting_passage","")).strip(): errors.append(f"missing passage {sid}")
        try:
            r=sess.get(url,timeout=30,allow_redirects=True)
            if r.status_code!=200: errors.append(f"source HTTP {r.status_code} {sid}")
            if not domain_ok(r.url): errors.append(f"redirected to disallowed domain {r.url}")
        except Exception as e:
            errors.append(f"source inaccessible {sid}: {type(e).__name__}")
    cover={k:0 for k in "ABCDE"}
    for e in candidate.get("evidence_map",[]):
        op=e.get("option")
        if op in cover: cover[op]+=1
        for sid in e.get("source_ids",[]):
            if sid not in ids: errors.append(f"unknown source id in evidence map {sid}")
    for k,v in cover.items():
        if v<1: errors.append(f"no evidence mapping for option {k}")
    return (not errors), errors

def score_gate(audit):
    scores=audit.get("scores",{})
    expected={"blueprint_fidelity","key_correctness","distractor_integrity","single_best_answer","reasoning_and_difficulty","item_writing","cueing_bias_fairness","evidence_quality","originality_duplication_rights","technical_integrity"}
    return set(scores)==expected and all(type(v) is int and v==10 for v in scores.values())

def audit_gate(candidate, blind, audit, dup_report):
    defects=[]
    if blind.get("blind_verdict")!="UNIQUE_BEST_ANSWER": defects.append("blind verdict not unique")
    if blind.get("alternative_defensible_options"): defects.append("blind found alternative")
    if blind.get("missing_assumptions"): defects.append("blind found missing assumptions")
    if blind.get("selected_key")!=candidate["item"]["intended_key"]: defects.append("blind key mismatch")
    if audit.get("candidate_id")!=candidate["candidate_id"]: defects.append("audit candidate mismatch")
    if audit.get("blind_audit",{}).get("selected_key")!=blind.get("selected_key"): defects.append("audit blind key mismatch")
    if audit.get("verdict")!="PASS_WITH_NO_CHANGES": defects.append("auditor rejected")
    if audit.get("defects"): defects.append("auditor defects")
    if audit.get("suggested_changes"): defects.append("auditor suggested changes")
    if not score_gate(audit): defects.append("not all ten scores are 10")
    ra=audit.get("rights_audit",{})
    if not ra.get("originality_verified") or ra.get("prohibited_derivation_found") or not ra.get("asset_rights_verified"):
        defects.append("rights gate failed")
    da=audit.get("duplicate_audit",{})
    if any(da.get(k) for k in ["exact_match","lexical_duplicate","semantic_duplicate","mechanism_duplicate"]):
        defects.append("auditor duplicate gate failed")
    if not dup_report.get("threshold_pass"): defects.append("deterministic duplicate gate failed")
    oa=audit.get("option_audit",{})
    for k in "ABCDE":
        x=oa.get(k,{})
        if not all(x.get(y) is True for y in ["factual_claim_verified","item_specific_status_verified","uniquely_correct_or_incorrect"]):
            defects.append(f"option audit failed {k}")
    verified_ids=set()
    for sv in audit.get("source_verification",[]):
        sid=sv.get("source_id")
        if sid: verified_ids.add(sid)
        if not all(sv.get(k) is True for k in ["opened_and_checked","government_status_verified","claim_supported","current_and_applicable"]):
            defects.append(f"source verification failed {sid}")
        if sv.get("conflict_found"): defects.append(f"source conflict {sid}")
    required_ids={s.get("source_id") for s in candidate.get("sources",[]) if s.get("source_id")}
    if not required_ids or verified_ids != required_ids:
        defects.append("auditor did not independently verify every cited source")
    return defects

def insert_execution(con,cid,role,meta):
    ns=sha_text(meta["copilot_home"]+"|"+meta["workdir"]+"|"+meta["execution_id"])
    con.execute("""INSERT INTO executions(candidate_id,role,execution_id,model,prompt_sha256,context_namespace_sha256,completed_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (cid,role,meta["execution_id"],meta["model"],meta["prompt_sha256"],ns,meta["completed_at"]))

def model_family(model):
    # Explicit allowlist for this pipeline's configured models. Unknown/automatic
    # routing does not prove distinct model families.
    return {"gpt-5.4": "openai-gpt", "claude-sonnet-4.6": "anthropic-claude"}.get(model)


def distinct_model_families(author_model, blind_model, audit_model):
    author = model_family(author_model)
    blind = model_family(blind_model)
    audit = model_family(audit_model)
    return bool(author and blind and audit and author != blind and author != audit)


def isolation_gate_db(con,cid):
    rows=con.execute("""SELECT role,execution_id,model,prompt_sha256,context_namespace_sha256
                        FROM executions WHERE candidate_id=? ORDER BY role""",(cid,)).fetchall()
    if len(rows)!=3: return False
    roles={r[0] for r in rows}
    if roles!={"AUTHOR_EXECUTION","AUDITOR_EXECUTION_PASS_A","AUDITOR_EXECUTION_PASS_B"}: return False
    if len({r[1] for r in rows})!=3 or len({r[4] for r in rows})!=3: return False
    models = {r[0]: r[2] for r in rows}
    return distinct_model_families(models["AUTHOR_EXECUTION"], models["AUDITOR_EXECUTION_PASS_A"], models["AUDITOR_EXECUTION_PASS_B"])

def insert_candidate(con,candidate,author_meta):
    cid=candidate["candidate_id"]
    con.execute("""INSERT INTO candidates(candidate_id,payload_json,payload_sha256,author_input_sha256,author_model,author_execution_id,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (cid,canonical(candidate),candidate["hashes"]["candidate_payload_sha256"],candidate["hashes"]["author_input_sha256"],
                 author_meta["model"],author_meta["execution_id"],now()))
    add_event(con,cid,None,"CANDIDATE_CREATED","orchestrator",candidate["hashes"]["author_input_sha256"],candidate["hashes"]["candidate_payload_sha256"])
    add_event(con,cid,"CANDIDATE_CREATED","AUTHOR_SELF_CHECK_PASSED","AUTHOR_EXECUTION",candidate["hashes"]["author_input_sha256"],candidate["hashes"]["candidate_payload_sha256"])
    add_event(con,cid,"AUTHOR_SELF_CHECK_PASSED","CANDIDATE_FROZEN","orchestrator",candidate["hashes"]["author_input_sha256"],candidate["hashes"]["candidate_payload_sha256"])

def insert_blind(con,cid,blind,bhash,meta,cand_hash):
    con.execute("""INSERT INTO blind_audits(candidate_id,blind_json,blind_sha256,auditor_model,auditor_execution_id,created_at)
                   VALUES(?,?,?,?,?,?)""",(cid,canonical(blind),bhash,meta["model"],meta["execution_id"],now()))
    add_event(con,cid,"CANDIDATE_FROZEN","BLIND_AUDIT_COMPLETED","AUDITOR_EXECUTION_PASS_A",meta["prompt_sha256"],cand_hash)

def insert_audit(con,cid,audit,ahash,meta,cand_hash):
    con.execute("""INSERT INTO audits(candidate_id,audit_json,audit_sha256,auditor_model,auditor_execution_id,created_at)
                   VALUES(?,?,?,?,?,?)""",(cid,canonical(audit),ahash,meta["model"],meta["execution_id"],now()))
    add_event(con,cid,"BLIND_AUDIT_COMPLETED","SOURCE_AUDIT_COMPLETED","AUDITOR_EXECUTION_PASS_B",meta["prompt_sha256"],cand_hash)
    add_event(con,cid,"SOURCE_AUDIT_COMPLETED","SEMANTIC_AUDIT_COMPLETED","AUDITOR_EXECUTION_PASS_B",meta["prompt_sha256"],cand_hash)

def import_or_reject(con,candidate,blind,bhash,audit,ahash,source_ok,source_errors,gate_errors):
    cid=candidate["candidate_id"]; ch=candidate["hashes"]["candidate_payload_sha256"]
    all_errors=list(source_errors)+list(gate_errors)
    if candidate_hash(candidate)!=ch: all_errors.append("candidate hash mismatch")
    if hash_obj(blind)!=bhash: all_errors.append("blind hash mismatch")
    atmp=copy.deepcopy(audit); saved=atmp.get("audit_record_sha256",""); atmp["audit_record_sha256"]=""
    calc=hash_obj(atmp)
    if saved and saved!=calc: all_errors.append("audit hash self-field mismatch")
    if ahash!=hash_obj(audit): all_errors.append("audit storage hash mismatch")
    author_scores=candidate.get("author_self_audit",{}).get("scores",{})
    if any(v!=10 for v in author_scores.values()) or candidate.get("author_self_audit",{}).get("unresolved_concerns"):
        all_errors.append("author self-audit not 10/10")
    verdict="REJECTED" if all_errors else "PRODUCTION_READY"
    con.execute("BEGIN IMMEDIATE")
    try:
        if verdict=="PRODUCTION_READY":
            add_event(con,cid,"SEMANTIC_AUDIT_COMPLETED","DETERMINISTIC_GATES_PASSED","TRUSTED_IMPORTER",ahash,ch)
            add_event(con,cid,"DETERMINISTIC_GATES_PASSED","AUDIT_PASS","TRUSTED_IMPORTER",ahash,ch)
            con.execute("""INSERT INTO items(candidate_id,payload_json,payload_sha256,audit_sha256,blind_sha256,status,committed_at)
                           VALUES(?,?,?,?,?,'PRODUCTION_READY',?)""",
                        (cid,canonical(candidate),ch,ahash,bhash,now()))
            con.execute("INSERT INTO decisions(candidate_id,verdict,decided_at,importer_version) VALUES(?,?,?,?)",
                        (cid,"PRODUCTION_READY",now(),"1.0"))
            add_event(con,cid,"AUDIT_PASS","PRODUCTION_READY_COMMITTED","TRUSTED_IMPORTER",ahash,ch)
        else:
            con.execute("INSERT INTO decisions(candidate_id,verdict,decided_at,importer_version) VALUES(?,?,?,?)",
                        (cid,"REJECTED",now(),"1.0"))
            add_event(con,cid,"SEMANTIC_AUDIT_COMPLETED","AUDIT_REJECTED","TRUSTED_IMPORTER",ahash,ch)
            add_event(con,cid,"AUDIT_REJECTED","REJECTION_PRESERVED","TRUSTED_IMPORTER",ahash,ch)
        con.commit()
    except:
        con.rollback(); raise
    integrity(con)
    if verdict=="PRODUCTION_READY":
        row=con.execute("SELECT payload_sha256,audit_sha256,blind_sha256,status FROM items WHERE candidate_id=?",(cid,)).fetchone()
        if row!=(ch,ahash,bhash,"PRODUCTION_READY"):
            raise RuntimeError("post-commit reread mismatch")
        con.execute("BEGIN IMMEDIATE")
        add_event(con,cid,"PRODUCTION_READY_COMMITTED","POST_COMMIT_VERIFIED","TRUSTED_IMPORTER",ahash,ch)
        con.commit()
    return verdict,all_errors

def isolation_gate(author_meta,blind_meta,audit_meta):
    ids={author_meta["execution_id"],blind_meta["execution_id"],audit_meta["execution_id"]}
    homes={author_meta["copilot_home"],blind_meta["copilot_home"],audit_meta["copilot_home"]}
    works={author_meta["workdir"],blind_meta["workdir"],audit_meta["workdir"]}
    if len(ids)!=3 or len(homes)!=3 or len(works)!=3:
        return False
    return distinct_model_families(author_meta.get("model"), blind_meta.get("model"), audit_meta.get("model"))

def trusted_import_candidate(cid):
    con=connect(); integrity(con)
    crow=con.execute("SELECT payload_json,payload_sha256 FROM candidates WHERE candidate_id=?",(cid,)).fetchone()
    brow=con.execute("SELECT blind_json,blind_sha256 FROM blind_audits WHERE candidate_id=?",(cid,)).fetchone()
    arow=con.execute("SELECT audit_json,audit_sha256 FROM audits WHERE candidate_id=?",(cid,)).fetchone()
    if not crow or not brow or not arow:
        raise RuntimeError("trusted importer missing frozen package")
    candidate=json.loads(crow[0]); blind=json.loads(brow[0]); audit=json.loads(arow[0])
    dup=deterministic_duplicate_report(con,candidate)
    source_ok,source_errors=verify_sources(candidate)
    gates=audit_gate(candidate,blind,audit,dup)
    if not isolation_gate_db(con,cid):
        gates.append("technical execution isolation not proven")
    verdict,errs=import_or_reject(con,candidate,blind,brow[1],audit,arow[1],source_ok,source_errors,gates)
    print(canonical({"candidate_id":cid,"verdict":verdict,"errors":errs}))
    return 0

def run(max_accepted=5,max_attempts=20):
    con=connect(); integrity(con)
    before=production_count(con)
    specs=fetch_specs()
    STATE.mkdir(parents=True,exist_ok=True); RUN_DIR.mkdir(parents=True,exist_ok=True)
    spec_file=STATE/"current_specs.json"
    spec_file.write_text(json.dumps(specs,indent=2,ensure_ascii=False),encoding="utf-8")
    accepted=0; attempts=0; isolation_proven=False; outcomes=[]
    while accepted<max_accepted and attempts<max_attempts and production_count(con)<TOTAL:
        attempts+=1
        cid=f"S1-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')}-{attempts:03d}-{uuid.uuid4().hex[:8]}"
        cell=select_cell(con)
        ap=author_prompt(cid,cell,specs)
        author,ameta=run_copilot(ap,"gpt-5.4","author",uuid.uuid4().hex)
        validate_author(author,cid,cell)
        usmle_meta=[s for s in specs if "USMLE" in s["title"]]
        nbme_meta=[s for s in specs if "NBME" in s["title"]]
        author["specification_version"]={
            "usmle_retrieved_at": max(s["retrieved_at"] for s in usmle_meta),
            "nbme_retrieved_at": max(s["retrieved_at"] for s in nbme_meta),
            "document_hashes":[{"title":s["title"],"url":s["url"],"sha256":s["sha256"],"retrieved_at":s["retrieved_at"],"last_modified":s.get("last_modified")} for s in specs]
        }
        author.setdefault("hashes",{})["author_input_sha256"]=sha_text(ap)
        author["hashes"]["candidate_payload_sha256"]=""
        author["hashes"]["candidate_payload_sha256"]=candidate_hash(author)
        con.execute("BEGIN IMMEDIATE"); insert_candidate(con,author,ameta); insert_execution(con,cid,"AUTHOR_EXECUTION",ameta); con.commit()

        bp=blind_prompt(author)
        blind,bmeta=run_copilot(bp,"claude-sonnet-4.6","auditor-blind",uuid.uuid4().hex)
        if blind.get("candidate_id")!=cid: blind["candidate_id"]=cid
        bhash=hash_obj(blind)
        con.execute("BEGIN IMMEDIATE"); insert_blind(con,cid,blind,bhash,bmeta,author["hashes"]["candidate_payload_sha256"]); insert_execution(con,cid,"AUDITOR_EXECUTION_PASS_A",bmeta); con.commit()

        dup=deterministic_duplicate_report(con,author)
        pp=passb_prompt(author,blind,bhash,dup)
        audit,aumeta=run_copilot(pp,"claude-sonnet-4.6","auditor-passb",uuid.uuid4().hex)
        audit["candidate_id"]=cid
        audit["auditor_model"]=aumeta["model"]
        audit["audited_at"]=now()
        audit["audit_record_sha256"]=""
        audit["audit_record_sha256"]=hash_obj(audit)
        ahash=hash_obj(audit)
        con.execute("BEGIN IMMEDIATE"); insert_audit(con,cid,audit,ahash,aumeta,author["hashes"]["candidate_payload_sha256"]); insert_execution(con,cid,"AUDITOR_EXECUTION_PASS_B",aumeta); con.commit()

        iso=isolation_gate(ameta,bmeta,aumeta) and isolation_gate_db(con,cid)
        isolation_proven=isolation_proven or iso
        imp=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--import-candidate",cid],
                           text=True,capture_output=True,timeout=1200)
        if imp.returncode!=0:
            raise RuntimeError(f"TRUSTED_IMPORTER failed: {imp.stderr[-2000:]}")
        result=extract_json(imp.stdout)
        verdict=result["verdict"]; errs=result.get("errors",[])
        outcomes.append({"candidate_id":cid,"verdict":verdict,"errors":errs,"isolation_proven":iso})
        if verdict=="PRODUCTION_READY": accepted+=1
        if attempts==1 and not iso:
            break
    integrity(con)
    after=production_count(con)
    if after-before != accepted:
        raise RuntimeError(f"counter delta mismatch: before={before} after={after} accepted={accepted}")
    summary={
        "run_at":now(),"before":before,"after":after,"accepted_this_run":accepted,
        "attempts":attempts,"isolation_proven":isolation_proven,"outcomes":outcomes,
        "author_model":"gpt-5.4","auditor_model":"claude-sonnet-4.6",
        "author_and_auditor_fresh_processes":True,
        "production_count_query":"SELECT COUNT(*) FROM items WHERE status='PRODUCTION_READY'",
    }
    (STATE/"last_run.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"FINAL_COUNT={after}")
    print(f"ACCEPTED_THIS_RUN={accepted}")
    print(f"ISOLATION_PROVEN={str(isolation_proven).lower()}")
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-accepted",type=int,default=5)
    ap.add_argument("--max-attempts",type=int,default=20)
    ap.add_argument("--import-candidate",default=None)
    args=ap.parse_args()
    if args.import_candidate:
        sys.exit(trusted_import_candidate(args.import_candidate))
    sys.exit(run(args.max_accepted,args.max_attempts))
