#!/usr/bin/env python3
"""Pre-commit check: Liquid examples in docs must not be run as Vue expressions.

The docs site is VitePress, which compiles every markdown file as a Vue
template. It applies `v-pre` to fenced code blocks automatically but NOT to
inline code spans — so `{{ routes.cart_url }}` inside backticks is evaluated as
a Vue expression, finds nothing, and the build dies.

This is worth a check rather than a rule because of how it was found: the docs
build had been broken since June 2026 and nobody knew, since the deploy workflow
only runs on pushes that touch docs/** and nothing had. Then the branch adding
this very check introduced three more instances of the same fault — two of them
in prose written specifically to document the standard. A convention nobody can
reliably follow by hand belongs in a script.

Fix: `<code v-pre>escaped content</code>` — renders identically, Vue leaves it
alone.

Only staged docs markdown is checked. Exit 1 if any file would break the build.
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


def offenders(path):
    """Lines containing {{ outside a fenced block and not already v-pre'd."""
    try:
        content = subprocess.run(
            ["git", "show", f":{path}"], capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError:
        return []

    found, in_fence = [], False
    for n, line in enumerate(content.split("\n"), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "{{" in line and "v-pre" not in line:
            found.append((n, line.strip()))
    return found


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
