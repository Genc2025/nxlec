#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ORIGINAL_COMMIT = 'e16a1b5f4160a54f3bbfe730484b548ca8d37497'
SELF = 'tools/rule1_cleanup_2000.py'
REPORT = Path('RULE1_FULL_3525_DUPLICATE_SCAN.json')


def run(cmd, check=True):
    return subprocess.run(cmd, check=check)


def main():
    scan = subprocess.run([sys.executable, 'tools/scan_full_3525_duplicates.py'])

    # Always restore the normal cleanup runner in the same runner worktree.
    run(['git', 'checkout', ORIGINAL_COMMIT, '--', SELF])
    run(['git', 'config', 'user.name', 'OpenAI GitHub Connector'])
    run(['git', 'config', 'user.email', 'github-connector@openai.com'])
    run(['git', 'add', SELF])
    if REPORT.exists():
        run(['git', 'add', str(REPORT)])

    if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode != 0:
        run(['git', 'commit', '-m', 'RULE1 full 3525 duplicate scan report'])
        # Integrate any concurrent branch update before pushing.
        run(['git', 'pull', '--rebase', 'origin', 'rule1-cleanup-2000'])
        run(['git', 'push', 'origin', 'HEAD:rule1-cleanup-2000'])

    if scan.returncode != 0:
        raise SystemExit(scan.returncode)
    print('FULL_3525_DUPLICATE_SCAN_COMMITTED')


if __name__ == '__main__':
    main()
