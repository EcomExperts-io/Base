#!/usr/bin/env python3
"""Validate the JSON files a theme ships — templates, locales, config.

Shopify's parser accepts two things strict JSON does not: `/* */` comment
blocks (every template starts with one) and trailing commas. Both are
tolerated here so that legitimate files pass, and a trailing comma is reported
as a warning because Prettier, `json.load` and most editors reject it —
`config/settings_schema.json` carried one for months without anyone noticing.

A file that does not parse even after those two allowances is an error: a
broken locale file renders key paths to the customer, and a broken template
404s the page.

Usage: check-json.py <paths...> [--quiet]
Exit 1 on a parse error. Warnings never fail.
"""

import json
import re
import sys


def strip_comments(raw):
    return re.sub(r"/\*.*?\*/", "", raw, flags=re.S)


def main(argv):
    quiet = "--quiet" in argv
    paths = [a for a in argv if not a.startswith("--") and a.endswith(".json")]
    failed = False
    for path in paths:
        try:
            raw = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"  {path}: cannot read — {e}")
            failed = True
            continue
        body = strip_comments(raw)
        try:
            json.loads(body)
            continue
        except json.JSONDecodeError as strict_err:
            # Python unbinds `strict_err` when the handler ends (PEP 3110), so
            # keep the one field the warning below needs while it is still in
            # scope. Reading it after the block raises UnboundLocalError, which
            # is what this check did on every file it was written to report.
            strict_lineno = strict_err.lineno
        try:
            json.loads(re.sub(r",(\s*[}\]])", r"\1", body))
            print(f"  warn   {path}:{strict_lineno} trailing comma — Shopify tolerates it, "
                  "strict JSON tools do not. Remove it.")
        except json.JSONDecodeError as e:
            print(f"  error  {path}:{e.lineno}:{e.colno} invalid JSON — {e.msg}")
            failed = True
    if not failed and not quiet and paths:
        pass
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
