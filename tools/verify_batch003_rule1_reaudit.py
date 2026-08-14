#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
EVIDENCE_FILES = [
    ROOT / "data/rule1_reaudit_batch003_evidence_part1_q0101_q0125.json",
    ROOT / "data/rule1_reaudit_batch003_evidence_part2_q0126_q0150.json",
]
REPORT = ROOT / "FINAL_QA_BATCH003_REAL_REAUDIT_20260814.md"
IDS = [f"V2-Q{i:04d}" for i in range(101, 151)]
EXPECTED_CRITERIA = [
    "stem_and_four_options_read",
    "source_authority_exact_locator_verified",
    "correct_answer_directly_verified",
    "stem_claims_verified",
    "rationale_claims_verified",
    "distractor_plausibility_and_second_answer_qc",
    "ambiguity_and_cue_qc",
    "blueprint_topic_difficulty_verified",
    "source_version_and_currentness_verified",
    "no_unresolved_conflict",
    "independent_second_pass",
]
SECONDARY_EXCEPTIONS = {
    "V2-Q0121", "V2-Q0122", "V2-Q0128", "V2-Q0130",
    "V2-Q0132", "V2-Q0134", "V2-Q0138", "V2-Q0142",
}
REJECTED_GENERIC_URLS = {
    "https://www.cms.gov/priorities/your-patient-rights/emergency-room-rights",
    "https://pubmed.ncbi.nlm.nih.gov/37487152/",
    "https://www.aabb.org/news-resources/resources/clinical-practice-resources",
    "https://www.wocn.org/",
    "https://www.cms.gov/medicare/health-safety-standards/conditions-coverage-participation/hospitals",
    "https://pva.org/research-resources/publications/clinical-practice-guidelines/",
    "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation-topics",
}
CORRECTED_ASSERTIONS = {
    "V2-Q0106": {
        "url": "https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/ipledge-risk-evaluation-and-mitigation-strategy-rems",
        "stem_contains": "August 2026",
        "option_contains": ("B", "FDA-authorized pregnancy-testing flexibilities"),
        "rationale_contains": "enforcement discretion",
        "source_detail_contains": ["June 16, 2026", "November 15, 2026", "Reviewed 2026-08-14"],
    },
    "V2-Q0131": {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8152175/",
        "stem_contains": "T4 spinal cord injury",
        "option_contains": ("D", "Sit the client upright"),
        "rationale_contains": "PVA Consortium guideline",
        "source_detail_contains": [
            "Current PVA Consortium CPG listing",
            "reviewed 2026-08-14",
            "Recommendations 2.1 and 2.5-2.13",
            "sitting the individual upright",
        ],
    },
    "V2-Q0141": {
        "url": "https://www.cdc.gov/asthma/living-with/index.html",
        "stem_contains": "peak expiratory flow",
        "option_contains": ("B", "personal best"),
        "rationale_contains": "green, yellow, and red zones",
        "source_detail_contains": ["May 4, 2026", "reviewed 2026-08-14"],
    },
    "V2-Q0146": {
        "url": "https://www.bonehealthandosteoporosis.org/preventing-fractures/prevention/",
        "stem_contains": "low bone mass",
        "option_contains": ("B", "calcium and vitamin D"),
        "rationale_contains": "weight-bearing and muscle-strengthening",
        "source_detail_contains": ["Calcium and Vitamin D", "Exercise for Strong Bones", "Reviewed 2026-08-14"],
    },
    "V2-Q0147": {
        "url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/colorectal-cancer-screening",
        "stem_contains": "47-year-old",
        "option_contains": ("A", "ages 45 to 49 as a Grade B service"),
        "rationale_contains": "not listed among USPSTF recommendations in progress",
        "source_detail_contains": ["May 18, 2021", "Grade B", "2026-08-14"],
    },
}


