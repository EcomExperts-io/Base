#!/usr/bin/env python3
"""Stop hook — a turn cannot end with the mechanical gate failing.

Why this exists
---------------
Claude stops when the work looks done. The pre-commit hook fires hours later,
if at all — every client fork runs husky, so Base's hook has never run on a
client machine — and `git commit --no-verify` is one keystroke. This runs the
same objective checks at the end of every turn that changed theme files, and
refuses to let the turn end while a new file fails them. Claude Code lifts the
refusal after eight consecutive blocks, so a check that is wrong cannot trap a
session forever; it can only make the disagreement visible.

What it gates, and what it only reports
----------------------------------------
Blocks (exit 2):  a new section missing the settings contract; a convention
                  error in a NEW file; invalid JSON in templates/locales/config;
                  a Theme Check error in any file changed this session.
Reports (JSON):   convention warnings in modified files; a Theme Check that
                  could not run; section or snippet work with no newer
                  verify-against-figma report.

"New" means untracked or added since HEAD. Modified legacy is never gated here
— see check-conventions.py for why.

Cost control: results are cached against the changed files' mtimes, so a turn
that changed nothing since the last pass costs one stat() per file, not a
Theme Check run.
"""

import hashlib
import json
import os
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


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or git("rev-parse", "--show-toplevel").strip()
    if not root:
        return 0
    os.chdir(root)

    new, mod = changed()
    every = new | mod
    if not every:
        return 0

    key = cache_key(every)
    try:
        cached = json.load(open(CACHE))
        if cached.get("key") == key and cached.get("result") == "pass":
            return 0
    except (OSError, json.JSONDecodeError):
        pass

    py = sys.executable
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
        elif "did not run" in out:
            warnings.append(out.strip())

    if any(p.startswith(("sections/", "snippets/")) and p.endswith(".liquid") for p in every):
        rc, out = run([py, ".claude/scripts/verify-status.py", "--changed"])
        if out.strip():
            warnings.append(out.strip())

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump({"key": key, "result": "fail" if blockers else "pass"}, open(CACHE, "w"))

    if blockers:
        sys.stderr.write(
            "Base stop gate: the turn cannot end while these fail. Fix them, then finish.\n"
            "(If a finding is wrong for this theme, tell the user which rule and why —\n"
            "do not work around it and do not disable hooks.)\n\n"
            + "\n\n".join(blockers)[:8000] + "\n"
        )
        return 2

    if warnings:
        print(json.dumps({"systemMessage": "Base stop gate — advisory only:\n" + "\n\n".join(warnings)[:3000]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
