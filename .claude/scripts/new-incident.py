#!/usr/bin/env python3
"""Create, list and close learning files — what went wrong, and the change to this repo's own setup that answers it.

Usage
-----
  new-incident.py --slug t-key-in-template --title "…" --scope generic \
                  --surfaced-by theme-500 --should-have-caught .claude/rules/templates.md
  new-incident.py --list [--open]
  new-incident.py --apply <file> --change <path>[,<path>…] [--changes-existing "<why>"]
  new-incident.py --decline <file> --reason "<why nothing changes>"

Notes:
- --scope is generic | client: would this be true in a Shopify theme that is not this client's? Generic is a flag for
  whoever maintains Base; it sends nothing anywhere.
- --should-have-caught names the rule, check or skill that should have prevented it; it turns the list into a queue of gaps.
- --surfaced-by is one of theme-500, theme-check, gate, hook, review, qa, designer, eyeball, verify, ci, other.
- status is open | applied | declined. `harvested` and `client-only` are older closed statuses, still read.
- --apply is run after the developer approved the change: in a client repo every --change path must be in the store's
  own area (.claude/rules/this-store-*.md, .claude/this-store/, .claude/skills/this-store-*/), never a Base file.
- --changes-existing is required by check-learnings.py when the change rewrites or removes an existing store rule or check.
"""

import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pull_base_tooling_lib import is_store_owned  # noqa: E402

DIR = "docs/ai-workflow/incidents"
CLOSED = ("applied", "declined", "harvested", "client-only")
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

## Proposed change to this repo's setup

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


def is_base():
    return "EcomExperts-io/Base" in subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout


def set_fields(path, fields):
    """Set or add frontmatter fields, in order, keeping everything else in the file as it is."""
    text = open(path, encoding="utf-8").read()
    end = text.find("\n---", 3)
    head, rest = text[:end], text[end:]
    for key, value in fields.items():
        line = f"{key}: {value}"
        if re.search(rf"^{key}:.*$", head, flags=re.M):
            head = re.sub(rf"^{key}:.*$", lambda m: line, head, count=1, flags=re.M)
        else:
            head += "\n" + line
    open(path, "w", encoding="utf-8").write(head + rest)


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

    if "--apply" in argv:
        path = arg(argv, "--apply")
        changes = [c.strip() for c in (arg(argv, "--change") or "").split(",") if c.strip()]
        if not path or not os.path.isfile(path) or not changes:
            print("usage: --apply <file> --change <path>[,<path>…] [--changes-existing \"<why>\"]")
            return 2
        missing = [c for c in changes if not os.path.exists(c)]
        if missing:
            print(f"--change names a path that does not exist: {', '.join(missing)}")
            return 1
        if not is_base():
            outside = [c for c in changes if not is_store_owned(c)]
            if outside:
                print(f"not in the store's own area: {', '.join(outside)}\n"
                      "A learning in a client repo changes .claude/rules/this-store-*.md, .claude/this-store/checks.json or a\n"
                      ".claude/skills/this-store-*/ skill. A Base file edited here stops receiving Base's updates.")
                return 1
        who = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip() or "unknown"
        fields = {"status": "applied", "change": ", ".join(changes), "approved_by": json.dumps(who),
                  "applied": datetime.date.today().isoformat()}
        why = arg(argv, "--changes-existing")
        if why:
            fields["changes_existing"] = json.dumps(why)
        set_fields(path, fields)
        print(f"{path}: status -> applied ({', '.join(changes)})")
        return 0

    if "--decline" in argv:
        path = arg(argv, "--decline")
        reason = (arg(argv, "--reason") or "").strip()
        if not path or not os.path.isfile(path) or not reason:
            print("usage: --decline <file> --reason \"<why nothing changes>\"")
            return 2
        set_fields(path, {"status": "declined", "declined_reason": json.dumps(reason)})
        print(f"{path}: status -> declined")
        return 0

    if "--set-status" in argv:
        path = arg(argv, "--set-status")
        status = argv[argv.index("--set-status") + 2] if argv.index("--set-status") + 2 < len(argv) else None
        if not path or status not in ("open",) + CLOSED:
            print("usage: --set-status <file> open|" + "|".join(CLOSED) + " [--pr <url>]")
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
