#!/usr/bin/env python3
"""Create, list and update incident files — the record a rule is later made from.

Why this exists
---------------
The v1 workflow asked for a "mistake log" in every client repo, gitignored,
created only if the AI offered and a human said yes. Four client builds later
the count of logs was zero, while every incident that mattered had become a
Base rule anyway — by archaeology, weeks late, by one person. The record has
to be cheap to create at the moment of failure, committed so it is visible in
review and greppable across forks, and shaped so a script can list what is
still waiting to be harvested. That is what this writes.

Fields that matter for harvesting
---------------------------------
  scope               generic | client   — the CLAUDE.md test: would this be true
                      in a Shopify theme that is not this client's?
  should_have_caught  the rule, check or skill that should have prevented it —
                      the field that turns a list of incidents into a queue of
                      standards gaps
  status              open | harvested | client-only

Usage
-----
  new-incident.py --slug t-key-in-template --title "…" --scope generic \
                  --surfaced-by theme-500 --should-have-caught .claude/rules/templates.md
  new-incident.py --list [--open]
  new-incident.py --set-status docs/ai-workflow/incidents/<file>.md harvested --pr <url>

surfaced-by is one of: theme-500, theme-check, gate, hook, review, qa, designer,
eyeball, verify, ci, other.
"""

import datetime
import json
import os
import re
import subprocess
import sys

DIR = "docs/ai-workflow/incidents"
SURFACED = ("theme-500", "theme-check", "gate", "hook", "review", "qa", "designer",
            "eyeball", "verify", "ci", "other")

TEMPLATE = """---
title: {title_yaml}
date: {date}
repo: {repo}
scope: {scope}
surfaced_by: {surfaced_by}
should_have_caught: {should_have_caught}
status: open
---

# {title}

## What happened

## How it surfaced

## What fixed it

## Which rule or check should have caught it, and why it did not

"""


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def repo_name():
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
        return re.sub(r"\.git$", "", url.rstrip("/").split("/")[-1]) or "unknown"
    except OSError:
        return "unknown"


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


def incidents():
    if not os.path.isdir(DIR):
        return []
    rows = []
    for name in sorted(os.listdir(DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(DIR, name)
        fm = frontmatter(open(path, encoding="utf-8", errors="replace").read())
        if fm:
            rows.append((path, fm))
    return rows


def main(argv):
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if root:
        os.chdir(root)

    if "--list" in argv:
        rows = incidents()
        if "--open" in argv:
            rows = [r for r in rows if r[1].get("status", "open") == "open"]
        if not rows:
            print("no incidents" + (" open" if "--open" in argv else "") + f" in {DIR}/")
            return 0
        for path, fm in rows:
            print(f"  {fm.get('status', 'open'):<11} {fm.get('scope', '?'):<8} {path}")
            print(f"              {fm.get('title', '')}  — should have caught: {fm.get('should_have_caught', '?')}")
        return 0

    if "--set-status" in argv:
        path = arg(argv, "--set-status")
        status = argv[argv.index("--set-status") + 2] if argv.index("--set-status") + 2 < len(argv) else None
        if not path or status not in ("open", "harvested", "client-only"):
            print("usage: --set-status <file> open|harvested|client-only [--pr <url>]")
            return 2
        text = open(path, encoding="utf-8").read()
        text = re.sub(r"^status:.*$", f"status: {status}", text, count=1, flags=re.M)
        pr = arg(argv, "--pr")
        if pr and "harvested_pr:" not in text:
            text = text.replace("\n---\n", f"\nharvested_pr: {pr}\n---\n", 1)
        open(path, "w", encoding="utf-8").write(text)
        print(f"{path}: status -> {status}" + (f" ({pr})" if pr else ""))
        return 0

    slug = arg(argv, "--slug")
    title = arg(argv, "--title")
    scope = arg(argv, "--scope", "generic")
    surfaced = arg(argv, "--surfaced-by", "other")
    caught = arg(argv, "--should-have-caught", "unknown")
    if not slug or not title:
        print(__doc__)
        return 2
    if scope not in ("generic", "client"):
        print("scope must be generic or client")
        return 2
    if surfaced not in SURFACED:
        print(f"surfaced-by must be one of: {', '.join(SURFACED)}")
        return 2
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    date = arg(argv, "--date", datetime.date.today().isoformat())
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, f"{date}-{slug}.md")
    if os.path.exists(path):
        print(f"{path} already exists — edit it instead.")
        return 1
    open(path, "w", encoding="utf-8").write(TEMPLATE.format(
        title=title, title_yaml=json.dumps(title), date=date, repo=repo_name(), scope=scope,
        surfaced_by=surfaced, should_have_caught=caught))
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
