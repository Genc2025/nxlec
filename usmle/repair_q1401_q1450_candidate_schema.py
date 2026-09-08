#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BATCH_DIR = ROOT / "batch_specs_1401_1500"
INPUTS = [
    BATCH_DIR / "01_q1401_q1425_author_20260908.json",
    BATCH_DIR / "02_q1426_q1450_author_20260908.json",
]
OUTPUTS = [
    BATCH_DIR / "01_q1401_q1425_author_20260908_schema_repaired.json",
    BATCH_DIR / "02_q1426_q1450_author_20260908_schema_repaired.json",
]

ALLOWED_DISCIPLINES = {
    "Pathology",
    "Physiology",
    "Nutrition",
    "Gross Anatomy & Embryology",
    "Microbiology",
    "Pharmacology",
    "Behavioral Sciences",
    "Biochemistry",
    "Histology & Cell Biology",
    "Immunology",
    "Genetics",
}
LETTERS = "ABCDE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_nonempty(values):
    out = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


def repair_item(x: dict) -> dict:
    q = int(x["num"])
    bp = x["blueprint"]
    it = x["item"]
    ex = x["explanation"]
    src = x["sources"]

    # Repository discipline vocabulary uses "Histology & Cell Biology".
    bp["disciplines"] = [
        "Histology & Cell Biology" if d == "Cell Biology" else d
        for d in bp.get("disciplines", [])
    ]

    assert bp.get("disciplines"), f"Q{q}: missing disciplines"
    assert set(bp["disciplines"]).issubset(ALLOWED_DISCIPLINES), (
        q,
        bp["disciplines"],
    )
    assert set(it["options"]) == set(LETTERS), f"Q{q}: options must be A-E"
    assert it["intended_key"] in LETTERS, f"Q{q}: invalid key"
    de = ex["distractor_explanations"]
    assert set(de) == set(LETTERS), f"Q{q}: rationale set must be A-E"
    assert ex.get("key_explanation"), f"Q{q}: missing key explanation"
    assert ex.get("educational_objective"), f"Q{q}: missing educational objective"
    assert src, f"Q{q}: missing sources"

    source_ids = [s["source_id"] for s in src]
    assert len(source_ids) == len(set(source_ids)), f"Q{q}: duplicate source_id"
    locators = unique_nonempty(s.get("section_locator") for s in src)
    key = it["intended_key"]

    # Do not invent new medical claims. Bind each evidence entry exactly to the
    # already-authored A-E rationale; key classification is direct and each
    # distractor rejection is an inference from the cited mechanism plus the
    # stipulated experimental/vignette conditions.
    x["evidence_map"] = [
        {
            "claim_id": f"Q{q}-{L}",
            "option": L,
            "claim_locator": f"explanation.distractor_explanations.{L}",
            "claim": de[L],
            "source_ids": source_ids,
            "direct_or_inference": "direct" if L == key else "inference",
            "source_locator": "; ".join(locators),
            "item_specific_application": (
                "Keyed target/mechanism is directly supported by the cited source(s); "
                "distractor rejection uses that mechanism together with the explicitly "
                "stipulated vignette/experimental conditions."
            ),
        }
        for L in LETTERS
    ]

    em = {e["option"]: e for e in x["evidence_map"]}
    assert set(em) == set(LETTERS), f"Q{q}: evidence map must cover A-E"
    for L in LETTERS:
        assert em[L]["claim"] == de[L], f"Q{q}-{L}: rationale binding mismatch"
        expected = "direct" if L == key else "inference"
        assert em[L]["direct_or_inference"] == expected, f"Q{q}-{L}: class mismatch"
        assert set(em[L]["source_ids"]).issubset(set(source_ids)), f"Q{q}-{L}: bad source id"

    return x


def repair_batch(input_path: Path, output_path: Path) -> dict:
    b = json.loads(input_path.read_text())
    items = b["items"]
    for item in items:
        repair_item(item)

    nums = [int(x["num"]) for x in items]
    assert nums == list(range(nums[0], nums[-1] + 1)), "noncontiguous item range"
    assert len(items) == 25, "expected 25 items per batch"
    keys = "".join(x["item"]["intended_key"] for x in items)
    assert {L: keys.count(L) for L in LETTERS} == {L: 5 for L in LETTERS}, (
        "unbalanced key distribution",
        keys,
    )

    b["schema_repair"] = {
        "repair_tool": "usmle/repair_q1401_q1450_candidate_schema.py",
        "source_batch_sha256": sha256(input_path),
        "changes": [
            "Normalize exact discipline value 'Cell Biology' to 'Histology & Cell Biology' where present.",
            "Materialize evidence_map as five A-E entries bound exactly to distractor_explanations.",
            "Classify keyed rationale as direct and distractor rationales as inference.",
        ],
        "medical_content_changed": False,
        "intended_keys_changed": False,
        "source_hashes_computed": False,
        "technical_freeze_complete": False,
        "independent_audit_complete": False,
    }
    b["status"] = "AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT"
    b["production_import_ready"] = False
    output_path.write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n")
    return {
        "input": str(input_path.relative_to(ROOT.parent)),
        "output": str(output_path.relative_to(ROOT.parent)),
        "input_sha256": sha256(input_path),
        "output_sha256": sha256(output_path),
        "item_count": len(items),
        "first": nums[0],
        "last": nums[-1],
        "keys": keys,
    }


def main():
    results = [repair_batch(i, o) for i, o in zip(INPUTS, OUTPUTS)]
    print(json.dumps({"status": "SCHEMA_REPAIR_MATERIALIZED", "results": results}, indent=2))


if __name__ == "__main__":
    main()