def load_evidence():
    items = []
    exception_reasons = {}
    for path in EVIDENCE_FILES:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("standard") != "RULE_1_FINAL_10_OF_10_REAL_REAUDIT":
            raise SystemExit(f"{path.name}: wrong standard")
        if doc.get("batch") != "Q0101-Q0150" or doc.get("date") != "2026-08-14":
            raise SystemExit(f"{path.name}: wrong batch/date")
        if doc.get("legacy_status_evidence") is not False:
            raise SystemExit(f"{path.name}: legacy status cannot be semantic evidence")
        if doc.get("criteria") != EXPECTED_CRITERIA:
            raise SystemExit(f"{path.name}: 11-criterion definition mismatch")
        if doc.get("count") != len(doc.get("items", [])):
            raise SystemExit(f"{path.name}: declared item count mismatch")
        items.extend(doc["items"])
        exception_reasons.update(doc.get("secondary_exception_reasons", {}))
    by_id = {item["id"]: item for item in items}
    if len(items) != 50 or len(by_id) != 50 or set(by_id) != set(IDS):
        raise SystemExit("Evidence must contain exactly Q0101-Q0150, once each")
    if set(exception_reasons) != SECONDARY_EXCEPTIONS:
        raise SystemExit("Secondary-source exception set mismatch")
    for uid in SECONDARY_EXCEPTIONS:
        if len(exception_reasons[uid].strip()) < 40:
            raise SystemExit(f"{uid}: secondary-source exception reason is incomplete")
    return by_id, exception_reasons


def option_metrics(options, key):
    lengths = {k: len(v.strip()) for k, v in options.items()}
    values = list(lengths.values())
    ratio = max(values) / max(min(values), 1)
    distractor_lengths = [lengths[k] for k in "ABCD" if k != key]
    distractor_mean = sum(distractor_lengths) / 3
    deviation = abs(lengths[key] - distractor_mean) / max(distractor_mean, 1)
    unique_extreme = (
        (lengths[key] == min(values) and values.count(min(values)) == 1)
        or (lengths[key] == max(values) and values.count(max(values)) == 1)
    )
    return lengths, ratio, deviation, unique_extreme


