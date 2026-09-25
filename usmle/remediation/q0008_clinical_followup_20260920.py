"""Repair Q0008's hemophilia-A/B ambiguity without granting FINAL status."""
import hashlib, json, sqlite3
from pathlib import Path
from q0006_clinical_followup_20260920 import canon, digest

ROOT = Path(__file__).resolve().parents[1]
CID = "S1-DIRECT-0008-20260827T020000Z"
EXPECTED = "b55de3da8c3dbe1069842d30d3ef435640a68a990420a048d17c3c0d0fdaaa8a"
AUDIT = "Q0008_CLINICAL_FOLLOWUP_20260920"

def src(i, title, url, date, locator, text):
    return dict(source_id=i, title=title, url=url, agency="NLM/NIH — MedlinePlus Genetics",
        government_status_verified=True, publication_or_revision_date=date, retrieved_at="2026-09-20",
        section_locator=locator, supporting_passage=text,
        supporting_passage_sha256=hashlib.sha256(text.encode()).hexdigest(),
        passage_type="Reviewer paraphrase, not a verbatim quotation",
        raw_capture_status="Live source inspected; raw response hash unavailable in this execution environment",
        set_id_applicability="NOT_APPLICABLE_NON_DRUG_SOURCE",
        rights_status="Federal educational source; facts paraphrased", evidence_record="audit/"+AUDIT+".md")

