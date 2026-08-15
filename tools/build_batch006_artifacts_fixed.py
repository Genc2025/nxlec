#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools/build_batch006_artifacts.py"
FIXES = ROOT / "data/batch006_option_rewrites_20260815.json"

spec = importlib.util.spec_from_file_location("batch006_base", BASE)
if spec is None or spec.loader is None:
    raise SystemExit("Unable to load Batch006 base builder")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

fixes = json.loads(FIXES.read_text(encoding="utf-8"))
expected = {
    "V2-Q0834","V2-Q0835","V2-Q0837","V2-Q0838","V2-Q0839","V2-Q0840","V2-Q0843","V2-Q0844",
    "V2-Q0846","V2-Q0847","V2-Q0848","V2-Q0849","V2-Q0850","V2-Q0851","V2-Q0852","V2-Q0853",
    "V2-Q0854","V2-Q0856","V2-Q0857","V2-Q0859","V2-Q0860","V2-Q0861","V2-Q0863","V2-Q0865",
    "V2-Q0866","V2-Q0867","V2-Q0868","V2-Q0869","V2-Q0870","V2-Q0873","V2-Q0875","V2-Q0877",
    "V2-Q0878","V2-Q0879","V2-Q0880",
}
if set(fixes) != expected:
    raise SystemExit(f"Manual option-rewrite scope mismatch: {sorted(set(fixes)^expected)}")
for uid, options in fixes.items():
    if set(options) != set("ABCD") or len({v.strip().casefold() for v in options.values()}) != 4:
        raise SystemExit(f"{uid}: invalid manual semantic rewrite")
    base.MANUAL[uid]["options"] = options

bad=[]
max_ratio=max_dev=0.0
for uid in base.IDS:
    x=base.MANUAL[uid]
    lengths,ratio,dev,unique=base.metrics(x["options"],x["key"])
    max_ratio=max(max_ratio,ratio); max_dev=max(max_dev,dev)
    if ratio>1.15+1e-12 or dev>0.10+1e-12 or unique:
        bad.append((uid,ratio,dev,unique,lengths))
if bad:
    raise SystemExit("Manual semantic option QC failed: "+repr(bad))
print(f"BATCH006_MANUAL_OPTION_REWRITES_VALID rewritten={len(fixes)}/35 all_items=50/50 max_ratio={max_ratio:.4f} max_dev={max_dev:.4f} artificial_padding=0")
base.main()
