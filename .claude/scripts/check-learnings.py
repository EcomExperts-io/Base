#!/usr/bin/env python3
"""Has every learning been answered, and does a change to an existing store rule or check say so?

Usage
-----
  check-learnings.py                       list the open learnings; never blocks
  check-learnings.py --brief               one line for the session context
  check-learnings.py --gate --range A..B   the pull-request gate: exit 1 on either finding below
  check-learnings.py --gate --staged       the same two findings on the index; the pre-commit prints them

Notes:
- Open: a file under docs/ai-workflow/incidents/ whose status is still `open` — recorded, and neither applied
  (`new-incident.py --apply`) nor declined (`--decline`). The developer answers every proposal, yes or no.
- Changes existing: a diff that rewrites or removes a line of a .claude/rules/this-store-*.md or a skill under
  .claude/skills/this-store-*/, or that removes a check or changes its pattern, files or severity in
  .claude/this-store/checks.json. Adding is free; changing what is there needs a learning in the same diff that
  carries `changes_existing:` (`--apply … --changes-existing "<why>"`), so a gate is never quietly loosened.
"""

import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_CHECKS = ".claude/this-store/checks.json"
STORE_TEXT = (".claude/rules/this-store-", ".claude/skills/this-store-")


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def open_learnings(inc):
    return [(path, fm) for path, fm in inc.incidents() if fm.get("status", "open") == "open"]


def changed_checks(old, new):
    """The ids of checks that were in `old` and are gone or different in `new`."""
    def by_id(raw):
        try:
            data = json.loads(raw) if raw else []
        except ValueError:
            return None
        return {str(e.get("id")): e for e in data if isinstance(e, dict)} if isinstance(data, list) else None
    before, after = by_id(old), by_id(new)
    if before is None:
        return []
    if after is None:
        return sorted(before)
    return sorted(cid for cid, e in before.items()
                  if cid not in after or any(e.get(k) != after[cid].get(k) for k in ("pattern", "files", "severity")))


def changes_existing(staged, a, b):
    """[(path, what)] for store rules, skills and checks whose existing content this diff rewrites or removes, and
    whether a learning in the same diff declares it."""
    if staged:
        names = git("diff", "--cached", "--name-status") or ""
        old_of = lambda p: git("show", f"HEAD:{p}")
        new_of = lambda p: git("show", f":{p}")
    else:
        names = git("diff", "--name-status", a, b) or ""
        old_of = lambda p: git("show", f"{a}:{p}")
        new_of = lambda p: git("show", f"{b}:{p}")
    found, declared = [], False
    for line in names.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[1]
        if status.startswith("A"):
            old = None
        else:
            old = old_of(path)
        new = None if status.startswith("D") else new_of(parts[-1])
        if path.startswith("docs/ai-workflow/incidents/") and new and "\nchanges_existing:" in new.split("\n---", 2)[0] + "\n":
            declared = True
        if old is None:
            continue
        if path == STORE_CHECKS:
            ids = changed_checks(old, new)
            if ids:
                found.append((path, "check(s) removed or changed: " + ", ".join(ids)))
        elif path.startswith(STORE_TEXT):
            kept = set((new or "").split("\n"))
            gone = [ln for ln in old.split("\n") if ln.strip() and ln not in kept]
            if gone:
                found.append((path, f"{len(gone)} existing line(s) rewritten or removed" if new is not None else "deleted"))
    return found, declared


def main(argv):
    root = (git("rev-parse", "--show-toplevel") or "").strip()
    if not root:
        return 0
    os.chdir(root)
    inc = load("new-incident")
    still_open = open_learnings(inc)

    if "--brief" in argv:
        total = len(inc.incidents())
        if not still_open:
            print(f"learnings: 0 open of {total} recorded")
        else:
            titles = "; ".join(fm.get("title", os.path.basename(path)) for path, fm in still_open[:5])
            more = f" (+{len(still_open) - 5} more)" if len(still_open) > 5 else ""
            print(f"learnings: {len(still_open)} open of {total} recorded, each waiting for a yes or a no — {titles}{more}")
        return 0

    if "--gate" not in argv:
        if not still_open:
            print("No open learnings.")
        for path, fm in still_open:
            print(f"  open  {path}\n        {fm.get('title', '')}")
        return 0

    staged = "--staged" in argv
    a = b = None
    if not staged:
        rng = argv[argv.index("--range") + 1] if "--range" in argv and argv.index("--range") + 1 < len(argv) else ""
        if ".." not in rng:
            print("usage: check-learnings.py --gate --range <base>..<head>   |   --gate --staged", file=sys.stderr)
            return 2
        a, b = rng.split("..", 1)
        a, b = a.strip("."), b.strip(".")
    touched, declared = changes_existing(staged, a, b)

    problems = 0
    if still_open:
        problems += len(still_open)
        print(f"  {len(still_open)} learning(s) recorded and not answered. Each one is applied or declined before the pull request:")
        for path, fm in still_open:
            print(f"    - {path} — {fm.get('title', '')}")
        print("    python3 .claude/scripts/new-incident.py --apply <file> --change <store file>   or   --decline <file> --reason \"…\"")
    if touched and not declared:
        problems += 1
        print("  This change rewrites or removes part of the store's existing rules or checks, and no learning says why:")
        for path, what in touched:
            print(f"    - {path} — {what}")
        print("    python3 .claude/scripts/new-incident.py --apply <file> --change <store file> --changes-existing \"<why>\"")
    if not problems:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