def main():
    db=sqlite3.connect(ROOT/"data/usmle-step1.db"); db.row_factory=sqlite3.Row
    ap=ROOT/"remediation"/(AUDIT+"_BEFORE_ROWS.json")
    with db:
        db.execute("BEGIN IMMEDIATE")
        old=dict(db.execute("select * from step2_final_items where candidate_id=?",(CID,)).fetchone())
        rev=dict(db.execute("select * from step2_final_reviews where candidate_id=?",(CID,)).fetchone())
        p=json.loads(old["payload_json"])
        if p.get("current_reaudit",{}).get("audit_id")==AUDIT:
            assert digest(p)==old["payload_sha256"] and ap.exists(); print("Already applied; no rows changed"); return
        assert old["payload_sha256"]==EXPECTED==digest(p)
        p["blueprint"].update(primary_system="Blood & Lymphoreticular System", official_outline_path=[
            "Blood & Lymphoreticular System","Coagulation disorders (hypocoagulable and hypercoagulable conditions)",
            "hypocoagulable","hemophilia, congenital; factors VIII [hemophilia A] and IX [hemophilia B]"],
            coverage_deficit_addressed="Distinguish congenital factor VIII deficiency from other inherited coagulation disorders using factor-specific assays.")
        p["item"].update(
            vignette=("An 8-year-old boy has recurrent hemarthroses after minor trauma. His maternal uncle had similar episodes. "
                "Platelet count and prothrombin time are normal, and activated partial thromboplastin time is prolonged. "
                "A mixing study corrects the prolonged activated partial thromboplastin time. Factor IX activity and von Willebrand factor antigen and activity are normal."),
            lead_in="Which coagulation protein is most likely deficient?", difficulty="easy", reasoning_steps_count=2,
            difficulty_basis=("Author estimate, not psychometrically calibrated: recognize an inherited intrinsic-pathway factor deficiency from the phenotype and corrected mixing study, then use normal factor IX and VWF assays to identify factor VIII. No calculation is required."),
            options={"A":"Factor VIII","B":"Factor IX","C":"Factor XI","D":"Factor XIII","E":"von Willebrand factor"},
            tested_construct=("Congenital factor VIII deficiency causes hemophilia A; factor-specific testing distinguishes it from hemophilia B and VWF-related bleeding."))
        r={
            "A":"Correct. Deep joint bleeding, an X-linked family pattern, an isolated prolonged aPTT that corrects with normal plasma, normal factor IX activity, and normal VWF testing together support congenital factor VIII deficiency (hemophilia A).",
            "B":"Incorrect. Factor IX deficiency causes hemophilia B and can otherwise produce the same inheritance, bleeding pattern, and screening tests. The normal factor IX activity is the decisive exclusion in this stem.",
            "C":"Incorrect. Factor XI deficiency can prolong aPTT and cause procedural or trauma-related bleeding, but spontaneous hemarthroses are less characteristic; it also does not explain the factor-specific exclusion pattern as well as factor VIII deficiency.",
            "D":"Incorrect. Factor XIII stabilizes a formed clot by cross-linking fibrin. Factor XIII deficiency typically is not detected by PT or aPTT, so it does not explain this isolated prolonged aPTT.",
            "E":"Incorrect. VWF supports platelet adhesion and carries factor VIII. Normal VWF antigen and activity make VWF deficiency or dysfunction an inferior explanation for this item; those results do not themselves measure factor VIII activity."
        }
        p["explanation"]=dict(key_explanation=r["A"],distractor_explanations=r,
            educational_objective="Distinguish hemophilia A from hemophilia B and other inherited bleeding disorders by combining the bleeding phenotype and mixing study with factor-specific and VWF assays.")
        p["sources"]=[
            src("S1","F8 gene","https://medlineplus.gov/genetics/gene/f8/","May 1, 2010","Normal Function; Health Conditions Related to Genetic Changes","Factor VIII circulates with VWF; activated factor VIII works with factor IX in coagulation, and F8 variants cause hemophilia A."),
            src("S2","F9 gene","https://medlineplus.gov/genetics/gene/f9/","May 1, 2010","Normal Function; Health Conditions Related to Genetic Changes","Activated factor IX participates with factor VIII in coagulation, and F9 variants cause hemophilia B."),
            src("S3","Factor XI deficiency","https://medlineplus.gov/genetics/condition/factor-xi-deficiency/","August 1, 2018","Description; Causes; Inheritance","Factor XI deficiency causes variable bleeding, often after trauma or surgery, and is caused by F11 variants."),
            src("S4","F13A1 gene","https://medlineplus.gov/genetics/gene/f13a1/","September 1, 2015","Normal Function","Activated factor XIII cross-links fibrin near the end of coagulation and stabilizes the clot."),
            src("S5","VWF gene","https://medlineplus.gov/genetics/gene/vwf/","December 1, 2012","Normal Function","VWF supports platelet adhesion at vascular injury and transports factor VIII."),
            src("S6","Hemophilia","https://medlineplus.gov/genetics/condition/hemophilia/","May 6, 2022","Description; Causes; Inheritance","Hemophilia A and B are caused by deficient factor VIII and IX activity, respectively; severe disease causes joint and deep-tissue bleeding and is commonly X-linked.")]
        binds={"A":["S1","S6"],"B":["S2","S6"],"C":["S3"],"D":["S4"],"E":["S5"]}
        p["evidence_map"]=[dict(option=o,claim=p["item"]["options"][o],rationale=r[o],source_ids=binds[o],
            target_diagnosis_or_process=p["item"]["options"][o],evidence_basis="LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION") for o in "ABCDE"]
        p["semantic_fingerprint"].update(lead_in_task=p["item"]["lead_in"],tested_construct=p["item"]["tested_construct"],
            mechanism="Factor VIII deficiency after explicit exclusion of factor IX and VWF abnormalities",
            essential_clues=["recurrent hemarthroses","maternal uncle affected","isolated prolonged aPTT correcting on mixing","normal factor IX activity","normal VWF antigen and activity"],
            reasoning_chain=["Identify an inherited intrinsic-pathway factor deficiency.","Use factor-specific and VWF assays to select factor VIII."],
            distractor_misconceptions=["failing to distinguish hemophilia B","overgeneralizing procedural bleeding in factor XI deficiency","assuming factor XIII deficiency prolongs aPTT","equating VWF carriage of factor VIII with VWF deficiency"])
        hist=p.setdefault("historical_audit_metadata",{})
        for f in ("author_self_audit","step2_final_audit","hashes"):
            if f in p: hist[f]=p.pop(f)
        p["current_reaudit"]=dict(audit_id=AUDIT,status="BLOCKED_PENDING_FULL_REAUDIT",full_clinical_certification=False,
            same_reviewer_content_passes=2,independent_blind_passes=0,
            corrections=["Resolve the original hemophilia-A/B second-answer defect","Replace awkward or remote alternatives with real inherited hemostatic disorders","Bind each alternative to disease-specific evidence","Repair exact USMLE outline hierarchy","Replace generic difficulty text with an author estimate"],
            targeted_originality_review={"Q0406":"Related reciprocal hemophilia-B diagnosis item; Q0008 explicitly tests factor VIII after normal IX/VWF assays. Not adjudicated as exhaustively original."},
            remaining_gates=["Isolated different-family audit required by README","Exhaustive semantic originality beyond targeted screening","Durable raw-source archival beyond passage hashes and claim summaries"])
        review=dict(candidate_id=CID,verdict="BLOCKED_PENDING_FULL_REAUDIT",payload_sha256=digest(p),prior_review_sha256=rev["review_sha256"],reviewed_at="2026-09-20",audit_record="audit/"+AUDIT+".md",defects=p["current_reaudit"]["remaining_gates"])
        archive=dict(item_row=old,review_row=rev)
        if ap.exists(): assert json.loads(ap.read_text())==archive
        else: ap.write_text(json.dumps(archive,indent=2)+"\n")
        db.execute("update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?",(canon(p),digest(p),digest(review),review["verdict"],"2026-09-20",CID))
        db.execute("update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?",(canon(review),digest(review),review["verdict"],"2026-09-20",CID))
        assert db.execute("pragma integrity_check").fetchone()[0]=="ok"
    result=dict(candidate_id=CID,before_sha256=EXPECTED,after_sha256=digest(p),new_final_passes=0,status=review["verdict"])
    (ROOT/"audit"/(AUDIT+"_RESULT.json")).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))

if __name__=="__main__": main()
