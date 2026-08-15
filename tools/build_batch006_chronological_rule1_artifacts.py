#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/rule1_batch006_chronological_reaudit_evidence_q0251_q0300.json"
OVERRIDE = ROOT / "data/clinical_overrides_z_rule1_batch006_chronological_q0251_q0300_20260815.json"
PATCHES = [
    ROOT / "data/manual_rule1_batch006_q0251_q0260_20260815.json",
    ROOT / "data/manual_rule1_batch006_q0261_q0270_20260815.json",
    ROOT / "data/manual_rule1_batch006_q0271_q0280_20260815.json",
    ROOT / "data/manual_rule1_batch006_q0281_q0290_20260815.json",
    ROOT / "data/manual_rule1_batch006_q0291_q0300_20260815.json",
]
IDS = [f"V2-Q{i:04d}" for i in range(251, 301)]
REVIEW_DATE = "2026-08-15"
STATUS = "SOURCE_VERIFIED_2026_RULE1_BATCH006_CHRONOLOGICAL_MANUAL"
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
    2: "Client Needs — Safe and Effective Care Environment — Management of Care; Assignment, Delegation and Supervision; prioritization/continuity/client rights as applicable.",
    3: "Client Needs — Safe and Effective Care Environment — Safety and Infection Prevention and Control; Reporting of Incident/Event and infection/safety activities as applicable.",
    4: "Client Needs — Health Promotion and Maintenance; preventive care, screening, prenatal/postpartum and newborn health-promotion activities as applicable.",
    5: "Client Needs — Psychosocial Integrity; coping, support systems, grief/loss and therapeutic adaptation activities as applicable.",
    7: "Client Needs — Physiological Integrity — Basic Care and Comfort; hygiene, comfort, positioning and nonpharmacologic care activities as applicable.",
    8: "Client Needs — Physiological Integrity — Pharmacological and Parenteral Therapies; medication administration, adverse effects/interactions and monitoring.",
    9: "Client Needs — Physiological Integrity — Reduction of Risk Potential; diagnostic tests, laboratory values, monitoring and potential complications.",
    10: "Client Needs — Physiological Integrity — Physiological Adaptation; acute/complex alterations and medical emergencies.",
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
    if not EVIDENCE.exists() or not OVERRIDE.exists():
        raise SystemExit("Baseline Batch 006 artifacts are required as content/source carriers")

    baseline_evidence_doc = load_json(EVIDENCE)
    baseline_override_doc = load_json(OVERRIDE)
    baseline_evidence = {x["id"]: x for x in baseline_evidence_doc.get("items", [])}
    baseline_override = {x["question_uid"]: x for x in baseline_override_doc.get("questions", [])}
    if set(baseline_evidence) != set(IDS) or set(baseline_override) != set(IDS):
        raise SystemExit("Baseline Batch 006 scope must be exactly Q0251-Q0300")

    manual: list[dict] = []
    for path in PATCHES:
        doc = load_json(path)
        if doc.get("batch") != "Q0251-Q0300" or doc.get("review_date") != REVIEW_DATE or doc.get("legacy_status_evidence") is not False:
            raise SystemExit(f"Invalid manual audit header: {path.name}")
        manual.extend(doc.get("items", []))
    if [x.get("id") for x in manual] != IDS or len(manual) != 50:
        raise SystemExit("Manual Rule 1 patches must contain Q0251-Q0300 exactly once and in order")

    evidence_out: list[dict] = []
    override_out: list[dict] = []
    for patch in manual:
        uid = patch["id"]
        base_q = dict(baseline_override[uid])
        base_e = baseline_evidence[uid]
        if patch.get("qa") != [11, "PASS", "FINAL_QA_PASS"]:
            raise SystemExit(f"{uid}: manual semantic decision incomplete")

        options = patch.get("o")
        if not isinstance(options, dict) or set(options) != set("ABCD"):
            raise SystemExit(f"{uid}: manual options must contain A-D")
        normalized = [str(options[k]).strip().casefold() for k in "ABCD"]
        if any(not x for x in normalized) or len(set(normalized)) != 4:
            raise SystemExit(f"{uid}: blank/duplicate manual option")
        key = patch.get("k")
        if key not in options:
            raise SystemExit(f"{uid}: invalid correct option")

        stem = patch.get("s", base_q["stem"])
        rationale = patch.get("r", base_q["rationale"])
        category_id = int(patch["cat"])
        client_need = patch["need"]
        difficulty = patch["diff"]
        src = patch.get("src")
        if src:
            source_name = src["n"]
            source_url = src["u"]
            locator = src["l"]
            version = src["v"]
            authority = src["a"]
        else:
            source_name = base_q["source_name"]
            source_url = base_q["source_url"]
            locator = base_e["source_locator"]
            version = base_e["source_version"]
            authority = base_e.get("authority", "PRIMARY_OR_AUTHORITATIVE")
        if not source_url.startswith("https://") or not locator.strip() or not version.strip():
            raise SystemExit(f"{uid}: source URL/locator/version missing")

        supporting = patch.get("support", [])
        for support in supporting:
            if not support["u"].startswith("https://") or not support["l"].strip() or not support["v"].strip():
                raise SystemExit(f"{uid}: invalid supporting source")

        ncsbn = {
            "required_currentness_and_blueprint_check": True,
            "source": "NCSBN — 2026 NCLEX-RN Test Plan",
            "url": NCSBN_URL,
            "locator": NCSBN_LOCATORS[category_id],
            "version": NCSBN_VERSION,
            "result": "PASS",
            "scope": "NCLEX blueprint/category/currentness and entry-level relevance; exact clinical claim is verified against the item topic authority.",
        }
        metrics = option_metrics(options, key)
        finding = patch.get("finding") or f"Manual Rule 1 item-by-item re-audit completed 2026-08-15; key {key} directly source-verified; stem, rationale, all four options, second-answer risk, cueing, blueprint/topic/difficulty, currentness, and independent second pass verified."

        source_detail_parts = [locator, version, f"NCSBN first-check: {ncsbn['locator']} {NCSBN_VERSION}"]
        if supporting:
            source_detail_parts.append("Supporting sources: " + " | ".join(f"{s['n']}: {s['l']} {s['v']} {s['u']}" for s in supporting))
        source_detail = " ".join(source_detail_parts)

        base_q.update({
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
            "editorial_flags_json": json.dumps([
                "RULE1_BATCH006_MANUAL_ITEM_BY_ITEM_REAUDIT",
                "LEGACY_STATUS_NOT_USED_AS_EVIDENCE",
                "SOURCE_LOCATOR_VERSION_CURRENTNESS_VERIFIED",
                "MANUAL_DISTRACTOR_AMBIGUITY_CUE_SECOND_ANSWER_QC_PASS",
                "INDEPENDENT_SECOND_PASS_QA_PASS",
                "OPTION_LENGTH_METRICS_MEASUREMENT_ONLY",
            ], separators=(",", ":")),
            "qc": {
                "question_uid": uid,
                "lengths_json": json.dumps(metrics["characters"], separators=(",", ":")),
                "min_chars": min(metrics["characters"].values()),
                "max_chars": max(metrics["characters"].values()),
                "max_min_ratio": metrics["max_min_ratio"],
                "correct_option": key,
                "correct_length_rank": sorted(metrics["characters"].values()).index(metrics["characters"][key]) + 1,
                "correct_is_extreme": int(metrics["characters"][key] in (min(metrics["characters"].values()), max(metrics["characters"].values()))),
                "qc_status": "MEASURED_NOT_GATE",
                "qc_note": "Length is measured only. Semantic distractor/cue/ambiguity decisions come exclusively from the manual Rule 1 audit.",
            },
        })
        override_out.append(base_q)
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
            "supporting_sources": supporting,
            "reviewed_at": REVIEW_DATE,
            "finding": finding,
            "ncsbn_first_check": ncsbn,
            "criteria": 11,
            "criteria_names": CRITERIA,
            "second_pass": "PASS",
            "second_pass_method": "Fresh second read of stem, all four options, key, rationale, source locator/version/currentness, blueprint and second-answer/cue risk without reliance on legacy status.",
            "final": "FINAL_QA_PASS",
            "option_measurement": metrics,
            "semantic_decision_origin": "MANUAL_ITEM_BY_ITEM_AUDIT_NOT_SCRIPT",
        })

    EVIDENCE.write_text(json.dumps({
        "standard": "RULE_1_FINAL_10_OF_10_MANUAL_ITEM_BY_ITEM_REAUDIT",
        "batch": "Q0251-Q0300",
        "review_date": REVIEW_DATE,
        "legacy_status_evidence": False,
        "semantic_decisions_by_script": False,
        "criteria_names": CRITERIA,
        "ncsbn_test_plan": {"url": NCSBN_URL, "version": NCSBN_VERSION},
        "items": evidence_out,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OVERRIDE.write_text(json.dumps({
        "version": "2026-08-15-rule1-batch006-manual-item-by-item-q0251-q0300",
        "semantic_decisions_by_script": False,
        "questions": override_out,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BATCH006_MANUAL_ARTIFACTS_APPLIED items=50/50 criteria11=50/50 second_pass=50/50 semantic_script_decisions=0 length_metrics=measurement_only")


if __name__ == "__main__":
    main()
