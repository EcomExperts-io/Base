#!/usr/bin/env python3
"""Stop hook — a turn cannot end with the mechanical gate failing.

Blocks (exit 2):  a new section missing the settings contract; a convention error in a NEW file; invalid JSON in
                  templates/locales/config; a Theme Check error in any file changed this session.
Blocks once:      something a learning may come from (a blocked turn, a failed Shopify command, a QA round, GitBot
                  findings) that has been neither learned from nor dismissed. Shown again as a report after that.
Reports (JSON):   convention warnings in modified files; a Theme Check that could not run or checked 0 files;
                  section or snippet work with no newer verify report; a client branch whose GitBot findings have not
                  been read since its last commit; learnings still open.

Notes:
- For the section contract, "new" means untracked or added since HEAD. For conventions, "new" means absent from the
  base branch (check-conventions.py decides). Modified legacy is reported, never gated.
- Claude Code lifts the refusal after eight consecutive blocks.
- Results are cached against the changed files' mtimes, so an unchanged turn costs one stat() per file, not a Theme Check run.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

THEME_DIRS = ("sections/", "snippets/", "assets/", "layout/", "templates/",
              "locales/", "config/", "blocks/")
CACHE = ".claude/.cache/stop-gate.json"


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def run(cmd, timeout=80):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 0, f"(skipped: {e})"


def changed():
    new = {p for p in git("ls-files", "--others", "--exclude-standard").split("\n") if p}
    mod = set()
    for line in git("diff", "--name-status", "HEAD").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        (new if parts[0].startswith("A") else mod).add(parts[-1])
    mod -= new
    keep = lambda s: {p for p in s if p.startswith(THEME_DIRS) and os.path.isfile(p)}
    return keep(new), keep(mod)


def cache_key(paths):
    h = hashlib.sha1()
    for p in sorted(paths):
        st = os.stat(p)
        h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}\n".encode())
    return h.hexdigest()


LEARNINGS = ".claude/scripts/check-learnings.py"
RULE_ID = re.compile(r"^\s+(?:error|warn)\s+:\d+\s+([a-z0-9:-]+)", re.M)


def learning_loop(py, advisory=""):
    """Exit code for the turn, after the mechanical gate has passed or had nothing to check: 2 the first time an
    unanswered signal is shown, 0 after that with the signals and the open learnings as a report."""
    if not os.path.isfile(LEARNINGS):
        if advisory:
            print(json.dumps({"systemMessage": advisory[:3000]}))
        return 0
    rc, pending = run([py, LEARNINGS, "--pending", "--hold"], timeout=20)
    if rc == 3:
        sys.stderr.write("Base stop gate — " + pending.strip()[:3000] + "\n")
        return 2
    _, brief = run([py, LEARNINGS, "--brief"], timeout=20)
    notes = [t.strip() for t in (pending, brief if "learnings: 0 open" not in brief else "") if t.strip()]
    parts = ([advisory] if advisory else []) + (["Base learning loop:\n" + "\n".join(notes)] if notes else [])
    if parts:
        print(json.dumps({"systemMessage": "\n\n".join(parts)[:4000]}))
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or git("rev-parse", "--show-toplevel").strip()
    if not root:
        return 0
    os.chdir(root)
    py = sys.executable

    new, mod = changed()
    every = new | mod
    if not every:
        return learning_loop(py)

    key = cache_key(every)
    try:
        cached = json.load(open(CACHE))
        if cached.get("key") == key and cached.get("result") == "pass":
            return learning_loop(py)
    except (OSError, json.JSONDecodeError):
        pass

    blockers, warnings = [], []

    new_sections = sorted(p for p in new if p.startswith("sections/") and p.endswith(".liquid"))
    if new_sections:
        rc, out = run([py, ".claude/scripts/check-section-contract.py", "--files", *new_sections, "--quiet"])
        if rc:
            blockers.append(out.strip())

    rc, out = run([py, ".claude/scripts/check-conventions.py", "--changed", "--block", "--quiet"])
    if rc:
        blockers.append(out.strip())
    elif out.strip():
        warnings.append(out.strip())

    json_files = sorted(p for p in every if p.endswith(".json")
                        and p.startswith(("templates/", "locales/", "config/")))
    if json_files:
        rc, out = run([py, ".claude/scripts/check-json.py", *json_files, "--quiet"])
        if rc:
            blockers.append(out.strip())
        elif out.strip():
            warnings.append(out.strip())

    liquid_json = sorted(p for p in every if p.endswith((".liquid", ".json")))
    if liquid_json:
        rc, out = run([py, ".claude/scripts/check-theme-staged.py", "--files", *liquid_json], timeout=120)
        if rc:
            blockers.append(out.strip())
        elif "did not run" in out or "checked 0 files" in out:
            warnings.append(out.strip())

    if any(p.startswith(("sections/", "snippets/")) and p.endswith(".liquid") for p in every):
        rc, out = run([py, ".claude/scripts/verify-status.py", "--changed"])
        if out.strip():
            warnings.append(out.strip())

    # Silent in Base and on a trunk branch.
    rc, out = run([py, ".claude/scripts/preflight-status.py", "--changed"])
    if out.strip():
        warnings.append(out.strip())

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump({"key": key, "result": "fail" if blockers else "pass"}, open(CACHE, "w"))

    if blockers:
        ids = sorted(set(RULE_ID.findall("\n".join(blockers))))
        if os.path.isfile(LEARNINGS):
            run([py, LEARNINGS, "--signal", "gate", "the stop gate blocked a turn on: " + (", ".join(ids) if ids else "a failing check")], timeout=20)
        sys.stderr.write(
            "Base stop gate: the turn cannot end while these fail. Fix them, then finish.\n"
            "(If a finding is wrong for this theme, tell the user which rule and why —\n"
            "do not work around it and do not disable hooks.)\n\n"
            + "\n\n".join(blockers)[:8000] + "\n"
        )
        return 2

    return learning_loop(py, "Base stop gate — advisory only:\n" + "\n\n".join(warnings)[:3000] if warnings else "")


if __name__ == "__main__":
    sys.exit(main())