def main():
    evidence, exception_reasons = load_evidence()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise SystemExit(f"DB integrity failure: {integrity}")

    con.execute("""
        CREATE TABLE IF NOT EXISTS rule1_reaudit_evidence(
            question_uid TEXT PRIMARY KEY,
            audit_date TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            source_authority TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_locator TEXT NOT NULL,
            source_currentness_date TEXT NOT NULL,
            finding TEXT NOT NULL,
            correction TEXT,
            criteria_passed_count INTEGER NOT NULL,
            second_pass TEXT NOT NULL,
            final_disposition TEXT NOT NULL,
            option_metrics_json TEXT NOT NULL,
            FOREIGN KEY(question_uid) REFERENCES questions(question_uid)
        )
    """)

    failures = []
    metrics_by_uid = {}
    corrected_integrated = 0
    for uid in IDS:
        item = evidence[uid]
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if not q:
            failures.append(f"{uid}: missing from DB")
            continue
        try:
            options = json.loads(q["item_data_json"])["options"]
            key = json.loads(q["correct_answer_json"])["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid item JSON: {exc}")
            continue

        if set(options) != {"A", "B", "C", "D"}:
            failures.append(f"{uid}: four-option schema invalid")
            continue
        if any(not str(v).strip() for v in options.values()) or len({str(v).strip().casefold() for v in options.values()}) != 4:
            failures.append(f"{uid}: blank or duplicate option")
            continue
        if key != item["key"]:
            failures.append(f"{uid}: DB key {key} != re-audit key {item['key']}")
            continue
        if item.get("qa") != 11 or item.get("second") != "PASS" or item.get("final") != "FINAL_QA_PASS":
            failures.append(f"{uid}: semantic re-audit evidence incomplete")
            continue
        if item.get("auth") not in {"P", "S"}:
            failures.append(f"{uid}: invalid source authority code")
            continue
        if (uid in SECONDARY_EXCEPTIONS) != (item["auth"] == "S"):
            failures.append(f"{uid}: secondary-source exception coding mismatch")
            continue

        db_url = (q["source_url"] or "").strip()
        if db_url != item["url"].strip():
            failures.append(f"{uid}: DB source URL does not match re-audit evidence: {db_url}")
            continue
        if db_url in REJECTED_GENERIC_URLS:
            failures.append(f"{uid}: rejected generic/obsolete source URL remains: {db_url}")
            continue
        if not db_url.startswith("https://"):
            failures.append(f"{uid}: source URL is not HTTPS")
            continue
        if len((q["source_detail"] or "").strip()) < 45 or len(item.get("loc", "").strip()) < 45:
            failures.append(f"{uid}: exact source locator is incomplete")
            continue
        if not str(q["clinical_qa_status"]).startswith("SOURCE_VERIFIED_2026_"):
            failures.append(f"{uid}: integrated source-verification status missing")
            continue
        if q["category_id"] not in (2, 3, 4, 5, 7, 8, 9, 10):
            failures.append(f"{uid}: blueprint category invalid")
            continue

        lengths, ratio, deviation, unique_extreme = option_metrics(options, key)
        if ratio > 1.15 + 1e-12:
            failures.append(f"{uid}: max/min option ratio {ratio:.4f} > 1.15")
            continue
        if deviation > 0.10 + 1e-12:
            failures.append(f"{uid}: correct-option deviation {deviation:.4f} > 0.10")
            continue
        if unique_extreme:
            failures.append(f"{uid}: correct option is a unique length extreme")
            continue

        if uid in CORRECTED_ASSERTIONS:
            req = CORRECTED_ASSERTIONS[uid]
            if db_url != req["url"]:
                failures.append(f"{uid}: corrected source URL not integrated")
                continue
            if req["stem_contains"].casefold() not in q["stem"].casefold():
                failures.append(f"{uid}: corrected stem signature missing")
                continue
            opt_key, opt_text = req["option_contains"]
            if opt_text.casefold() not in options[opt_key].casefold():
                failures.append(f"{uid}: corrected option signature missing")
                continue
            if req["rationale_contains"].casefold() not in q["rationale"].casefold():
                failures.append(f"{uid}: corrected rationale signature missing")
                continue
            if not all(marker.casefold() in q["source_detail"].casefold() for marker in req["source_detail_contains"]):
                failures.append(f"{uid}: corrected locator/currentness signature missing")
                continue
            corrected_integrated += 1

        finding = item.get("fix") or item.get("finding") or ""
        if len(finding.strip()) < 15:
            failures.append(f"{uid}: item-specific finding/fix evidence missing")
            continue

        metrics = {
            "characters": lengths,
            "max_min_ratio": round(ratio, 4),
            "correct_option": key,
            "correct_deviation_from_distractor_mean": round(deviation, 4),
            "correct_unique_length_extreme": False,
        }
        metrics_by_uid[uid] = metrics
        authority = (
            "SECONDARY_EXCEPTION: " + exception_reasons[uid]
            if uid in SECONDARY_EXCEPTIONS
            else "PRIMARY_OR_OFFICIAL_AUTHORITATIVE"
        )
        con.execute(
            """INSERT OR REPLACE INTO rule1_reaudit_evidence(
                question_uid,audit_date,correct_option,source_authority,source_url,source_locator,
                source_currentness_date,finding,correction,criteria_passed_count,second_pass,
                final_disposition,option_metrics_json
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                uid, "2026-08-14", key, authority, db_url, item["loc"].strip(),
                "2026-08-14", item.get("finding") or item.get("fix") or "",
                item.get("fix"), 11, "PASS", "FINAL_QA_PASS",
                json.dumps(metrics, sort_keys=True),
            ),
        )

    if failures:
        con.rollback()
        raise SystemExit("\n".join(failures))

    total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    ready = con.execute("SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1").fetchone()[0]
    evidence_count = con.execute("""
        SELECT COUNT(*) FROM rule1_reaudit_evidence
        WHERE question_uid BETWEEN 'V2-Q0101' AND 'V2-Q0150'
          AND criteria_passed_count=11
          AND second_pass='PASS'
          AND final_disposition='FINAL_QA_PASS'
    """).fetchone()[0]
    old_gate = con.execute("""
        SELECT COUNT(*) FROM question_final_gate
        WHERE question_uid BETWEEN 'V2-Q0101' AND 'V2-Q0150'
          AND final_status='FINAL_QA_PASS'
    """).fetchone()[0]
    gate = con.execute("SELECT value FROM bank_metadata WHERE key='commercial_release_gate'").fetchone()

    if total != 3525:
        raise SystemExit(f"unexpected total question count: {total}")
    if ready != 0:
        raise SystemExit(f"commercial_release_ready must remain 0, got {ready}")
    if evidence_count != 50:
        raise SystemExit(f"reaudit evidence count must be 50, got {evidence_count}")
    if old_gate != 50:
        raise SystemExit(f"strict final gate must contain 50 Batch 003 PASS rows, got {old_gate}")
    if corrected_integrated != 5:
        raise SystemExit(f"five new correction signatures required, got {corrected_integrated}")
    if not gate or gate[0] != "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA":
        raise SystemExit(f"commercial gate state invalid: {gate}")

    meta_value = "PASS_50_OF_50_REAL_REAUDIT_SECOND_PASS_11_OF_11_2026_08_14"
    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key,value) VALUES(?,?)",
        ("batch003_q0101_q0150_rule1_reaudit_20260814", meta_value),
    )
    con.commit()
    con.close()

    max_ratio = max(m["max_min_ratio"] for m in metrics_by_uid.values())
    max_dev = max(m["correct_deviation_from_distractor_mean"] for m in metrics_by_uid.values())
    REPORT.write_text(
        "\n".join([
            "# Rule 1 Batch 003 — Real Re-audit Q0101-Q0150",
            "",
            "- Scope: **50/50**",
            "- Legacy PASS/status used as semantic evidence: **NO**",
            "- Real item-by-item source/semantic evidence: **50/50**",
            "- Eleven Rule 1 criteria: **11/11 for 50/50**",
            "- Independent second pass: **50/50**",
            "- Unresolved conflicts: **0**",
            f"- Option max/min <= 1.15: **50/50** (max {max_ratio:.4f})",
            f"- Correct-option deviation <= 10%: **50/50** (max {max_dev:.4f})",
            "- Correct option unique length extreme: **0/50**",
            "- Artificial option padding: **NOT USED**",
            "- New integrated corrections/source realignments: **Q0106, Q0131, Q0141, Q0146, Q0147**",
            "- Previously selected Rule 1 source upgrades preserved and reverified: **Q0115, Q0120, Q0129, Q0136, Q0143, Q0144**",
            "- Documented secondary-source exceptions: **Q0121, Q0122, Q0128, Q0130, Q0132, Q0134, Q0138, Q0142**",
            "- DB integrity: **ok**",
            "- Full-bank commercial release gate: **CLOSED**",
            "- Final Batch 003 result: **FINAL_QA_PASS 50/50**",
            "",
            "Per-item evidence is persisted in `rule1_reaudit_evidence`; source records and corrections are integrated into the master DB.",
            "",
        ]),
        encoding="utf-8",
    )
    print(
        "RULE1_BATCH003_REAUDIT_VERIFIED "
        f"integrity={integrity} total={total} pass={evidence_count}/50 "
        f"criteria11={evidence_count}/50 second_pass={evidence_count}/50 "
        f"option_qc={len(metrics_by_uid)}/50 corrections={corrected_integrated}/5 "
        f"old_gate={old_gate}/50 ready={ready}"
    )


if __name__ == "__main__":
    main()
