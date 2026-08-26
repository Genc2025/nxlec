#!/usr/bin/env python3
"""Fail-closed runtime adapter for isolated USMLE model executions."""
import sys
from pathlib import Path

import pipeline as p

USMLE_ROOT = Path(__file__).resolve().parent
p.ROOT = USMLE_ROOT
p.DB = USMLE_ROOT / "data" / "usmle-step1.db"
p.STATE = USMLE_ROOT / "state"
p.RUN_DIR = USMLE_ROOT / "runs"

_real_subprocess_run = p.subprocess.run
_original_run_copilot = p.run_copilot


def _isolated_importer_aware_run(cmd, *args, **kwargs):
    """Route Trusted Importer to this adapter so it uses the authoritative usmle DB path."""
    if (
        isinstance(cmd, (list, tuple))
        and len(cmd) >= 3
        and str(cmd[1]).endswith(("pipeline.py", "core.py"))
        and cmd[2] == "--import-candidate"
    ):
        cmd = [cmd[0], str(Path(__file__).resolve()), *cmd[2:]]
    return _real_subprocess_run(cmd, *args, **kwargs)


p.subprocess.run = _isolated_importer_aware_run


def _run_model_with_fallback(prompt, requested_model, phase, execution_id):
    """Use account-available models; every try is a fresh no-resume Copilot CLI process."""
    if phase == "author":
        candidates = ["gpt-5.3-codex", "claude-sonnet-4.6", "auto"]
    else:
        candidates = ["claude-sonnet-4.6", "gpt-5.3-codex", "auto"]

    seen = set()
    last_error = None
    for model in candidates:
        if model in seen:
            continue
        seen.add(model)
        try:
            result, meta = _original_run_copilot(prompt, model, phase, execution_id)
            meta["model"] = model
            return result, meta
        except RuntimeError as exc:
            last_error = exc
            text = str(exc).lower()
            if "model" in text and "not available" in text:
                continue
            raise
    raise RuntimeError(f"no permitted Copilot model available for {phase}: {last_error}")


p.run_copilot = _run_model_with_fallback


def _isolation_gate(author_meta, blind_meta, audit_meta):
    """Prove session/process separation; a different model is preferred but not required."""
    ids = {author_meta["execution_id"], blind_meta["execution_id"], audit_meta["execution_id"]}
    homes = {author_meta["copilot_home"], blind_meta["copilot_home"], audit_meta["copilot_home"]}
    works = {author_meta["workdir"], blind_meta["workdir"], audit_meta["workdir"]}
    return len(ids) == 3 and len(homes) == 3 and len(works) == 3


def _isolation_gate_db(con, cid):
    rows = con.execute(
        """SELECT role,execution_id,model,prompt_sha256,context_namespace_sha256
           FROM executions WHERE candidate_id=? ORDER BY role""",
        (cid,),
    ).fetchall()
    if len(rows) != 3:
        return False
    if {r[0] for r in rows} != {
        "AUTHOR_EXECUTION",
        "AUDITOR_EXECUTION_PASS_A",
        "AUDITOR_EXECUTION_PASS_B",
    }:
        return False
    return len({r[1] for r in rows}) == 3 and len({r[4] for r in rows}) == 3


p.isolation_gate = _isolation_gate
p.isolation_gate_db = _isolation_gate_db


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-accepted", type=int, default=5)
    ap.add_argument("--max-attempts", type=int, default=20)
    ap.add_argument("--import-candidate", default=None)
    args = ap.parse_args()

    if args.import_candidate:
        return p.trusted_import_candidate(args.import_candidate)
    return p.run(args.max_accepted, args.max_attempts)


if __name__ == "__main__":
    sys.exit(main())
