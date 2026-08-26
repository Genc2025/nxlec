#!/usr/bin/env python3
import copy, hashlib, json, pathlib, re, sqlite3, sys

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "data" / "usmle-step1.db"
STATE = ROOT / "state"
REVIEWED = ROOT / "reviewed"
EXPECTED_REVIEW_SCORES = {
    "blueprint_fidelity","key_correctness","distractor_integrity","single_best_answer",
    "reasoning_and_difficulty","item_writing","cueing_bias_fairness","evidence_quality",
    "originality_duplication_rights","technical_integrity"
}
EXPECTED_AUTHOR_SCORES = {
    "blueprint","key","distractors","single_best_answer","reasoning","item_writing",
    "fairness","evidence","originality","technical_integrity"
}
ALLOWED_MEDICAL_ROOTS = ("nih.gov","nlm.nih.gov","cdc.gov","fda.gov","hhs.gov","ahrq.gov",
                         "cms.gov","hrsa.gov","osha.gov","epa.gov","va.gov")

def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def hash_obj(o):
    return sha_text(canonical(o))

def candidate_hash(c):
    x = copy.deepcopy(c)
    x.setdefault("hashes", {})["candidate_payload_sha256"] = ""
    return hash_obj(x)

def review_hash(r):
    x = copy.deepcopy(r)
    x["review_sha256"] = ""
    return hash_obj(x)

def request_hash(r):
    x = copy.deepcopy(r)
    x["request_sha256"] = ""
    return hash_obj(x)

def norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()

def item_text(c):
    i = c["item"]
    return " ".join([i["vignette"], i["lead_in"], *[i["options"][k] for k in "ABCDE"]])

def ngrams(s, n=5):
    t = re.findall(r"[a-z0-9]+", s.lower())
    if len(t) < n:
        return {tuple(t)} if t else set()
    return {tuple(t[i:i+n]) for i in range(len(t)-n+1)}

def domain_ok(url):
    from urllib.parse import urlparse
    h = (urlparse(url).hostname or "").lower()
    return any(h == r or h.endswith("." + r) for r in ALLOWED_MEDICAL_ROOTS)

def add_event(con, cid, prev, new, actor, input_hash, payload_hash, event_at):
    row = con.execute("SELECT event_sha256 FROM history WHERE candidate_id=? ORDER BY seq DESC LIMIT 1",(cid,)).fetchone()
    pe = row[0] if row else None
    evt = {
        "candidate_id":cid,"previous_status":prev,"new_status":new,"event_at":event_at,
        "actor":actor,"input_sha256":input_hash,"payload_sha256":payload_hash,
        "previous_event_sha256":pe
    }
    eh = hash_obj(evt)
    con.execute("""INSERT INTO history(candidate_id,previous_status,new_status,event_at,actor,input_sha256,
                   payload_sha256,previous_event_sha256,event_sha256) VALUES(?,?,?,?,?,?,?,?,?)""",
                (cid,prev,new,event_at,actor,input_hash,payload_hash,pe,eh))

