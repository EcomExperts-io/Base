#!/usr/bin/env python3
"""How far has this repo's AI tooling drifted from Base — in both directions?

Why this exists
---------------
"After every store we have a new version of the workflow" — true, and the
problem: the learning happened after the build, by one person, as archaeology.
Nobody could list which rules a client build had edited, so nothing flowed up
until someone went digging. And nothing said how many Base improvements the
fork was missing, so nothing flowed down.

Both lists are one diff away once `.base-version` records the Base commit the
tooling was last aligned to. This prints them:

  HARVEST candidates   files this repo edited since the stamp and Base did not
                       — a local decision that is either a client measurement
                       (stays) or a generic trap (goes up, via /harvest)
  PULL-DOWN candidates files Base changed since the stamp and this repo did not
                       — run pull-base-tooling.py
  BOTH changed         needs a human merge; pull-base-tooling.py stashes Base's copy

The client-vs-generic guess is a heuristic on the added lines — pixel values,
file counts and container classes read as client-specific — and is labelled a
guess. The decision is the reader's; the list is the point.

Usage
-----
  python3 .claude/scripts/check-tooling-drift.py [--brief] [--json] [--ref base/development]
  python3 .claude/scripts/check-tooling-drift.py --base-path ../Base
  python3 .claude/scripts/check-tooling-drift.py --help
  --no-fetch  skip `git fetch base` (offline, or in CI where the remote is a checkout)

When the stamped commit is not on the ref being compared against — the fork
pulled its tooling from a Base feature branch that has not merged yet — every
file that branch touched shows as BOTH changed and nothing shows as HARVEST.
That is not drift; it is the branch not having landed. The report says so
instead of printing "distance unknown".
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pull_base_tooling_lib import Source, check_flags, is_tooling, load_stamp, sh  # noqa: E402

KNOWN_FLAGS = {"--brief": False, "--json": False, "--ref": True, "--base-path": True, "--no-fetch": False}
USAGE = __doc__.split("Usage\n-----\n", 1)[1]

CLIENT_HINT = re.compile(r"\b\d{2,4}px\b|\bfiles? against\b|\bcontainer\b|\bpage-width\b|\bthis (theme|client|store)\b", re.I)


def added_lines(old, new):
    old_lines = set((old or b"").decode("utf-8", "replace").split("\n"))
    return [ln for ln in (new or b"").decode("utf-8", "replace").split("\n") if ln.strip() and ln not in old_lines]


def classify(old, cur):
    lines = added_lines(old, cur)
    hits = sum(1 for ln in lines if CLIENT_HINT.search(ln))
    if not lines:
        return "edited"
    return "looks client-specific" if hits >= max(1, len(lines) // 4) else "looks generic"


def main(argv):
    rc = check_flags(argv, KNOWN_FLAGS, USAGE)
    if rc is not None:
        return rc
    root = sh("git", "rev-parse", "--show-toplevel").strip()
    os.chdir(root)
    brief = "--brief" in argv
    as_json = "--json" in argv

    if "EcomExperts-io/Base" in sh("git", "remote", "get-url", "origin", check=False):
        if not brief:
            print("This checkout is Base itself — drift is measured in the forks.")
        return 0

    stamp = load_stamp()
    if not stamp:
        msg = "tooling: no .base-version stamp — run sh .claude/scripts/base-link.sh then python3 .claude/scripts/pull-base-tooling.py"
        print(json.dumps({"error": msg}) if as_json else msg)
        return 0

    base_path = argv[argv.index("--base-path") + 1] if "--base-path" in argv else None
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "base/development"
    if not base_path:
        if sh("git", "remote", "get-url", "base", check=False).strip() == "":
            msg = "tooling: stamped but no `base` remote — sh .claude/scripts/base-link.sh"
            print(json.dumps({"error": msg}) if as_json else msg)
            return 0
        if "--no-fetch" not in argv:
            subprocess.run(["git", "fetch", "--quiet", "base"], check=False)

    try:
        source = Source(ref=ref, base_path=base_path)
    except RuntimeError as e:
        msg = f"tooling: cannot read Base ({e.args[0].splitlines()[0]})"
        print(json.dumps({"error": msg}) if as_json else msg)
        return 0
    old_sha = stamp.get("sha")

    paths = set(source.files())
    paths |= {p for p in sh("git", "ls-files").split("\n") if p and is_tooling(p)}
    try:
        old_files = sh("git", "ls-tree", "-r", "--name-only", old_sha, cwd=source.git_dir)
        paths |= {p for p in old_files.split("\n") if p and is_tooling(p)}
    except RuntimeError:
        pass
    try:
        # A count only means something when the stamp is an ancestor of the ref.
        # A stamp taken from an unmerged feature branch is reachable in the repo
        # but not on the ref, and `rev-list --count` would happily report a
        # number that is not a distance.
        sh("git", "merge-base", "--is-ancestor", old_sha, source.sha, cwd=source.git_dir)
        behind = int(sh("git", "rev-list", "--count", f"{old_sha}..{source.sha}", cwd=source.git_dir).strip())
    except RuntimeError:
        behind = None

    harvest, pull_down, both, fork_only = [], [], [], []
    for path in sorted(paths):
        if path == ".github/workflows/theme-review.yml":
            continue
        old = source.read(path, old_sha)
        new = source.read(path)
        cur = open(path, "rb").read() if os.path.exists(path) else None
        if cur is None:
            if new is not None and old != new:
                pull_down.append(path)
            continue
        if new is None and old is None:
            fork_only.append(path)
            continue
        fork_changed = cur != old
        base_changed = new != old
        if fork_changed and base_changed and cur != new:
            both.append((path, classify(old, cur)))
        elif fork_changed and cur != new:
            harvest.append((path, classify(old, cur)))
        elif base_changed and cur != new:
            pull_down.append(path)

    if as_json:
        print(json.dumps({"stamp": stamp, "base": source.sha, "commits_behind": behind,
                          "harvest": harvest, "pull_down": pull_down, "both": both, "fork_only": fork_only}, indent=2))
        return 0

    if behind is not None:
        behind_txt = f"{behind} Base commit(s) behind"
        behind_brief = behind_txt
    else:
        came_from = stamp.get("ref", "?")
        behind_brief = (f"stamp not on {source.ref} (pulled from {came_from}) — "
                        f"BOTH/HARVEST unreliable until that branch merges")
        behind_txt = (f"stamp {old_sha[:9]} is not on {source.ref}; .base-version says it came from "
                      f"{came_from}. Until that branch lands on {source.ref}, every file it touched "
                      f"reads as BOTH changed and nothing reads as HARVEST — that is the branch not "
                      f"having merged, not drift")
    if brief:
        print(f"tooling: stamped {old_sha[:9]} ({stamp.get('date', '?')}), {behind_brief}; "
              f"{len(harvest)} local edit(s) to harvest, {len(pull_down)} to pull down, {len(both)} need a merge"
              + (" — python3 .claude/scripts/check-tooling-drift.py" if (harvest or pull_down or both) else ""))
        return 0

    print()
    print(f"  Base tooling: this repo stamped at {old_sha[:9]} ({stamp.get('date', '?')}); "
          f"Base {source.ref} is {source.sha[:9]} — {behind_txt}")
    print("  " + "-" * 70)

    def block(title, items, note):
        print(f"  {title} ({len(items)}) — {note}")
        for it in items:
            if isinstance(it, tuple):
                print(f"      {it[0]:<52} {it[1]}")
            else:
                print(f"      {it}")
        print()

    block("HARVEST candidates", harvest, "edited here since the stamp, unchanged in Base. Client measurement stays; generic trap goes up via /harvest")
    block("PULL-DOWN candidates", pull_down, "changed in Base since the stamp, untouched here. python3 .claude/scripts/pull-base-tooling.py")
    block("BOTH changed", both, "needs a hand merge; pull-base-tooling.py saves Base's copy under .claude/.cache/base-new/")
    if fork_only:
        block("fork-only", fork_only, "exist here, never in Base at either commit")
    print("  " + "-" * 70)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
