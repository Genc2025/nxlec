#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
for i in range(532, 582):
    uid = f"V2-Q{i:04d}"
    q = con.execute("SELECT item_data_json, correct_answer_json FROM questions WHERE question_uid=?", (uid,)).fetchone()
    data = json.loads(q["item_data_json"])
    ans = json.loads(q["correct_answer_json"])
    opts = data["options"]
    key = ans["correct_option"]
    lengths = {k: len(str(opts[k]).strip()) for k in "ABCD"}
    mn, mx = min(lengths.values()), max(lengths.values())
    ratio = mx / max(mn, 1)
    min_count = sum(v == mn for v in lengths.values())
    max_count = sum(v == mx for v in lengths.values())
    unique_extreme = (lengths[key] == mn and min_count == 1) or (lengths[key] == mx and max_count == 1)
    dmean = sum(lengths[k] for k in "ABCD" if k != key) / 3
    dev = abs(lengths[key] - dmean) / max(dmean, 1)
    flag = ratio > 1.15 or unique_extreme or dev > 0.10
    print(f"{uid} key={key} lengths={lengths} ratio={ratio:.4f} key_dev={dev:.4f} unique_extreme={int(unique_extreme)} flag={int(flag)}")
con.close()
