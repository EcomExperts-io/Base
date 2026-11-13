#!/usr/bin/env python3
"""Has every learning been answered, and does a change to an existing store rule or check say so?

Usage
-----
  check-learnings.py                       list the open learnings; never blocks
  check-learnings.py --brief               one line for the session context
  check-learnings.py --gate --range A..B   the pull-request gate: exit 1 on either finding below
  check-learnings.py --gate --staged       the same two findings on the index; the pre-commit prints them
  check-learnings.py --signal <kind> "<what happened>"   note something a learning may come from (hooks and scripts call this)
  check-learnings.py --pending [--hold]    the unanswered signals; with --hold, exit 3 the first time each is shown
  check-learnings.py --dismiss "<why>"     answer the unanswered signals with a reason: nothing to learn

Notes:
- A signal is local to this machine (.claude/.cache/): a failed Shopify command, a blocked turn, a QA round, GitBot
  findings. It is answered by a learning recorded after it, or by --dismiss. The same signal is raised once.
- Open: a file under docs/ai-workflow/incidents/ whose status is still `open` — recorded, and neither applied
  (`new-incident.py --apply`) nor declined (`--decline`). The developer answers every proposal, yes or no.
- The gate also fails when the store has checks and this repo's conventions checker is too old to run them.
- The gate fails on an open learning this change records or edits. One that was open before the change is listed and
  does not fail it, so a backlog never blocks unrelated work.
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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_CHECKS = ".claude/this-store/checks.json"
STORE_TEXT = (".claude/rules/this-store-", ".claude/skills/this-store-")
SIGNALS = ".claude/.cache/learning-signals.json"
INCIDENTS = "docs/ai-workflow/incidents"


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


def load_signals():
    try:
        data = json.load(open(SIGNALS))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_signals(signals):
    os.makedirs(os.path.dirname(SIGNALS), exist_ok=True)
    json.dump(signals[-200:], open(SIGNALS, "w"), indent=1)


def newest_learning():
    """When the newest learning file was written; a learning recorded after a signal answers it."""
    try:
        files = [os.path.join(INCIDENTS, n) for n in os.listdir(INCIDENTS) if n.endswith(".md") and n != "README.md"]
    except OSError:
        return 0
    return max((os.stat(f).st_mtime for f in files), default=0)


def unanswered(signals):
    newest = newest_learning()
    changed = False
    for sig in signals:
        if not sig.get("answered") and newest >= sig.get("time", 0):
            sig["answered"] = "a learning was recorded"
            changed = True
    if changed:
        save_signals(signals)
    return [sig for sig in signals if not sig.get("answered")]


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


def checks_not_running():
    """A line to print when this repo has store checks and its conventions checker is a copy that cannot load them."""
    if not os.path.isfile(STORE_CHECKS):
        return ""
    try:
        checker = open(os.path.join(HERE, "check-conventions.py"), encoding="utf-8", errors="replace").read()
    except OSError:
        checker = ""
    if "load_store_checks" in checker:
        return ""
    return (f"store checks: {STORE_CHECKS} is NOT being run — this repo's .claude/scripts/check-conventions.py is an edited "
            "copy from before store checks. Take Base's version (a tooling pull saves it under .claude/.cache/base-new/).")


def in_change(staged, a, b):
    """The learning files this change adds or edits."""
    out = git("diff", "--cached", "--name-only", "--", INCIDENTS) if staged else git("diff", "--name-only", a, b, "--", INCIDENTS)
    return set((out or "").split())


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
    if "--signal" in argv:
        i = argv.index("--signal")
        kind = argv[i + 1] if i + 1 < len(argv) else ""
        what = " ".join((argv[i + 2] if i + 2 < len(argv) else "").split())[:300]
        if not kind or not what:
            print("usage: check-learnings.py --signal <kind> \"<what happened>\"", file=sys.stderr)
            return 2
        signals = load_signals()
        if not any(sig.get("kind") == kind and sig.get("what") == what for sig in signals):
            signals.append({"kind": kind, "what": what, "time": time.time()})
            save_signals(signals)
        return 0

    if "--dismiss" in argv:
        i = argv.index("--dismiss")
        why = (argv[i + 1] if i + 1 < len(argv) else "").strip()
        if not why:
            print("usage: check-learnings.py --dismiss \"<why there is nothing to learn>\"", file=sys.stderr)
            return 2
        signals = load_signals()
        waiting = unanswered(signals)
        for sig in waiting:
            sig["answered"] = "dismissed: " + why
        save_signals(signals)
        print(f"{len(waiting)} signal(s) dismissed.")
        return 0

    if "--pending" in argv:
        signals = load_signals()
        waiting = unanswered(signals)
        if not waiting:
            return 0
        fresh = [sig for sig in waiting if not sig.get("held")]
        print("learning loop: this happened and nothing has been learned from it yet:")
        for sig in waiting:
            print(f"  - [{sig.get('kind')}] {sig.get('what')}")
        print("If a rule, check or skill of this repo should have prevented it, run /record-incident and show the developer "
              "the proposed change. If there is nothing to learn, say why: "
              "python3 .claude/scripts/check-learnings.py --dismiss \"<why>\"")
        if "--hold" in argv and fresh:
            for sig in fresh:
                sig["held"] = True
            save_signals(signals)
            return 3
        return 0

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
        if checks_not_running():
            print(checks_not_running())
        waiting = unanswered(load_signals())
        if waiting:
            print(f"learning loop: {len(waiting)} thing(s) from an earlier session not yet learned from or dismissed — "
                  "python3 .claude/scripts/check-learnings.py --pending")
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
    if checks_not_running():
        problems += 1
        print("  " + checks_not_running())
    mine = in_change(staged, a, b)
    fresh = [(path, fm) for path, fm in still_open if path.replace(os.sep, "/") in mine]
    older = len(still_open) - len(fresh)
    if fresh:
        problems += len(fresh)
        print(f"  {len(fresh)} learning(s) recorded in this change and not answered. Each one is applied or declined before the pull request:")
        for path, fm in fresh:
            print(f"    - {path} — {fm.get('title', '')}")
        print("    python3 .claude/scripts/new-incident.py --apply <file> --change <store file>   or   --decline <file> --reason \"…\"")
    if older:
        print(f"  {older} older learning(s) still open, from before this change — listed, not blocking: python3 .claude/scripts/check-learnings.py")
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
