#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
PATCHES = [
    ROOT / "data" / "manual_option_balance_wave26a_0532_0556.json",
    ROOT / "data" / "manual_option_balance_wave26b_0557_0581.json",
]
EXPECTED = [f"V2-Q{i:04d}" for i in range(532, 582)]
MAX_RATIO = 1.15
MAX_KEY_DEVIATION = 0.10


def fail(msg: str) -> None:
    raise SystemExit(msg)


def metrics(options: dict[str, str], key: str) -> dict:
    lengths = {k: len(str(options[k]).strip()) for k in "ABCD"}
    mn = min(lengths.values())
    mx = max(lengths.values())
    ratio = mx / max(mn, 1)
    distractor_mean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    key_deviation = abs(lengths[key] - distractor_mean) / max(distractor_mean, 1)
    sorted_keys = sorted(lengths, key=lambda k: (lengths[k], k))
    return {
        "lengths": lengths,
        "min_chars": mn,
        "max_chars": mx,
        "max_min_ratio": round(ratio, 4),
        "correct_option": key,
        "correct_length_rank": sorted_keys.index(key) + 1,
        "correct_is_extreme": int(lengths[key] in (mn, mx)),
        "correct_vs_distractor_mean_deviation": round(key_deviation, 4),
        "strict_pass": ratio <= MAX_RATIO and key_deviation <= MAX_KEY_DEVIATION,
    }


def main() -> None:
    if not DB.exists():
        fail("Master database missing")
    patch_items = []
    for path in PATCHES:
        if not path.exists():
            fail(f"Missing manual option patch: {path.name}")
        doc = json.loads(path.read_text(encoding="utf-8"))
        patch_items.extend(doc.get("items", []))

    ids = [x.get("question_uid") for x in patch_items]
    if ids != EXPECTED:
        fail(f"Wave26 option patch scope mismatch: expected 50 ordered IDs, got {len(ids)}")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    failures: list[str] = []
    ratios: list[float] = []
    deviations: list[float] = []

    for patch in patch_items:
        uid = patch["question_uid"]
        q = con.execute("SELECT * FROM questions WHERE question_uid=?", (uid,)).fetchone()
        if not q:
            failures.append(f"{uid}: missing question")
            continue
        try:
            old_data = json.loads(q["item_data_json"])
            answer = json.loads(q["correct_answer_json"])
            key = answer["correct_option"]
        except Exception as exc:
            failures.append(f"{uid}: invalid existing JSON: {exc}")
            continue

        options = patch.get("options")
        if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"}:
            failures.append(f"{uid}: option patch must contain exactly A-D")
            continue
        if key not in options:
            failures.append(f"{uid}: key {key} missing from option patch")
            continue
        normalized = [str(options[k]).strip().casefold() for k in "ABCD"]
        if any(not x for x in normalized) or len(set(normalized)) != 4:
            failures.append(f"{uid}: blank or duplicate option")
            continue

        m = metrics(options, key)
        ratios.append(m["max_min_ratio"])
        deviations.append(m["correct_vs_distractor_mean_deviation"])
        if not m["strict_pass"]:
            failures.append(
                f"{uid}: strict option QC failed ratio={m['max_min_ratio']:.4f} "
                f"key_dev={m['correct_vs_distractor_mean_deviation']:.4f}"
            )
            continue

        new_data = dict(old_data)
        new_data["options"] = options
        flags = json.loads(q["editorial_flags_json"] or "[]")
        for flag in ("MANUAL_OPTION_CUE_REVIEW", "STRICT_OPTION_LENGTH_QC_PASS"):
            if flag not in flags:
                flags.append(flag)

        con.execute(
            "UPDATE questions SET item_data_json=?, editorial_flags_json=? WHERE question_uid=?",
            (json.dumps(new_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
             json.dumps(flags, ensure_ascii=False, sort_keys=True, separators=(",", ":")), uid),
        )
        con.execute(
            """INSERT OR REPLACE INTO option_length_qc(
                question_uid,lengths_json,min_chars,max_chars,max_min_ratio,correct_option,
                correct_length_rank,correct_is_extreme,qc_status,qc_note
            ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                uid,
                json.dumps(m["lengths"], sort_keys=True),
                m["min_chars"],
                m["max_chars"],
                m["max_min_ratio"],
                key,
                m["correct_length_rank"],
                m["correct_is_extreme"],
                "PASS",
                f"Manual option/cue review; max/min <= {MAX_RATIO:.2f}; correct-option length deviation from distractor mean <= {MAX_KEY_DEVIATION:.2f}. Metrics support, but do not replace, semantic distractor review.",
            ),
        )
        con.execute(
            """INSERT INTO clinical_audit_log(
                question_uid,source_id,audit_date,audit_version,old_stem,old_options_json,
                old_correct_answer_json,old_rationale,new_stem,new_options_json,new_correct_answer_json,
                new_rationale,source_name,source_url,source_detail,findings_json,reviewer
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                uid,
                q["source_id"],
                datetime.now(timezone.utc).isoformat(),
                "2026-08-14-wave26-manual-option-balance-v1",
                q["stem"],
                q["item_data_json"],
                q["correct_answer_json"],
                q["rationale"],
                q["stem"],
                json.dumps(new_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                q["correct_answer_json"],
                q["rationale"],
                q["source_name"],
                q["source_url"],
                q["source_detail"],
                json.dumps({"manual_option_balance": True, "metrics": m}, sort_keys=True),
                "OpenAI manual item-by-item option/cue QA",
            ),
        )

    if failures:
        con.rollback()
        fail("\n".join(failures))

    count = con.execute(
        """SELECT COUNT(*) FROM option_length_qc
           WHERE question_uid BETWEEN 'V2-Q0532' AND 'V2-Q0581' AND qc_status='PASS'"""
    ).fetchone()[0]
    if count != 50:
        con.rollback()
        fail(f"Expected 50 Wave26 strict option QC PASS rows, got {count}")

    con.commit()
    con.close()
    print(
        f"Wave26 manual option balance: PASS 50/50; max_ratio={max(ratios):.4f}; "
        f"max_key_deviation={max(deviations):.4f}"
    )


if __name__ == "__main__":
    main()
