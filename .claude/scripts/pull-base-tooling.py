#!/usr/bin/env python3
"""Overlay Base's AI tooling onto a client repo — three-way, never clobbering.

Why this exists
---------------
Every client theme copies Base's `.claude/` on day one and drifts from that
moment. CLAUDE.md asserted "14 of the 16 rules are byte-identical between Base
and the BPN fork"; measured on 14 Sep 2026 the number was 6, because Base had
moved and there was no way to pull it down. A fork's rule copies also carry
things Base must not overwrite — the measured breakpoint, the container class,
the client's own decisions — so a plain copy is as wrong as no copy.

This does what a merge would do for the tooling files only, with no shared
history required. For each file Base ships:

    fork missing it                 -> ADD
    fork == Base                    -> unchanged
    fork untouched since stamp      -> UPDATE  (Base changed, fork did not)
    fork edited, Base unchanged     -> KEEP    (a local decision; harvest candidate)
    fork edited AND Base changed    -> KEEP, save Base's copy under .claude/.cache/base-new/
    no stamp and fork differs       -> KEEP, same as above (provenance unknown)

"Since stamp" means since the Base commit recorded in `.base-version` by the
previous run. The first run on a fork that already has tooling therefore keeps
everything that differs and lists it — nothing the previous team decided is
lost, and you get the list of what they decided. `--force` overwrites.

Files the fork holds under the tooling paths that Base does not ship are left
alone and listed as fork-only.

What counts as tooling
----------------------
See pull_base_tooling_lib.py: .claude/** (except per-machine state),
.githooks/**, .mcp.json, .theme-check.yml, CLAUDE.md, docs/ai-workflow/**,
docs/base-theme-standards/**. Incidents are excluded — they belong to the repo
that recorded them. The CI workflow is special: a fork gets the six-line
CALLER that uses Base's reusable workflow, never a copy of the steps.

.cursor/ is not copied; it is regenerated from .claude/ afterwards.

Usage
-----
  python3 .claude/scripts/pull-base-tooling.py [--ref base/development] [--dry-run] [--force]
  python3 .claude/scripts/pull-base-tooling.py --base-path ../Base     # a local Base checkout
  python3 .claude/scripts/pull-base-tooling.py --stamp-only            # fresh fork: record the version

Run `sh .claude/scripts/base-link.sh` first if there is no `base` remote.
"""

import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pull_base_tooling_lib import STAMP, Source, is_tooling, load_stamp, sh  # noqa: E402

STASH_DIR = ".claude/.cache/base-new"
CALLER_TEMPLATE = ".claude/templates/fork-theme-review.yml"
CI_PATH = ".github/workflows/theme-review.yml"


def read_local(path):
    try:
        return open(path, "rb").read()
    except OSError:
        return None


def write_stamp(source):
    with open(STAMP, "w") as f:
        json.dump({
            "sha": source.sha,
            "ref": source.ref,
            "date": datetime.date.today().isoformat(),
            "tool": "pull-base-tooling.py",
            "note": "Base commit this repo's AI tooling was last aligned to. Read by check-tooling-drift.py and doctor.py.",
        }, f, indent=2)
        f.write("\n")


def main(argv):
    root = sh("git", "rev-parse", "--show-toplevel").strip()
    os.chdir(root)
    if "EcomExperts-io/Base" in sh("git", "remote", "get-url", "origin", check=False):
        print("This checkout is Base itself — there is nothing to pull.")
        return 0

    dry = "--dry-run" in argv
    force = "--force" in argv
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "base/development"
    base_path = argv[argv.index("--base-path") + 1] if "--base-path" in argv else None

    if not base_path:
        if sh("git", "remote", "get-url", "base", check=False).strip() == "":
            print("No `base` remote. Run:  sh .claude/scripts/base-link.sh")
            return 1
        subprocess.run(["git", "fetch", "--quiet", "base"], check=False)

    source = Source(ref=ref, base_path=base_path)
    stamp = load_stamp()
    old_sha = stamp.get("sha") if stamp else None
    if old_sha and source.read("CLAUDE.md", old_sha) is None:
        print(f"note: stamped Base commit {old_sha[:9]} is not reachable from here; treating as no stamp.")
        old_sha = None

    if "--stamp-only" in argv:
        if not dry:
            write_stamp(source)
        print(f"Stamped {STAMP} at Base {source.sha[:9]}.")
        return 0

    added, updated, kept, conflicts, unchanged = [], [], [], [], []
    for path in source.files():
        new = source.read(path)
        if new is None:
            continue
        if path == CI_PATH:
            # Forks get the caller, not the steps — the logic must live in one place.
            new = source.read(CALLER_TEMPLATE) or new
        cur = read_local(path)
        old = source.read(path, old_sha) if old_sha else None

        if cur is None:
            added.append(path)
            action = "write"
        elif cur == new:
            unchanged.append(path)
            action = None
        elif old is not None and cur == old:
            updated.append(path)
            action = "write"
        elif old is not None and new == old:
            kept.append(path)
            action = None
        else:
            conflicts.append(path)
            action = "write" if force else "stash"

        if dry or action is None:
            continue
        if action == "write":
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "wb") as f:
                f.write(new)
            if path.endswith((".sh", "pre-commit", ".py")):
                os.chmod(path, 0o755)
        else:
            dest = os.path.join(STASH_DIR, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(new)

    base_set = set(source.files())
    fork_only = [p for p in sh("git", "ls-files").split("\n")
                 if p and is_tooling(p) and p not in base_set]

    if not dry:
        write_stamp(source)
        if os.path.exists(".claude/scripts/sync-ai-config.sh"):
            subprocess.run(["sh", ".claude/scripts/sync-ai-config.sh"], capture_output=True)

    verb = "would " if dry else ""
    saved = "would be saved" if dry else "saved"
    print()
    print(f"  Base tooling {source.ref} @ {source.sha[:9]}"
          + (f"  (previous stamp {old_sha[:9]})" if old_sha else "  (no previous stamp)"))
    print("  " + "-" * 70)

    def block(title, items, note=""):
        if not items:
            return
        print(f"  {title} ({len(items)}){' — ' + note if note else ''}")
        for p in items:
            print(f"      {p}")

    block(f"{verb}ADD", added)
    block(f"{verb}UPDATE", updated, "Base changed, this repo had not touched them")
    block("KEEP — local edits", kept, "this repo edited them, Base did not: harvest candidates")
    block("KEEP — both changed" if old_sha else "KEEP — differs, provenance unknown", conflicts,
          f"Base's copy {saved} under {STASH_DIR}/ to merge by hand; --force overwrites")
    block("fork-only", fork_only, "present here, absent in Base — left alone")
    print(f"  unchanged: {len(unchanged)}")
    print("  " + "-" * 70)
    if dry:
        print("  dry run — nothing written.")
    else:
        print(f"  stamped {STAMP}; .cursor/ regenerated.")
        print("  next:  sh .claude/scripts/setup.sh     then     python3 .claude/scripts/check-tooling-drift.py")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        print(f"pull-base-tooling: {e}")
        sys.exit(1)
