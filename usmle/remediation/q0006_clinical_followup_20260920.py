"""Rewrite duplicate Q0006 and apply reviewed corrections without a FINAL verdict."""
import hashlib, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CID = "S1-DIRECT-0006-20260827T020000Z"
EXPECTED = "f83cc8ead31d3dc785db46d7323accf9f85812168ccb86c39dad741a34284e2d"
AUDIT = "Q0006_CLINICAL_FOLLOWUP_20260920"


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def source(source_id, title, url, agency, government, date, locator, summary, sha, rights):
    return {
        "source_id": source_id,
        "title": title,
        "url": url,
        "agency": agency,
        "government_status_verified": government,
        "publication_or_revision_date": date,
        "retrieved_at": "2026-09-20",
        "section_locator": locator,
        "supporting_passage": summary,
        "passage_type": "Reviewer paraphrase, not a verbatim quotation",
        "raw_source_sha256": sha,
        "raw_capture_record": "audit/" + AUDIT + ".md",
        "set_id_applicability": "NOT_APPLICABLE_NON_DRUG_SOURCE",
        "rights_status": rights,
    }


def main():
    db = sqlite3.connect(ROOT / "data/usmle-step1.db")
    db.row_factory = sqlite3.Row
    archive_path = ROOT / "remediation" / (AUDIT + "_BEFORE_ROWS.json")
    with db:
        db.execute("BEGIN IMMEDIATE")
        old = dict(db.execute("select * from step2_final_items where candidate_id=?", (CID,)).fetchone())
        review = dict(db.execute("select * from step2_final_reviews where candidate_id=?", (CID,)).fetchone())
        payload = json.loads(old["payload_json"])
        if payload.get("current_reaudit", {}).get("audit_id") == AUDIT:
            assert digest(payload) == old["payload_sha256"] and archive_path.exists()
            print("Already applied; no rows changed")
            return
        assert old["payload_sha256"] == EXPECTED == digest(payload)

        payload["blueprint"].update(
            coverage_deficit_addressed="Parvovirus B19 transient aplastic crisis complicating hereditary spherocytosis.",
            disciplines=["Microbiology", "Pathology"],
            primary_system="Blood & Lymphoreticular System",
            official_outline_path=[
                "Blood & Lymphoreticular System",
                "Anemia, cytopenias, and polycythemia anemias",
                "disorders of hemoglobin, heme, or membrane",
                "hereditary spherocytosis",
            ],
        )
        payload["item"].update(
            vignette=(
                "A 12-year-old boy with hereditary spherocytosis has chronic mild anemia and splenomegaly. "
                "One week after close contact with a sibling who had fever and a slapped-cheek rash, he develops "
                "abrupt severe fatigue and pallor. His hemoglobin has fallen markedly from baseline, and the "
                "reticulocyte count is very low."
            ),
            lead_in="Which process most directly explains this patient's acute deterioration?",
            difficulty="moderate",
            reasoning_steps_count=2,
            difficulty_basis=(
                "Author estimate, not psychometrically calibrated: the examinee must identify a production failure "
                "from reticulocytopenia and connect fifth-disease exposure with parvovirus B19 suppression of "
                "erythropoiesis in a patient with shortened red-cell survival. No calculation is required."
            ),
            intended_key="C",
            options={
                "A": "Increased splenic clearance of IgG-coated erythrocytes",
                "B": "Oxidative hemoglobin injury due to deficient G6PD-derived NADPH",
                "C": "Parvovirus B19 infection of erythroid precursors with transient arrest of erythropoiesis",
                "D": "Decreased renal erythropoietin production",
                "E": "Folate deficiency causing megaloblastic erythropoiesis",
            },
            tested_construct=(
                "Parvovirus B19 targets erythroid progenitor cells and can transiently arrest erythropoiesis; in an "
                "underlying chronic hemolytic disorder, the abrupt reticulocytopenia can cause a severe aplastic crisis."
            ),
        )
        explanations = {
            "A": (
                "Incorrect. Warm autoimmune hemolytic anemia can cause splenic removal of IgG-coated erythrocytes, "
                "but active hemolysis ordinarily produces reticulocytosis. It does not account for the fifth-disease "
                "exposure and abrupt reticulocytopenia."
            ),
            "B": (
                "Incorrect. G6PD deficiency permits oxidant injury to hemoglobin and episodic hemolysis. This stem "
                "instead shows abrupt failure of marrow compensation, marked by a very low reticulocyte count."
            ),
            "C": (
                "Correct. Parvovirus B19 preferentially infects erythroid progenitor cells. Transient interruption of "
                "red-cell production produces profound reticulocytopenia and can cause a severe aplastic crisis when "
                "baseline red-cell survival is already shortened by hereditary spherocytosis."
            ),
            "D": (
                "Incorrect. Chronic kidney disease can lower erythropoietin and gradually reduce red-cell production, "
                "but there is no renal history and it does not explain the acute illness after fifth-disease exposure."
            ),
            "E": (
                "Incorrect. Folate deficiency can impair DNA synthesis and cause megaloblastic, ineffective "
                "erythropoiesis, but it develops insidiously and does not explain this abrupt exposure-linked crisis."
            ),
        }
        payload["explanation"] = {
            "key_explanation": explanations["C"],
            "distractor_explanations": explanations,
            "educational_objective": (
                "Use an abrupt hemoglobin decline with reticulocytopenia to distinguish parvovirus B19 aplastic crisis "
                "from increased hemolysis and chronic causes of reduced erythropoiesis."
            ),
        }
        source_ids = {"A": ["S4"], "B": ["S5"], "C": ["S1", "S2", "S3"], "D": ["S6"], "E": ["S7"]}
        diagnoses = {
            "A": "Warm autoimmune hemolytic anemia",
            "B": "G6PD deficiency",
            "C": "Parvovirus B19 transient aplastic crisis",
            "D": "Anemia of chronic kidney disease",
            "E": "Folate-deficiency megaloblastic anemia",
        }
        payload["evidence_map"] = [
            {
                "option": option,
                "claim": text,
                "rationale": explanations[option],
                "source_ids": source_ids[option],
                "evidence_basis": "LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION",
                "audit_record": "audit/" + AUDIT + ".md",
                "target_diagnosis_or_process": diagnoses[option],
                "target_mechanism": text,
            }
            for option, text in payload["item"]["options"].items()
        ]
        payload["sources"] = [
            source(
                "S1", "Hereditary spherocytosis",
                "https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/",
                "National Library of Medicine (NIH) — MedlinePlus Genetics", True,
                "Last updated September 1, 2013", "Description; Causes",
                "Hereditary spherocytosis is a membrane disorder with anemia, jaundice and splenomegaly caused by premature splenic red-cell destruction.",
                "78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b",
                "Official U.S. federal health-information source; facts used for original synthesis.",
            ),
            source(
                "S2", "About Parvovirus B19",
                "https://www.cdc.gov/parvovirus-b19/about/index.html",
                "Centers for Disease Control and Prevention", True,
                "December 17, 2025", "At a glance; Rashes; Complications",
                "Fifth disease can cause a slapped-cheek rash; parvovirus B19 can cause a severe anemia drop in hereditary spherocytosis.",
                "e2766f1db03c965a37f613d5f0d70347ff9890002e7c9c9574ef0a166106f237",
                "Official U.S. federal public-health source; facts used for original synthesis.",
            ),
            source(
                "S3", "Human parvovirus B19: a mechanistic overview of infection and DNA replication",
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC4470565/",
                "Luo and Qiu, Future Virology; hosted by PubMed Central", False,
                "2015; author manuscript available in PMC November 1, 2015", "Abstract; introductory clinical spectrum",
                "B19V mainly infects human erythroid progenitor cells and can cause transient aplastic crisis in patients with increased erythropoiesis.",
                "9cf828c7c3bf5e7170696d628bc4876485483546def8686c6ff1876bd756671c",
                "Third-party peer-reviewed article hosted by NCBI; NCBI hosting is not federal authorship.",
            ),
            source(
                "S4", "Autoimmune Hemolytic Anemia",
                "https://www.merckmanuals.com/professional/hematology/anemias-caused-by-hemolysis/autoimmune-hemolytic-anemia",
                "Merck Manual Professional Edition", False,
                "Full review and last update April 2026", "Warm antibody hemolytic anemia; Diagnosis",
                "Warm AIHA is usually IgG-mediated splenic hemolysis and generally presents with reticulocytosis; low reticulocytes are unusual and signal another complication.",
                "10d6a3700ca4ac106b29f5c640c42307bf84fe45db7611ee115c7c1902316eac",
                "Third-party professional reference; facts paraphrased for original educational content.",
            ),
            source(
                "S5", "G6PD gene", "https://medlineplus.gov/genetics/gene/g6pd/",
                "National Library of Medicine (NIH) — MedlinePlus Genetics", True,
                "Last updated April 12, 2023", "Normal Function; G6PD deficiency",
                "Erythrocytes depend on G6PD-derived NADPH to protect hemoglobin and other proteins from reactive oxygen species.",
                "b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655",
                "Official U.S. federal health-information source; facts used for original synthesis.",
            ),
            source(
                "S6", "Anemia in Chronic Kidney Disease",
                "https://www.niddk.nih.gov/health-information/kidney-disease/anemia",
                "National Institute of Diabetes and Digestive and Kidney Diseases (NIH)", True,
                "Last reviewed September 2020", "What causes anemia in CKD?",
                "Damaged kidneys produce less erythropoietin, so marrow produces fewer red blood cells; CKD anemia typically develops slowly.",
                "ed0ce208ee4c573c109027ef9146b2d2eb28035d666b2f3c69e69c408001698c",
                "Official U.S. federal health-information source; facts used for original synthesis.",
            ),
            source(
                "S7", "Megaloblastic Macrocytic Anemias",
                "https://www.merckmanuals.com/professional/hematology/anemias-caused-by-deficient-erythropoiesis/megaloblastic-macrocytic-anemias",
                "Merck Manual Professional Edition", False,
                "Full review and last update March 2025", "Etiology; Pathophysiology; Symptoms and Signs",
                "Folate deficiency can cause defective DNA synthesis, ineffective megaloblastic erythropoiesis and reticulocytopenia, but the anemia develops insidiously.",
                "6749ccc20ca457a01448dfd99fb87aaaab9298d4936ecb9d12256f076c47a3f2",
                "Third-party professional reference; facts paraphrased for original educational content.",
            ),
        ]
        payload["semantic_fingerprint"].update(
            correct_answer_concept=payload["item"]["options"]["C"],
            diagnosis_or_process="Parvovirus B19 transient aplastic crisis",
            essential_clues=[
                "underlying hereditary spherocytosis",
                "household exposure to slapped-cheek illness",
                "abrupt severe anemia",
                "very low reticulocyte count",
            ],
            lead_in_task=payload["item"]["lead_in"],
            mechanism=payload["item"]["tested_construct"],
            tested_construct=payload["item"]["tested_construct"],
            reasoning_chain=[
                "Interpret very low reticulocytes as acute failure of erythrocyte production rather than increased hemolysis.",
                "Connect fifth-disease exposure and chronic hemolysis with parvovirus B19 transient aplastic crisis.",
            ],
            distractor_misconceptions=[
                "mistaking increased immune hemolysis for marrow arrest",
                "mistaking oxidant hemolysis for reticulocytopenic anemia",
                "substituting chronic renal EPO deficiency for an acute exposure-linked event",
                "substituting insidious megaloblastic erythropoiesis for an acute aplastic crisis",
            ],
        )
        historical = payload.setdefault("historical_audit_metadata", {})
        for field in ("author_self_audit", "step2_final_audit", "hashes"):
            if field in payload:
                historical[field] = payload.pop(field)
        payload["current_reaudit"] = {
            "audit_id": AUDIT,
            "status": "BLOCKED_PENDING_FULL_REAUDIT",
            "full_clinical_certification": False,
            "same_reviewer_content_passes": 2,
            "independent_blind_passes": 0,
            "corrections": [
                "Resolve confirmed semantic duplicate Q1111 by rewriting the vignette, task and answer set around parvovirus B19 aplastic crisis",
                "Replace diagnosis-list distractors with five verified competing mechanisms",
                "Bind every alternative to separately inspected evidence",
                "Use the exact USMLE 2026 hereditary-spherocytosis outline path and remove non-USMLE NCJMM-style metadata",
                "Provide an item-specific difficulty estimate and reasoning count",
                "Isolate obsolete PASS metadata as historical",
            ],
            "duplicate_resolution": {
                "status": "CONFIRMED_SEMANTIC_DUPLICATE_RESOLVED_BY_FULL_CONSTRUCT_REWRITE",
                "duplicate_candidate_id": "S1-DIRECT-1111-20260902T100000Z",
                "old_construct": "Diagnosis of hereditary spherocytosis from familial hemolysis, splenomegaly and spherocytes",
                "new_construct": "Parvovirus B19 transient aplastic crisis in hereditary spherocytosis",
            },
            "remaining_gates": [
                "Independent isolated author/auditor workflow required by README",
                "Exhaustive semantic comparison beyond targeted candidate screening",
            ],
        }
        assert payload["item"]["intended_key"] == "C" and set(payload["item"]["options"]) == set("ABCDE")
        review_payload = {
            "candidate_id": CID,
            "verdict": "BLOCKED_PENDING_FULL_REAUDIT",
            "payload_sha256": digest(payload),
            "prior_review_sha256": review["review_sha256"],
            "reviewed_at": "2026-09-20",
            "audit_record": "audit/" + AUDIT + ".md",
            "review_scope": "Duplicate resolution, live claim review, evidence repair and same-reviewer adversarial reread; not independent certification",
            "defects": payload["current_reaudit"]["remaining_gates"],
        }
        archive = {"item_row": old, "review_row": review}
        if archive_path.exists():
            assert json.loads(archive_path.read_text()) == archive
        else:
            archive_path.write_text(json.dumps(archive, indent=2) + "\n")
        db.execute(
            "update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?",
            (canon(payload), digest(payload), digest(review_payload), review_payload["verdict"], "2026-09-20", CID),
        )
        db.execute(
            "update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?",
            (canon(review_payload), digest(review_payload), review_payload["verdict"], "2026-09-20", CID),
        )
        assert db.execute("pragma integrity_check").fetchone()[0] == "ok"
    result = {
        "candidate_id": CID,
        "before_sha256": EXPECTED,
        "after_sha256": digest(payload),
        "status": review_payload["verdict"],
        "duplicate_resolved": "S1-DIRECT-1111-20260902T100000Z",
        "new_final_passes": 0,
        "item_count": 1635,
    }
    (ROOT / "audit" / (AUDIT + "_RESULT.json")).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
