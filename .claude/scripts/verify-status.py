#!/usr/bin/env python3
"""Has the section or snippet work in this change been verified against its design?

verify-against-figma writes `.claude/verify/<slug>/report.json` when it runs.
This compares the newest such report against the newest change to a section or
snippet and says, in one paragraph, whether the evidence is current. It never
blocks: a bug fix or a refactor legitimately has no frame to verify against,
and only the person in the session knows which kind of change this was.

Usage: verify-status.py --changed | --files <paths...>
Prints nothing when the evidence is current or nothing relevant changed.
"""

import glob
import json
import os
import subprocess
import sys


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed_ui_files():
    paths = set(p for p in git("ls-files", "--others", "--exclude-standard").split("\n") if p)
    paths |= set(p for p in git("diff", "--name-only", "HEAD").split("\n") if p)
    return sorted(p for p in paths if p.startswith(("sections/", "snippets/"))
                  and p.endswith(".liquid") and os.path.isfile(p))


def main(argv):
    root = git("rev-parse", "--show-toplevel").strip()
    if root:
        os.chdir(root)
    if "--files" in argv:
        files = [p for p in argv[argv.index("--files") + 1:] if not p.startswith("--") and os.path.isfile(p)]
    else:
        files = changed_ui_files()
    if not files:
        return 0

    newest_change = max(os.stat(p).st_mtime for p in files)
    reports = glob.glob(".claude/verify/*/report.json")
    current = []
    for r in reports:
        if os.stat(r).st_mtime >= newest_change:
            try:
                d = json.load(open(r))
                widths = ", ".join(f"{f.get('width')}px {f.get('diff_pct', '?')}%" for f in d.get("frames", []))
                current.append(f"{d.get('slug', os.path.basename(os.path.dirname(r)))} ({widths})")
            except (OSError, json.JSONDecodeError):
                current.append(os.path.dirname(r))
    if current:
        return 0

    print(f"verify: {len(files)} section/snippet file(s) changed since the last verify-against-figma "
          f"report ({len(reports)} report(s) on disk). If this work came from a Figma frame, run "
          "/verify-against-figma before reporting it done — a report is the evidence, not the "
          "assertion. If it did not (a fix, a refactor), ignore this line.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
