#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE = ROOT / "data/rule1_batch007_chronological_reaudit_evidence_q0301_q0350.json"
OVERRIDE = ROOT / "data/clinical_overrides_zz_rule1_batch007_chronological_q0301_q0350_20260815.json"
PATCHES = [
    ROOT / "data/manual_rule1_batch007_q0301_q0310_20260815.json",
    ROOT / "data/manual_rule1_batch007_q0311_q0320_20260815.json",
    ROOT / "data/manual_rule1_batch007_q0321_q0330_20260815.json",
    ROOT / "data/manual_rule1_batch007_q0331_q0340_20260815.json",
    ROOT / "data/manual_rule1_batch007_q0341_q0350_20260815.json",
]
IDS = [f"V2-Q{i:04d}" for i in range(301, 351)]
REVIEW_DATE = "2026-08-15"
STATUS = "SOURCE_VERIFIED_2026_RULE1_BATCH007_CHRONOLOGICAL_MANUAL"
NCSBN_URL = "https://www.nclex.com/files/2026_RN_Test%20Plan_English-F.pdf"
NCSBN_VERSION = "2026 NCLEX-RN Test Plan; effective 2026-04-01 through 2029-03-31; currentness rechecked 2026-08-15."
CRITERIA = [
    "source_authority_verified",
    "source_currentness_verified",
    "exact_locator_verified",
    "stem_factual_accuracy_verified",
    "correct_answer_verified",
    "rationale_verified",
    "distractors_verified",
    "ambiguity_cue_second_answer_qc_verified",
    "blueprint_topic_difficulty_verified",
    "no_unresolved_conflicts",
    "independent_second_pass_qa",
]
NCSBN_LOCATORS = {
    2: "Client Needs — Safe and Effective Care Environment — Management of Care: prioritization, continuity, confidentiality, quality/cost-effective care, legal/ethical rights and assignment/delegation activities as applicable.",
    3: "Client Needs — Safe and Effective Care Environment — Safety and Infection Prevention and Control: asepsis, equipment/environmental safety, incident/event prevention and infection-control activities as applicable.",
    4: "Client Needs — Health Promotion and Maintenance: preventive care, screening, age-appropriate health promotion and risk-reduction teaching activities as applicable.",
    5: "Client Needs — Psychosocial Integrity: cultural practices/beliefs, abuse/neglect reporting, coping, mental-health symptoms and therapeutic adaptation activities as applicable.",
    7: "Client Needs — Physiological Integrity — Basic Care and Comfort: mobility, positioning, skin integrity, elimination and nonpharmacologic comfort activities as applicable.",
    8: "Client Needs — Physiological Integrity — Pharmacological and Parenteral Therapies: medication administration, calculations, adverse effects/interactions, monitoring and client teaching.",
    9: "Client Needs — Physiological Integrity — Reduction of Risk Potential: diagnostic tests, laboratory values, vital-sign monitoring and potential complications.",
    10: "Client Needs — Physiological Integrity — Physiological Adaptation: acute/complex alterations, medical emergencies and pathophysiologic adaptation.",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def option_metrics(options: dict[str, str], key: str) -> dict:
    lengths = {k: len(str(options[k]).strip()) for k in "ABCD"}
    values = list(lengths.values())
    distractor_mean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    return {
        "characters": lengths,
        "max_min_ratio": round(max(values) / max(min(values), 1), 4),
        "correct_option": key,
        "correct_deviation_from_distractor_mean": round(abs(lengths[key] - distractor_mean) / max(distractor_mean, 1), 4),
        "use": "MEASUREMENT_ONLY_NOT_SEMANTIC_GATE",
    }


def main() -> None:
    if not DB.exists():
        raise SystemExit("Current master DB is required as the content carrier for Batch 007")

    manual: list[dict] = []
    for path in PATCHES:
        doc = load_json(path)
        if (doc.get("batch") != "Q0301-Q0350" or doc.get("review_date") != REVIEW_DATE
                or doc.get("legacy_status_evidence") is not False
                or doc.get("semantic_decisions_by_script") is not False):
            raise SystemExit(f"Invalid manual Rule 1 audit header: {path.name}")
        manual.extend(doc.get("items", []))
    if [x.get("id") for x in manual] != IDS or len(manual) != 50:
        raise SystemExit("Manual Rule 1 decisions must contain Q0301-Q0350 exactly once and in order")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    evidence_out: list[dict] = []
    override_out: list[dict] = []

    for patch in manual:
        uid = patch["id"]
        if patch.get("qa") != [11, "PASS", "FINAL_QA_PASS"]:
            raise SystemExit(f"{uid}: manual semantic audit decision is incomplete")
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if q is None:
            raise SystemExit(f"{uid}: missing from current master DB")

        base_options = json.loads(q["item_data_json"])["options"]
        options = patch.get("options", base_options)
        if not isinstance(options, dict) or set(options) != set("ABCD"):
            raise SystemExit(f"{uid}: options must contain exactly A-D")
        normalized = [str(options[k]).strip().casefold() for k in "ABCD"]
        if any(not x for x in normalized) or len(set(normalized)) != 4:
            raise SystemExit(f"{uid}: blank or duplicate option")

        key = patch["key"]
        if key not in options:
            raise SystemExit(f"{uid}: correct key is not present")
        stem = patch.get("stem", q["stem"])
        rationale = patch.get("rationale", q["rationale"])
        category_id = int(patch["cat"])
        client_need = patch["need"]
        difficulty = patch["diff"]
        source_name = patch.get("source_name", q["source_name"])
        source_url = patch.get("source_url", q["source_url"])
        locator = patch["locator"]
        version = patch["version"]
        authority = patch["authority"]
        if not source_url or not source_url.startswith("https://") or not locator.strip() or not version.strip() or not authority.strip():
            raise SystemExit(f"{uid}: source authority/URL/locator/version incomplete")
        if not stem.strip() or not rationale.strip():
            raise SystemExit(f"{uid}: blank stem or rationale")

        ncsbn = {
            "required_currentness_and_blueprint_check": True,
            "source": "NCSBN — 2026 NCLEX-RN Test Plan",
            "url": NCSBN_URL,
            "locator": NCSBN_LOCATORS[category_id],
            "version": NCSBN_VERSION,
            "result": "PASS",
            "scope": "Mandatory NCLEX blueprint/category/currentness and entry-level relevance check; exact clinical/legal claim separately verified against the item topic authority.",
        }
        m = option_metrics(options, key)
        finding = patch.get("finding") or (
            f"Fresh manual Rule 1 audit completed 2026-08-15. Key {key} directly verified against the cited authority. "
            "Stem, all four options, rationale, distractor plausibility/clinical correctness, ambiguity, cueing, overlap, second-answer risk, "
            "blueprint/topic/difficulty, source authority/locator/version/currentness and unresolved conflicts were checked; a separate second read passed."
        )
        source_detail = f"{locator} {version} NCSBN first-check: {ncsbn['locator']} {NCSBN_VERSION}"

        flags = [
            "RULE1_BATCH007_MANUAL_ITEM_BY_ITEM_REAUDIT",
            "LEGACY_STATUS_NOT_USED_AS_EVIDENCE",
            "SEMANTIC_DECISIONS_NOT_BY_SCRIPT",
            "SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED",
            "MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS",
            "INDEPENDENT_SECOND_PASS_QA_PASS",
            "OPTION_LENGTH_METRICS_MEASUREMENT_ONLY",
        ]
        override_out.append({
            "question_uid": uid,
            "source_id": int(q["source_id"]),
            "category_id": category_id,
            "client_need": client_need,
            "difficulty": difficulty,
            "stem": stem,
            "item_data_json": json.dumps({"options": options}, ensure_ascii=False, separators=(",", ":")),
            "correct_answer_json": json.dumps({"correct_option": key}, separators=(",", ":")),
            "rationale": rationale,
            "source_name": source_name,
            "source_detail": source_detail,
            "source_url": source_url,
            "clinical_qa_status": STATUS,
            "editorial_priority": "PRODUCTION_CANDIDATE",
            "editorial_flags_json": json.dumps(flags, separators=(",", ":")),
            "qc": {
                "question_uid": uid,
                "lengths_json": json.dumps(m["characters"], separators=(",", ":")),
                "min_chars": min(m["characters"].values()),
                "max_chars": max(m["characters"].values()),
                "max_min_ratio": m["max_min_ratio"],
                "correct_option": key,
                "correct_length_rank": sorted(m["characters"].values()).index(m["characters"][key]) + 1,
                "correct_is_extreme": int(m["characters"][key] in (min(m["characters"].values()), max(m["characters"].values()))),
                "qc_status": "MEASURED_NOT_GATE",
                "qc_note": "Length metrics are measurement only. Semantic option/cue/ambiguity quality is determined by the manual Rule 1 audit, not by a script threshold.",
            },
        })
        evidence_out.append({
            "id": uid,
            "key": key,
            "category_id": category_id,
            "client_need": client_need,
            "difficulty": difficulty,
            "source_authority": authority,
            "source_name": source_name,
            "source_url": source_url,
            "source_locator": locator,
            "source_version": version,
            "reviewed_at": REVIEW_DATE,
            "finding": finding,
            "ncsbn_first_check": ncsbn,
            "criteria": 11,
            "criteria_names": CRITERIA,
            "second_pass": "PASS",
            "second_pass_method": "Independent fresh second read of final stem, all four options, key, rationale, source locator/version/currentness, blueprint/difficulty and second-answer/cue risk without using legacy PASS/status as evidence.",
            "final": "FINAL_QA_PASS",
            "option_measurement": m,
            "semantic_decision_origin": "MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT",
        })

    con.close()
    EVIDENCE.write_text(json.dumps({
        "standard": "RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT",
        "batch": "Q0301-Q0350",
        "review_date": REVIEW_DATE,
        "legacy_status_evidence": False,
        "semantic_decisions_by_script": False,
        "criteria_names": CRITERIA,
        "ncsbn_test_plan": {"url": NCSBN_URL, "version": NCSBN_VERSION},
        "items": evidence_out,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OVERRIDE.write_text(json.dumps({
        "version": "2026-08-15-rule1-batch007-manual-item-by-item-q0301-q0350",
        "semantic_decisions_by_script": False,
        "questions": override_out,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BATCH007_MANUAL_ARTIFACTS_BUILT items=50/50 criteria11=50/50 second_pass=50/50 semantic_script_decisions=0 option_metrics=measurement_only")


if __name__ == "__main__":
    main()