def main(path):
    req = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    c = req["candidate"]; r = req["review"]; cid = c["candidate_id"]
    ch = c["hashes"]["candidate_payload_sha256"]; rh = r["review_sha256"]

    if request_hash(req) != req.get("request_sha256"): raise SystemExit("request hash mismatch")
    if candidate_hash(c) != ch: raise SystemExit("candidate hash mismatch")
    if review_hash(r) != rh: raise SystemExit("review hash mismatch")
    if c.get("status") != "CANDIDATE_FROZEN": raise SystemExit("candidate not frozen")
    if r.get("candidate_id") != cid or r.get("verdict") != "PASS_WITH_NO_CHANGES": raise SystemExit("review gate failed")
    if r.get("selected_key") != c["item"].get("intended_key") or not r.get("key_matches"): raise SystemExit("key mismatch")

    opts = c["item"].get("options", {})
    if set(opts) != set("ABCDE") or len(set(opts.values())) != 5: raise SystemExit("A-E unique options required")
    if not c["item"].get("vignette","").strip() or not c["item"].get("lead_in","").strip(): raise SystemExit("missing item text")

    a = c.get("author_self_audit", {})
    asc = a.get("scores", {})
    if set(asc) != EXPECTED_AUTHOR_SCORES or any(type(v) is not int or v != 10 for v in asc.values()) or a.get("unresolved_concerns"):
        raise SystemExit("author 10/10 gate failed")
    rsc = r.get("scores", {})
    if set(rsc) != EXPECTED_REVIEW_SCORES or any(type(v) is not int or v != 10 for v in rsc.values()):
        raise SystemExit("review 10/10 gate failed")
    if r.get("defects") or r.get("suggested_changes"): raise SystemExit("review contains defects/changes")

    sids = set()
    for s in c.get("sources", []):
        if not s.get("source_id") or s["source_id"] in sids: raise SystemExit("invalid source id")
        sids.add(s["source_id"])
        if not s.get("government_status_verified") or not domain_ok(s.get("url","")):
            raise SystemExit("medical source policy failed")
        if not s.get("section_locator") or not s.get("supporting_passage"):
            raise SystemExit("incomplete source evidence")
    if len(sids) < 2: raise SystemExit("at least two official medical sources required")
    covered = {k:0 for k in "ABCDE"}
    for e in c.get("evidence_map", []):
        op = e.get("option")
        if op in covered: covered[op] += 1
        if any(x not in sids for x in e.get("source_ids", [])): raise SystemExit("unknown evidence source")
    if any(v < 1 for v in covered.values()): raise SystemExit("every option needs evidence mapping")

    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok": raise SystemExit("pre-import integrity failure")
    con.execute("""CREATE TABLE IF NOT EXISTS direct_reviews(
        candidate_id TEXT PRIMARY KEY REFERENCES candidates(candidate_id),
        review_json TEXT NOT NULL, review_sha256 TEXT NOT NULL UNIQUE,
        model TEXT NOT NULL, reviewed_at TEXT NOT NULL
    )""")
    con.execute("""CREATE TRIGGER IF NOT EXISTS direct_reviews_no_update BEFORE UPDATE ON direct_reviews BEGIN
        SELECT RAISE(ABORT,'direct reviews are immutable'); END;""")
    con.execute("""CREATE TRIGGER IF NOT EXISTS direct_reviews_no_delete BEFORE DELETE ON direct_reviews BEGIN
        SELECT RAISE(ABORT,'direct reviews are immutable'); END;""")
    con.commit()

    existing = con.execute("SELECT payload_sha256,status FROM items WHERE candidate_id=?",(cid,)).fetchone()
    if existing:
        if existing != (ch, "PRODUCTION_READY"): raise SystemExit("candidate id collision")
        print("ALREADY_IMPORTED")
        return 0

    qtext = norm(item_text(c)); qng = ngrams(qtext)
    fp = canonical(c.get("semantic_fingerprint", {}))
    for ocid, payload in con.execute("SELECT candidate_id,payload_json FROM candidates"):
        if ocid == cid: continue
        other = json.loads(payload)
        otext = norm(item_text(other)); ong = ngrams(otext)
        if qtext == otext: raise SystemExit(f"exact duplicate: {ocid}")
        jac = len(qng & ong) / len(qng | ong) if (qng or ong) else 0.0
        if jac >= 0.72: raise SystemExit(f"lexical duplicate {jac:.3f}: {ocid}")
        if canonical(other.get("semantic_fingerprint", {})) == fp:
            raise SystemExit(f"semantic fingerprint duplicate: {ocid}")

    before = con.execute("SELECT COUNT(*) FROM items WHERE status='PRODUCTION_READY'").fetchone()[0]
    if before >= 5040: raise SystemExit("target already reached")
    at = r["reviewed_at"]
    author_exec = "CHATGPT-DIRECT-" + ch[:24]
    blind_hash = sha_text("DIRECT_REVIEW_NO_BLIND|" + cid + "|" + rh)

    try:
        con.execute("BEGIN IMMEDIATE")
        con.execute("""INSERT INTO candidates(candidate_id,payload_json,payload_sha256,author_input_sha256,
                     author_model,author_execution_id,created_at) VALUES(?,?,?,?,?,?,?)""",
                    (cid, canonical(c), ch, c["hashes"]["author_input_sha256"],
                     "GPT-5.6 Sol direct", author_exec, at))
        add_event(con,cid,None,"CANDIDATE_CREATED","CHATGPT_DIRECT",c["hashes"]["author_input_sha256"],ch,at)
        con.execute("""INSERT INTO direct_reviews(candidate_id,review_json,review_sha256,model,reviewed_at)
                     VALUES(?,?,?,?,?)""",(cid,canonical(r),rh,r.get("model","GPT-5.6 Sol"),at))
        add_event(con,cid,"CANDIDATE_CREATED","DIRECT_REVIEW_PASSED","CHATGPT_DIRECT",rh,ch,at)
        con.execute("INSERT INTO decisions(candidate_id,verdict,decided_at,importer_version) VALUES(?,?,?,?)",
                    (cid,"PRODUCTION_READY",at,"direct-connector-v1"))
        con.execute("""INSERT INTO items(candidate_id,payload_json,payload_sha256,audit_sha256,blind_sha256,status,committed_at)
                     VALUES(?,?,?,?,?,'PRODUCTION_READY',?)""",(cid,canonical(c),ch,rh,blind_hash,at))
        add_event(con,cid,"DIRECT_REVIEW_PASSED","PRODUCTION_READY_COMMITTED","DIRECT_IMPORTER",rh,ch,at)
        con.commit()
    except:
        con.rollback()
        raise

    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok": raise SystemExit("post-import integrity failure")
    row = con.execute("SELECT payload_sha256,audit_sha256,status FROM items WHERE candidate_id=?",(cid,)).fetchone()
    if row != (ch,rh,"PRODUCTION_READY"): raise SystemExit("post-commit reread mismatch")
    after = con.execute("SELECT COUNT(*) FROM items WHERE status='PRODUCTION_READY'").fetchone()[0]
    if after != before + 1: raise SystemExit("counter delta mismatch")

    STATE.mkdir(parents=True, exist_ok=True)
    REVIEWED.mkdir(parents=True, exist_ok=True)
    (REVIEWED / f"{cid}.json").write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding="utf-8")
    (STATE / "last_run.json").write_text(json.dumps({
        "mode":"CHATGPT_DIRECT","candidate_id":cid,"before":before,"after":after,
        "accepted_this_run":1,"review_sha256":rh,"candidate_sha256":ch,
        "production_count_query":"SELECT COUNT(*) FROM items WHERE status='PRODUCTION_READY'"
    },indent=2),encoding="utf-8")
    print(f"{after}/5040")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("usage: direct_import.py REQUEST.json")
    raise SystemExit(main(sys.argv[1]))
