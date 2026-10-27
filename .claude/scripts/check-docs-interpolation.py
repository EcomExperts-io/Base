#!/usr/bin/env python3
"""Pre-commit check: Liquid examples in docs must not be run as Vue expressions.

Usage: check-docs-interpolation.py
Only staged docs markdown is checked. Exit 1 if any file would break the build.

Notes:
- VitePress compiles every markdown file as a Vue template. It applies `v-pre`
  to fenced code blocks but NOT to inline code spans, so `{{ routes.cart_url }}`
  inside backticks is evaluated as a Vue expression and the build dies.
- Fix: `<code v-pre>escaped content</code>` renders identically — as an element,
  not inside backticks, where Markdown escapes the tag and Vue still evaluates.
"""

import os
import re
import subprocess
import sys

FENCE = re.compile(r"^\s*(```|~~~)")


def staged_docs():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [
        p for p in out.split("\n")
        if p.startswith("docs/") and p.endswith(".md") and ".vitepress" not in p
    ]


SPAN = re.compile(r"`[^`]+`")
VPRE = re.compile(r"<code v-pre>.*?</code>")


def offenders_in(content):
    """(line, text) for every line whose `{{` Vue would evaluate: outside a
    fenced block, and either inside a backtick span or outside a `<code v-pre>`."""
    found, in_fence = [], False
    for n, line in enumerate(content.split("\n"), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or "{{" not in line:
            continue
        spans = SPAN.findall(line)
        rest = VPRE.sub("", SPAN.sub("", line))
        if any("{{" in s for s in spans) or "{{" in rest:
            found.append((n, line.strip()))
    return found


def offenders(path):
    try:
        content = subprocess.run(
            ["git", "show", f":{path}"], capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError:
        return []
    return offenders_in(content)


def main():
    problems = {}
    for path in staged_docs():
        hits = offenders(path)
        if hits:
            problems[path] = hits

    if not problems:
        return 0

    total = sum(len(v) for v in problems.values())
    print()
    print("=" * 74)
    print(f"  COMMIT BLOCKED — {total} Liquid example(s) would break the docs build")
    print("=" * 74)
    print()
    print("  VitePress evaluates {{ }} in inline code spans as Vue expressions.")
    print("  Fenced code blocks are safe; inline spans are not.")
    print()
    for path, hits in problems.items():
        print(f"  {path}")
        for n, line in hits:
            print(f"    {n}: {line[:88]}")
        print()
    print("-" * 74)
    print("  Fix: replace `...{{ x }}...` with")
    print("       <code v-pre>...{{ x }}...</code>   (escape < and > as &lt; &gt;)")
    print()
    print("  Renders identically. Verify with: cd docs && npm run build")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
