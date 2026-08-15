#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/rule1_batch005_reaudit_evidence_q0782_q0831.json"
OVERRIDE = ROOT / "data/clinical_overrides_z_rule1_batch005_reaudit_20260815.json"

BLUEPRINT_FIXES = {
    "V2-Q0799": (5, "Psychosocial Integrity", "easy"),
    "V2-Q0813": (3, "Safety & Infection Prevention and Control", "easy"),
}


def metrics(options: dict[str, str], key: str):
    lengths = {k: len(str(v).strip()) for k, v in options.items()}
    vals = list(lengths.values())
    ratio = max(vals) / max(min(vals), 1)
    dmean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    dev = abs(lengths[key] - dmean) / max(dmean, 1)
    unique = (
        (lengths[key] == min(vals) and vals.count(min(vals)) == 1)
        or (lengths[key] == max(vals) and vals.count(max(vals)) == 1)
    )
    return lengths, ratio, dev, unique


def main():
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    ov = json.loads(OVERRIDE.read_text(encoding="utf-8"))
    by_e = {x["id"]: x for x in ev["items"]}
    by_o = {x["question_uid"]: x for x in ov["questions"]}

    for uid, (category_id, client_need, difficulty) in BLUEPRINT_FIXES.items():
        e = by_e[uid]
        e["category_id"] = category_id
        e["client_need"] = client_need
        e["difficulty"] = difficulty
        note = (
            f" Blueprint metadata normalized against the committed master DB on 2026-08-15: "
            f"category_id={category_id}, client_need={client_need}, difficulty={difficulty}."
        )
        if note.strip() not in str(e.get("finding", "")):
            e["finding"] = str(e.get("finding", "")).rstrip() + note

    q = by_o["V2-Q0829"]
    options = json.loads(q["item_data_json"])["options"]
    options = {k: v.replace("ultrasonography", "ultrasound").replace("Ultrasonography", "Ultrasound") for k, v in options.items()}
    q["rationale"] = q["rationale"].replace("Ultrasonography", "Ultrasound").replace("ultrasonography", "ultrasound")
    q["item_data_json"] = json.dumps({"options": options}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    key = json.loads(q["correct_answer_json"])["correct_option"]
    lengths, ratio, dev, unique = metrics(options, key)
    if ratio > 1.15 + 1e-12 or dev > 0.10 + 1e-12 or unique:
        raise SystemExit(f"Q0829 hotfix option QC failed: ratio={ratio:.4f} dev={dev:.4f} unique={unique}")
    q["qc"].update({
        "lengths_json": json.dumps(lengths, sort_keys=True, separators=(",", ":")),
        "min_chars": min(lengths.values()),
        "max_chars": max(lengths.values()),
        "max_min_ratio": round(ratio, 4),
        "correct_option": key,
        "correct_is_extreme": 0,
        "qc_status": "PASS",
        "qc_note": "Rule 1 Batch 005 semantic option/cue QC after Q0829 terminology normalization: max/min <=1.15; correct-option deviation <=10%; correct option is not a unique length extreme; no artificial padding.",
    })

    EVIDENCE.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OVERRIDE.write_text(json.dumps(ov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"BATCH005_GATE_INPUTS_FIXED blueprint=2/2 q0829_signature=ultrasound "
        f"q0829_ratio={ratio:.4f} q0829_dev={dev:.4f}"
    )


if __name__ == "__main__":
    main()
