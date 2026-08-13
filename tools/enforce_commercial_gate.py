#!/usr/bin/env python3
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT.db"
REPORT = ROOT / "NCLEX_COMMERCIAL_MASTER_CURRENT_AUDIT.md"
GATE_STATUS = "CLOSED_PENDING_FULL_BANK_CLINICAL_CURRENTNESS_SOURCE_LICENSING_AND_RELEASE_QA"


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"Missing master database: {DB.name}")
    if not REPORT.exists():
        raise SystemExit(f"Missing master audit report: {REPORT.name}")

    con = sqlite3.connect(DB)
    con.execute("UPDATE questions SET commercial_release_ready=0")
    con.execute(
        "INSERT OR REPLACE INTO bank_metadata(key, value) VALUES(?, ?)",
        ("commercial_release_gate", GATE_STATUS),
    )
    con.commit()

    ready = con.execute(
        "SELECT COUNT(*) FROM questions WHERE commercial_release_ready=1"
    ).fetchone()[0]
    con.close()

    if ready != 0:
        raise SystemExit(f"Commercial hard gate failed: ready={ready}")

    report = REPORT.read_text(encoding="utf-8")
    report = re.sub(
        r"- Current commercial-gate-ready items: \*\*\d+\*\*",
        "- Current commercial-gate-ready items: **0**",
        report,
    )
    gate_line = (
        "- Commercial release hard gate: **CLOSED** — pending full-bank clinical "
        "verification/currentness, source/licensing review, and release QA."
    )
    if gate_line not in report:
        marker = "- Current commercial-gate-ready items: **0**"
        report = report.replace(marker, f"{marker}\n{gate_line}")
    REPORT.write_text(report, encoding="utf-8")

    print(f"Commercial release hard gate enforced: ready={ready}, status={GATE_STATUS}")


if __name__ == "__main__":
    main()
