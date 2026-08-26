#!/usr/bin/env python3
"""Run Theme Check, but only fail on offenses in files this commit touches.

Why not just `shopify theme check`
----------------------------------
Theme Check has no per-file argument — it always scans the whole theme. Used
directly in a pre-commit hook that means a pre-existing error anywhere blocks
everyone, including the person trying to commit the fix. Reproduced: a bad
section arriving via merge blocked an unrelated docs-only commit.

So we run the whole-theme scan (unavoidable), take the JSON output, and only
fail on offenses in staged files. You are accountable for what you touch, not
for what you inherited.

Warnings never block; only severity `error` does.

Exit 0 = nothing to answer for. Exit 1 = an error in a file you staged.
A Theme Check that cannot run at all is a skip, never a block: the Shopify CLI
needs a recent Node and dies on older ones, and an environment problem must not
stop a commit.
"""

import json
import os
import shutil
import subprocess
import sys


def staged_files(root):
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {os.path.normpath(p) for p in out.split("\n") if p.strip()}


def main():
    if shutil.which("shopify") is None:
        return 0

    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    staged = staged_files(root)
    if not staged:
        return 0

    proc = subprocess.run(
        ["shopify", "theme", "check", "--output", "json"],
        capture_output=True, text=True, cwd=root,
    )

    # The CLI failing to start and the CLI reporting problems are different
    # things. Unparsable output means the former.
    try:
        results = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        print("pre-commit: Theme Check did not run (CLI or Node problem) — skipping.")
        print("            Your Node may be too old for the Shopify CLI. Not blocking.")
        return 0

    blocking = []
    for entry in results:
        rel = os.path.normpath(os.path.relpath(entry.get("path", ""), root))
        if rel not in staged:
            continue
        for off in entry.get("offenses", []):
            if off.get("severity") == "error":
                blocking.append((rel, off))

    if not blocking:
        return 0

    print()
    print("=" * 74)
    print(f"  COMMIT BLOCKED — Theme Check found {len(blocking)} error(s) in staged files")
    print("=" * 74)
    print()
    for rel, off in blocking:
        print(f"  {rel}:{off.get('start_row', '?')}")
        print(f"    [{off.get('check')}] {off.get('message')}")
        print()
    print("-" * 74)
    print("  Only files in this commit are checked — pre-existing offenses")
    print("  elsewhere in the theme do not block you.")
    print()
    print("  If a check is wrong for this theme, disable it in .theme-check.yml")
    print("  with a comment saying why.")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
