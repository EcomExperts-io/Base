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

A locale file is also counted. Shopify rejects one with more than 3,400 keys
("Too many translation keys") and the failed upload takes every page of the
theme down; Theme Check, Prettier and a JSON parse all pass the file. Pique's
schema locale hit the cap exactly in Oct 2026 with 16 keys for one block, so
the warning starts 100 keys early.

Usage: check-json.py <paths...> [--quiet]
Exit 1 on a parse error or a locale over the cap. Warnings never fail.
"""

import json
import re
import sys

LOCALE_KEY_CAP = 3400
LOCALE_KEY_WARN = 3300


def strip_comments(raw):
    return re.sub(r"/\*.*?\*/", "", raw, flags=re.S)


def leaf_count(obj):
    if isinstance(obj, dict):
        return sum(leaf_count(v) for v in obj.values())
    return 1


def is_locale(path):
    return path.startswith("locales/") or "/locales/" in path.replace("\\", "/")


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
            data = json.loads(body)
        except json.JSONDecodeError as strict_err:
            # Python unbinds `strict_err` when the handler ends (PEP 3110), so
            # keep the one field the warning below needs while it is still in
            # scope. Reading it after the block raises UnboundLocalError, which
            # is what this check did on every file it was written to report.
            strict_lineno = strict_err.lineno
            try:
                data = json.loads(re.sub(r",(\s*[}\]])", r"\1", body))
                print(f"  warn   {path}:{strict_lineno} trailing comma — Shopify tolerates it, "
                      "strict JSON tools do not. Remove it.")
            except json.JSONDecodeError as e:
                print(f"  error  {path}:{e.lineno}:{e.colno} invalid JSON — {e.msg}")
                failed = True
                continue
        if is_locale(path):
            n = leaf_count(data)
            if n > LOCALE_KEY_CAP:
                print(f"  error  {path} holds {n} keys — Shopify rejects a locale file over "
                      f"{LOCALE_KEY_CAP} and every route 500s. Reuse labels.* keys or remove unused ones "
                      "(see .claude/rules/locales.md).")
                failed = True
            elif n > LOCALE_KEY_WARN:
                print(f"  warn   {path} holds {n} keys — within {LOCALE_KEY_CAP - n} of Shopify's "
                      f"{LOCALE_KEY_CAP}-key cap. Reuse before adding (see .claude/rules/locales.md).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
