#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, re, sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "usmle-step1.db"
CAND_DIR = ROOT / "batch_specs_1201_1300" / "q1226_q1230_r2"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
STOP = {"the","and","for","with","that","this","from","into","most","which","patient","patients","cell","cells","normal","shows","show","which","directly","defect","signaling","loss","function","genetic","testing","identifies","receptor","receptors"}
TERMS = {
    "Q1226": ["aire", "tissue-restricted", "medullary thymic", "negative selection"],
    "Q1227": ["tap2", "transporter associated with antigen", "mhc class i deficiency", "bare lymphocyte syndrome"],
    "Q1228": ["il2rg", "common gamma chain", "t-b+nk-", "x-linked scid"],
    "Q1229": ["zap70", "zap-70", "anti-cd3", "pma", "ionomycin"],
    "Q1230": ["myd88", "irak4", "toll-like receptor", "interleukin-1 receptor"]
}

def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x, list):
        for v in x: yield from strings(v)

def text_of(x): return " ".join(strings(x))
def toks(s): return [t for t in TOKEN_RE.findall(s.casefold()) if len(t) > 2 and t not in STOP]
def vec(ts, idf):
    c=Counter(ts)
    return {k:(1+math.log(v))*idf.get(k,1.0) for k,v in c.items()}
def cos(a,b):
    if not a or not b: return 0.0
    n=sum(a[k]*b[k] for k in set(a)&set(b))
    da=math.sqrt(sum(v*v for v in a.values())); db=math.sqrt(sum(v*v for v in b.values()))
    return n/(da*db) if da and db else 0.0

def compact(i):
    return {"vignette":i.get("vignette"),"lead_in":i.get("lead_in"),"options":i.get("options"),"intended_key":i.get("intended_key"),"tested_construct":i.get("tested_construct")}

def main():
    db=DB.resolve(strict=True)
    files=[CAND_DIR/f"Q{n}.json" for n in range(1226,1231)]
    docs={f.stem:json.loads(f.read_text(encoding="utf-8")) for f in files}
    validation={}
    for q,d in docs.items():
        item=d["item"]
        opts=item.get("options",{})
        validation[q]={
            "num_matches_filename": str(d.get("num"))==q[1:],
            "five_options": list(opts.keys())==["A","B","C","D","E"],
            "key_exists": item.get("intended_key") in opts,
            "candidate_frozen": d.get("status")=="CANDIDATE_FROZEN",
            "production_import_permitted_false": d.get("production_import_permitted") is False,
            "zero_trust_no_remaining_defects": d.get("zero_trust_audit",{}).get("material_defects_remaining")==0,
            "ncjmm_absent": "ncjmm" not in text_of(d).casefold(),
        }
    key_dist=Counter(d["item"]["intended_key"] for d in docs.values())

    db_sha=hashlib.sha256(db.read_bytes()).hexdigest()
    with sqlite3.connect(db.as_uri()+"?mode=ro", uri=True) as con:
        con.execute("PRAGMA query_only=ON")
        integrity=[r[0] for r in con.execute("PRAGMA integrity_check").fetchall()]
        rows=con.execute("SELECT candidate_id,payload_json,payload_sha256,final_status FROM step2_final_items ORDER BY candidate_id").fetchall()
        status_counts=dict(con.execute("SELECT final_status,COUNT(*) FROM step2_final_items GROUP BY final_status").fetchall())
    prod=[]; mismatches=[]
    for cid,payload,stored,status in rows:
        calc=hashlib.sha256(payload.encode()).hexdigest()
        if calc!=stored: mismatches.append(cid)
        obj=json.loads(payload); item=obj.get("item",obj)
        prod.append({"candidate_id":cid,"status":status,"item":item,"text":text_of(item)})

    term_hits={}
    for q,terms in TERMS.items():
        term_hits[q]={}
        for term in terms:
            needle=term.casefold()
            hits=[]
            for r in prod:
                if needle in r["text"].casefold(): hits.append({"candidate_id":r["candidate_id"],"item":compact(r["item"])})
            term_hits[q][term]=hits

    pt=[toks(r["text"]) for r in prod]; n=len(pt); df=Counter()
    for ts in pt: df.update(set(ts))
    idf={t:math.log((n+1)/(f+1))+1 for t,f in df.items()}
    pv=[vec(ts,idf) for ts in pt]
    nearest={}
    for q,d in docs.items():
        ctext=text_of(d["item"]); ct=toks(ctext); cv=vec(ct,idf); cs=set(ct)
        scored=[]
        for r,ts,v in zip(prod,pt,pv):
            score=cos(cv,v); overlap=sorted(cs & set(ts), key=lambda t:idf.get(t,0), reverse=True)[:18]
            scored.append((score,r,overlap))
        scored.sort(key=lambda x:x[0], reverse=True)
        nearest[q]=[{"candidate_id":r["candidate_id"],"tfidf_cosine":round(s,6),"overlap":o,"item":compact(r["item"])} for s,r,o in scored[:12]]

    out={
        "batch":"Q1226-Q1230",
        "db_sha256":db_sha,
        "sqlite_integrity_check":integrity,
        "row_count":len(rows),
        "status_counts":status_counts,
        "payload_hash_mismatches":mismatches,
        "candidate_validation":validation,
        "answer_key_distribution":dict(sorted(key_dist.items())),
        "term_hits":term_hits,
        "nearest_neighbours":nearest,
        "production_db_modified":False,
        "note":"TF-IDF and term hits are retrieval evidence only. Final semantic duplicate determination requires adversarial review of retrieved neighbours."
    }
    print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=="__main__": main()
