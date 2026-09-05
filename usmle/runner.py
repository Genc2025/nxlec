#!/usr/bin/env python3
"""Minimal isolated runtime for the USMLE production pipeline."""
import os
import sys
import tempfile
from pathlib import Path

import pipeline as p

USMLE_ROOT = Path(__file__).resolve().parent
p.ROOT = USMLE_ROOT
p.DB = USMLE_ROOT / "data" / "usmle-step1.db"
p.STATE = USMLE_ROOT / "state"
p.RUN_DIR = USMLE_ROOT / "runs"

_real_run = p.subprocess.run


def _route_importer(cmd, *args, **kwargs):
    if (
        isinstance(cmd, (list, tuple))
        and len(cmd) >= 3
        and str(cmd[1]).endswith("pipeline.py")
        and cmd[2] == "--import-candidate"
    ):
        cmd = [cmd[0], str(Path(__file__).resolve()), *cmd[2:]]
    return _real_run(cmd, *args, **kwargs)


p.subprocess.run = _route_importer


def _fresh_execution(prompt, requested_model, phase, execution_id):
    """Every Author/Auditor pass is a brand-new Copilot process and context."""
    if p.model_family(requested_model) is None:
        raise ValueError("Explicit supported model required; automatic routing is not auditable")
    home = Path(tempfile.mkdtemp(prefix=f"copilot-{phase}-"))
    work = Path(tempfile.mkdtemp(prefix=f"work-{phase}-"))
    env = os.environ.copy()
    env["COPILOT_HOME"] = str(home)
    env["COPILOT_AUTO_UPDATE"] = "false"

    cmd = [
        "copilot", "-p", prompt, "-s", "--no-ask-user",
        "--model", requested_model,
        "--available-tools=web_search,web_fetch",
        "--allow-tool=web_search", "--allow-tool=web_fetch",
        "--disable-builtin-mcps", "-C", str(work),
    ]
    for url in p.URL_ALLOW_ARGS:
        cmd += ["--allow-url", url]

    proc = _real_run(cmd, env=env, text=True, capture_output=True, timeout=1200)
    if proc.returncode != 0:
        raise RuntimeError(f"{phase} execution failed rc={proc.returncode}: {proc.stderr[-2000:]}")

    return p.extract_json(proc.stdout), {
        "execution_id": execution_id,
        "model": requested_model,
        "copilot_home": str(home),
        "workdir": str(work),
        "prompt_sha256": p.sha_text(prompt),
        "completed_at": p.now(),
    }


p.run_copilot = _fresh_execution


# Use the canonical gates; local wrappers must not weaken family separation.
_isolation_gate = p.isolation_gate
_isolation_gate_db = p.isolation_gate_db


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-accepted", type=int, default=5)
    ap.add_argument("--max-attempts", type=int, default=10)
    ap.add_argument("--import-candidate", default=None)
    args = ap.parse_args()

    if args.import_candidate:
        return p.trusted_import_candidate(args.import_candidate)
    return p.run(args.max_accepted, args.max_attempts)


if __name__ == "__main__":
    sys.exit(main())
