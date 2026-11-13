#!/usr/bin/env python3
"""Run Theme Check, but only fail on offenses in files this change touches.

Usage:
  check-theme-staged.py                  the staged set — the pre-commit hook
  check-theme-staged.py --files <paths>  an explicit set — the Stop hook passes what changed this turn
Exit 0 = nothing to answer for. Exit 1 = an error in a file you named. A Theme Check that cannot run is a skip, and says so.
Every run prints one line with the number of files it checked. "checked 0 files" means nothing was checked.

Notes:
- Theme Check has no per-file argument, so the whole theme is scanned and only errors (never warnings) in the named files fail.
- A named file is counted as checked only when it is a .liquid or .json file that no `ignore` pattern in
  .theme-check.yml matches. Patterns are matched the way Theme Check matches them: a leading `/` anchors the pattern to
  the theme root; any other pattern matches at any depth of the absolute path, parent folders included.
- The Shopify CLI needs Node 22+ and dies at startup on older versions; when PATH's node is too old and ~/.nvm has one
  that works, that one is used, and the result always says which Node it ran on, or why it could not.
"""

import fnmatch
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


def offenses(results, root):
    """(repo-relative path, offense) pairs from either JSON shape the CLI emits:
    CLI 4 is a list of files each holding `offenses` (`start_row`); CLI 5 is a
    dict whose `issues` are flat (`filePath`, `startRow`)."""
    if isinstance(results, dict):
        for issue in results.get("issues", []):
            if isinstance(issue, dict):
                rel = os.path.normpath(os.path.relpath(issue.get("filePath", ""), root))
                yield rel, {**issue, "start_row": issue.get("startRow", issue.get("start_row", "?"))}
        return
    for entry in results:
        if not isinstance(entry, dict):
            continue
        rel = os.path.normpath(os.path.relpath(entry.get("path", ""), root))
        for off in entry.get("offenses", []):
            if isinstance(off, dict):
                yield rel, off


def ignore_patterns(root):
    """The `ignore:` list of .theme-check.yml, read without a YAML library."""
    try:
        text = open(os.path.join(root, ".theme-check.yml"), encoding="utf-8").read()
    except OSError:
        return []
    block = re.search(r"^ignore:[ \t]*\n((?:[ \t]+.*\n|[ \t]*\n)*)", text, re.M)
    if not block:
        return []
    return re.findall(r"^[ \t]+-[ \t]*['\"]?([^'\"#\n]+?)['\"]?[ \t]*$", block.group(1), re.M)


def is_ignored(rel, root, patterns):
    """True when Theme Check would skip this file because of an ignore pattern."""
    full = os.path.join(root, rel).replace(os.sep, "/")
    base = root.replace(os.sep, "/")
    for pat in patterns:
        pat = base + pat if pat.startswith("/") else "*/" + pat
        if fnmatch.fnmatchcase(full, pat.replace("**", "*")):
            return True
    return False


def main(argv):
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    if "--files" in argv:
        targets = {os.path.normpath(p) for p in argv[argv.index("--files") + 1:] if not p.startswith("--")}
    else:
        targets = staged_files()
    named = {p for p in targets if os.path.exists(os.path.join(root, p))}
    readable = {p for p in named if p.endswith((".liquid", ".json"))}
    patterns = ignore_patterns(root)
    ignored = {p for p in readable if is_ignored(p, root, patterns)}
    targets = readable - ignored
    if not targets:
        if ignored:
            print(f"Theme Check checked 0 files: all {len(ignored)} .liquid/.json file(s) named match an ignore "
                  "pattern in .theme-check.yml. Nothing was checked.")
        else:
            print(f"Theme Check checked 0 files: no .liquid or .json file among the {len(named)} file(s) named.")
        return 0

    if shutil.which("shopify") is None:
        print(f"Theme Check did not run on {len(targets)} file(s): the Shopify CLI is not installed. Not blocking.")
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

    blocking = [
        (rel, off) for rel, off in offenses(results, root)
        if rel in targets and off.get("severity") == "error"
    ]

    skipped = f", {len(ignored)} ignored by .theme-check.yml" if ignored else ""
    if not blocking:
        print(f"Theme Check checked {len(targets)} file(s){skipped}: 0 errors (node: {node_used}).")
        return 0

    print()
    print("=" * 74)
    print(f"  BLOCKED — Theme Check found {len(blocking)} error(s) in the files you changed")
    print("=" * 74)
    print(f"  ({len(targets)} file(s) checked{skipped}; node: {node_used})")
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
