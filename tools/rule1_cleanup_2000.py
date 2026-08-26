#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

OUTPUT = Path('NCLEX_FULL_3525_RULE1_1125.db')
REPORT = Path('RULE1_FULL_3525_REPORT.json')


def run(cmd):
    subprocess.check_call(cmd)


def main():
    # This is a temporary runner entry point only. It does not modify NCLEX_CANONICAL.db
    # or NCLEX_COMMERCIAL_MASTER_CURRENT.db. The builder copies the source DB to OUTPUT.
    OUTPUT.unlink(missing_ok=True)
    REPORT.unlink(missing_ok=True)

    run([sys.executable, 'tools/rule1_legacy_review_gate_compat.py'])
    run([
        sys.executable, 'tools/build_rule1_reviewed_snapshot.py',
        '--expected-reviewed', '1125',
        '--output', str(OUTPUT),
        '--report', str(REPORT),
    ])

    run(['git', 'config', 'user.name', 'OpenAI GitHub Connector'])
    run(['git', 'config', 'user.email', 'github-connector@openai.com'])
    run(['git', 'add', str(OUTPUT), str(REPORT)])
    staged = subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode != 0
    if staged:
        run(['git', 'commit', '-m', 'RULE1 full 3525 source with audited overlay'])
        run(['git', 'push', 'origin', 'HEAD:rule1-cleanup-2000'])
    print('FULL_3525_BUILD_COMMITTED')


if __name__ == '__main__':
    main()
