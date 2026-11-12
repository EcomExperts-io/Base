#!/usr/bin/env python3
"""What the stores learned that would be true in any Shopify theme — read from every store repo, run from Base.

Usage
-----
  learnings-report.py                     the generic learnings not yet decided, from every repo in the organisation
  learnings-report.py --all               every generic learning, decided or not
  learnings-report.py --path <dir>        read local checkouts under <dir> instead of GitHub
  learnings-report.py --org <name>        another organisation (default: the one Base's origin belongs to)
  learnings-report.py --mark <repo>/<file> taken|skipped     record the decision, so the item stops being listed

Notes:
- Reads only: one `gh` code search for docs/ai-workflow/incidents/*.md across the organisation, then each file found,
  one at a time. Code search covers default branches and can trail a merge by a few minutes.
  A learning is listed when its `scope` is `generic`; nothing in a store repo is changed and nothing is sent to Base.
- Runs from Base only, and is not part of the tooling a store pulls (BASE_ONLY in pull_base_tooling_lib.py).
- The decisions live in .claude/.cache/, outside git, so no store's name enters Base.
- What becomes a Base rule is written by hand, in Base, in the rule's own voice and without the store's numbers.
"""

import json
import os
import re
import subprocess
import sys

DIR = "docs/ai-workflow/incidents"
LEDGER = ".claude/.cache/learnings-report.json"
SECTIONS = ("What happened", "Which rule or check should have caught it, and why it did not",
            "Proposed change to this repo's setup")
KNOWN_FLAGS = {"--all": 0, "--path": 1, "--org": 1, "--mark": 2}


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return " ".join(m.group(1).split()) if m else ""


def local_repos(parent):
    """(repo name, [(file name, text)]) for each checkout under `parent` that has learnings."""
    for name in sorted(os.listdir(parent)):
        d = os.path.join(parent, name, DIR)
        if not os.path.isdir(os.path.join(parent, name, ".git")):
            continue
        files = []
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".md") and f != "README.md":
                files.append((f, open(os.path.join(d, f), encoding="utf-8", errors="replace").read()))
        yield name, files


def remote_repos(org):
    """One code search for every learning file in the organisation, then one read per file found."""
    rc, out = run("gh", "search", "code", "--owner", org, f"path:{DIR}", "--limit", "1000",
                  "--json", "repository,path")
    if rc != 0:
        raise RuntimeError(f"`gh search code --owner {org}` failed — is gh installed and signed in? (gh auth status)")
    found = {}
    for hit in json.loads(out or "[]"):
        full = (hit.get("repository") or {}).get("nameWithOwner", "")
        path = hit.get("path", "")
        name = full.split("/")[-1]
        if (not full or name == "Base" or not path.startswith(DIR + "/") or not path.endswith(".md")
                or path.endswith("/README.md")):
            continue
        found.setdefault(full, set()).add(path)
    for full in sorted(found):
        files = []
        for path in sorted(found[full]):
            rc, text = run("gh", "api", f"repos/{full}/contents/{path}", "-H", "Accept: application/vnd.github.raw")
            if rc == 0:
                files.append((os.path.basename(path), text))
        yield full.split("/")[-1], files


def load_ledger():
    try:
        d = json.load(open(LEDGER))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def main(argv):
    i = 0
    while i < len(argv):
        if argv[i] in ("-h", "--help") or argv[i] not in KNOWN_FLAGS:
            print(__doc__.strip())
            return 0 if argv[i] in ("-h", "--help") else 2
        i += 1 + KNOWN_FLAGS[argv[i]]
    rc, root = run("git", "rev-parse", "--show-toplevel")
    if rc == 0 and root.strip():
        os.chdir(root.strip())
    origin = run("git", "remote", "get-url", "origin")[1].strip()
    if "/Base" not in origin and ":Base" not in origin:
        print("This report runs from Base. In a store repo the learnings are its own: python3 .claude/scripts/check-learnings.py")
        return 1
    ledger = load_ledger()

    if "--mark" in argv:
        k = argv.index("--mark")
        key = argv[k + 1] if k + 1 < len(argv) else ""
        decision = argv[k + 2] if k + 2 < len(argv) else ""
        if "/" not in key or decision not in ("taken", "skipped"):
            print("usage: learnings-report.py --mark <repo>/<file> taken|skipped")
            return 2
        ledger[key] = decision
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        json.dump(ledger, open(LEDGER, "w"), indent=1, sort_keys=True)
        print(f"{key}: {decision}")
        return 0

    path = argv[argv.index("--path") + 1] if "--path" in argv else None
    m = re.search(r"[:/]([^/:]+)/Base(?:\.git)?$", origin)
    org = argv[argv.index("--org") + 1] if "--org" in argv else (m.group(1) if m else "")
    try:
        repos = list(local_repos(path) if path else remote_repos(org))
    except RuntimeError as e:
        print(f"learnings-report: {e}")
        return 1

    shown = decided = with_learnings = 0
    for repo, files in repos:
        with_learnings += 1 if files else 0
        for name, text in files:
            fm = frontmatter(text)
            if fm.get("scope") != "generic":
                continue
            key = f"{repo}/{name}"
            if key in ledger:
                decided += 1
                if "--all" not in argv:
                    continue
            shown += 1
            print(f"\n  {key}" + (f"   [{ledger[key]}]" if key in ledger else ""))
            print(f"    {fm.get('title', '')}")
            print(f"    {fm.get('date', '?')} · status {fm.get('status', 'open')} · surfaced by {fm.get('surfaced_by', '?')}"
                  f" · should have caught: {fm.get('should_have_caught', '?')}")
            if fm.get("change"):
                print(f"    the store changed: {fm['change']}")
            for heading in SECTIONS:
                body = section(text, heading)
                if body:
                    print(f"    {heading}: {body[:600]}")
    print(f"\n  {len(repos)} repo(s) read, {with_learnings} with learnings; {shown} generic learning(s) listed"
          + (f", {decided} already decided" + ("" if "--all" in argv else " (--all shows them)") if decided else "") + ".")
    if shown:
        print("  Decide each one:  python3 .claude/scripts/learnings-report.py --mark <repo>/<file> taken|skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
