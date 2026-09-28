#!/usr/bin/env python3
"""Run Theme Check, but only fail on offenses in files this change touches.

Why not just `shopify theme check`
----------------------------------
Theme Check has no per-file argument — it always scans the whole theme. Used
directly in a pre-commit hook that means a pre-existing error anywhere blocks
everyone, including the person trying to commit the fix. Reproduced: a bad
section arriving via merge blocked an unrelated docs-only commit.

So we run the whole-theme scan (unavoidable), take the JSON output, and only
fail on offenses in the files you name. You are accountable for what you touch,
not for what you inherited.

Warnings never block; only severity `error` does.

Two ways to name the files
--------------------------
  (default)        the staged set — the pre-commit hook
  --files <paths>  an explicit set — the Stop hook passes what changed this turn

Node
----
The Shopify CLI needs Node 22+ and dies at startup on older versions. On this
team's machines the default Node is often 20 with a newer one under ~/.nvm, so
when the PATH node is too old and nvm has one that works, that one is used for
this run. The skip is the dangerous outcome — a gate that silently did not run
looks exactly like a gate that passed — so the result always says which Node it
ran on, or why it could not.

Exit 0 = nothing to answer for. Exit 1 = an error in a file you named.
A Theme Check that cannot run at all is a skip, never a block, and says so.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {os.path.normpath(p) for p in out.split("\n") if p.strip()}


def node_env():
    """An environment whose PATH leads with a Node the Shopify CLI can run on."""
    env = dict(os.environ)
    try:
        v = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        major = int(re.match(r"v(\d+)", v).group(1))
    except (OSError, AttributeError, ValueError):
        v, major = "none", 0
    if major >= 22:
        return env, v
    cands = []
    for d in glob.glob(os.path.expanduser("~/.nvm/versions/node/v*")):
        m = re.match(r"v(\d+)\.(\d+)\.(\d+)", os.path.basename(d))
        if m and int(m.group(1)) >= 22:
            cands.append((tuple(int(x) for x in m.groups()), d))
    if cands:
        best = sorted(cands)[-1][1]
        env["PATH"] = os.path.join(best, "bin") + os.pathsep + env["PATH"]
        return env, f"{os.path.basename(best)} (from ~/.nvm; PATH node is {v})"
    return env, v


def main(argv):
    if shutil.which("shopify") is None:
        print("Theme Check did not run: the Shopify CLI is not installed. Not blocking.")
        return 0

    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    if "--files" in argv:
        targets = {os.path.normpath(p) for p in argv[argv.index("--files") + 1:] if not p.startswith("--")}
    else:
        targets = staged_files()
    targets = {p for p in targets if os.path.exists(os.path.join(root, p))}
    if not targets:
        return 0

    env, node_used = node_env()
    proc = subprocess.run(
        ["shopify", "theme", "check", "--output", "json"],
        capture_output=True, text=True, cwd=root, env=env,
    )

    # The CLI failing to start and the CLI reporting problems are different
    # things. Unparsable output means the former.
    try:
        results = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        print(f"Theme Check did not run (CLI or Node problem; node: {node_used}) — skipping, not blocking.")
        print("            The Shopify CLI needs Node 22+: nvm install 24 && nvm alias default 24")
        return 0

    blocking = []
    for entry in results:
        rel = os.path.normpath(os.path.relpath(entry.get("path", ""), root))
        if rel not in targets:
            continue
        for off in entry.get("offenses", []):
            if off.get("severity") == "error":
                blocking.append((rel, off))

    if not blocking:
        return 0

    print()
    print("=" * 74)
    print(f"  BLOCKED — Theme Check found {len(blocking)} error(s) in the files you changed")
    print("=" * 74)
    print(f"  (node: {node_used})")
    print()
    for rel, off in blocking:
        print(f"  {rel}:{off.get('start_row', '?')}")
        print(f"    [{off.get('check')}] {off.get('message')}")
        print()
    print("-" * 74)
    print("  Only the files you changed are checked — pre-existing offenses")
    print("  elsewhere in the theme do not block you.")
    print()
    print("  If a check is wrong for this theme, disable it in .theme-check.yml")
    print("  with a comment saying why.")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
