#!/usr/bin/env python3
"""Pre-commit check: structural invariants of the AI configuration itself.

Why this exists
---------------
The rules are the thing that keeps every client theme consistent, and until this
script there was nothing checking the rules. Three failures made the case:

  * Two rules taught opposite things about container queries — `css-standards.md`
    recommended them, `sections.md` banned them — for long enough that nobody
    could say which came first. A contradiction between two injected rules means
    the model picks one arbitrarily, so the standard is whatever the coin says.
  * Editing one snippet injected 2,453 lines of rules, 919 of them CSS authoring
    guidance a Liquid file cannot act on. Nothing measured that, so it grew
    unnoticed until an audit counted it.
  * `prompts-and-references.md` was always-apply and described two directories
    that hold one file each in Base and do not exist in a client fork. It cost
    every task 48 lines of context to say nothing.

None of those is a code defect and none would ever fail a build. They are drift
in the layer that governs everything else, which is exactly the kind of thing
that only gets found by an audit unless something checks it every commit.

What it does NOT do
-------------------
It does not grade the writing or check that a rule is correct — that is review.
It asserts the structural properties the rule system depends on: every rule is
loadable, scoped deliberately, inventoried in CLAUDE.md, and cheap enough to
inject. Content correctness stays a human judgment.

Usage: python3 .claude/scripts/check-ai-config.py [--verbose]
"""

import ast
import fnmatch
import glob
import os
import re
import subprocess
import sys

RULES_DIR = ".claude/rules"

# Rules allowed to load on every file regardless of type. Anything unscoped is
# paid for by every single task, so adding to this list is a deliberate act.
# `prompts-and-references.md` sat here for months describing paths that did not
# exist in the themes that were loading it.
ALWAYS_APPLY_ALLOWLIST = {
    "rules-of-engagement",
    "naming-conventions",
}

# Ceiling on rule lines injected when editing one file of each kind. These are
# not style targets — they are the point at which something has gone structurally
# wrong, normally a large rule scoped more widely than it needs to be. Measured
# values at the time of writing: 1834 / 2119 / 1214 / 1152.
INJECTION_CAPS = {
    "snippets/component-example.liquid": 2000,
    "sections/example.liquid": 2300,
    "assets/section-example.css": 1400,
    "assets/section-example.js": 1400,
}

# Headings that must live in exactly one rule. The CSS split put markup-side
# decisions (class names, custom properties set in a style attribute) in
# css-in-markup.md and stylesheet-side decisions in css-standards.md. If a
# heading reappears in both, the split has been undone by hand.
UNIQUE_HEADINGS = [
    "## BEM Naming Convention",
    "## Scoping CSS to Instances of Sections and Blocks",
    "## Namespace Your CSS Variables",
]


def repo_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def read(path):
    return open(path, encoding="utf-8", errors="replace").read()


def frontmatter(text):
    """Return (dict-ish frontmatter block as text, body) or (None, text)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def paths_of(fm):
    """The `paths:` globs from a frontmatter block, or None for always-apply.

    Accepts both the inline form (`paths: "a,b"`) and the indented YAML list,
    because sync-ai-config.sh accepts both and the two have to agree.
    """
    if fm is None:
        return None
    out, inlist = [], False
    for line in fm.split("\n"):
        if re.match(r"^paths:\s*$", line):
            inlist = True
            continue
        m = re.match(r"^paths:\s*(\S.*)$", line)
        if m:
            return [p.strip().strip('"') for p in m.group(1).split(",")]
        if inlist and re.match(r"^\s+-\s", line):
            out.append(re.sub(r"^\s+-\s*", "", line).strip().strip('"'))
        elif inlist:
            break
    return out or None


def matches(target, globs):
    for g in globs:
        if fnmatch.fnmatch(target, g) or fnmatch.fnmatch(target, g.replace("**/", "")):
            return True
    return False


def load_rules():
    rules = {}
    for path in sorted(glob.glob(f"{RULES_DIR}/*.md")):
        text = read(path)
        fm, body = frontmatter(text)
        rules[os.path.basename(path)[:-3]] = {
            "path": path,
            "text": text,
            "fm": fm,
            "body": body,
            "paths": paths_of(fm),
            "lines": len(text.split("\n")),
        }
    return rules


def check(rules, problems, notes):
    # --- every rule is loadable at all -------------------------------------
    for name, r in rules.items():
        if r["fm"] is None:
            problems.append(f"{r['path']}: no frontmatter block — the harness cannot scope it.")
            continue
        if not re.search(r"^description:\s*\S", r["fm"], re.M):
            problems.append(f"{r['path']}: frontmatter has no `description:`.")

    # --- always-apply is deliberate ----------------------------------------
    unscoped = {n for n, r in rules.items() if r["fm"] is not None and r["paths"] is None}
    for name in sorted(unscoped - ALWAYS_APPLY_ALLOWLIST):
        problems.append(
            f"{rules[name]['path']}: always-apply (no `paths:`) but not in the allowlist.\n"
            "      Every task pays for this rule on every file. Either scope it with a\n"
            "      `paths:` glob, or add it to ALWAYS_APPLY_ALLOWLIST in this script\n"
            "      with a reason in the commit message."
        )
    for name in sorted(ALWAYS_APPLY_ALLOWLIST - unscoped):
        if name in rules:
            notes.append(
                f"{rules[name]['path']} is in the always-apply allowlist but is now scoped. "
                "Remove it from ALWAYS_APPLY_ALLOWLIST."
            )

    # --- injection budget ---------------------------------------------------
    for target, cap in sorted(INJECTION_CAPS.items()):
        total = sum(
            r["lines"] for r in rules.values()
            if r["paths"] is None or matches(target, r["paths"])
        )
        if total > cap:
            loaded = sorted(
                ((r["lines"], n) for n, r in rules.items()
                 if r["paths"] is None or matches(target, r["paths"])),
                reverse=True,
            )
            top = ", ".join(f"{n} ({ln})" for ln, n in loaded[:3])
            problems.append(
                f"editing {target} now injects {total} rule lines (cap {cap}).\n"
                f"      Largest contributors: {top}.\n"
                "      Usually this means a big rule is scoped more widely than it needs\n"
                "      to be. Narrow its `paths:`, or split the part that genuinely applies\n"
                "      — that is what css-in-markup.md was carved out of css-standards.md for."
            )

    # --- the CSS split has not been undone ---------------------------------
    for heading in UNIQUE_HEADINGS:
        owners = [n for n, r in rules.items() if heading in r["body"]]
        if len(owners) > 1:
            problems.append(
                f'heading "{heading}" appears in {len(owners)} rules: {", ".join(sorted(owners))}.\n'
                "      It must live in exactly one. Duplicating it means both copies get\n"
                "      injected together and they will drift apart."
            )

    # --- CLAUDE.md inventory matches disk ----------------------------------
    if os.path.exists("CLAUDE.md"):
        claude = read("CLAUDE.md")
        for name in sorted(rules):
            if f"`{name}.md`" not in claude:
                problems.append(
                    f"{name}.md exists but is not listed in CLAUDE.md.\n"
                    "      CLAUDE.md's inventory is how a reader finds the rule at all."
                )
        for cited in sorted(set(re.findall(r"`([a-z][a-z0-9-]*)\.md`", claude))):
            if cited in rules or cited in ("CLAUDE",):
                continue
            if os.path.exists(f"{RULES_DIR}/{cited}.md"):
                continue
            # Only complain when it looks like a rule reference, i.e. a name that
            # used to be one. Skills, workflows and docs are cited too.
            if os.path.exists(f".claude/workflows/{cited}.md") or os.path.exists(
                f".claude/agents/{cited}.md"
            ):
                continue
            notes.append(f"CLAUDE.md cites `{cited}.md`, which is not a rule, workflow or agent.")

    # --- scripts parse ------------------------------------------------------
    for script in sorted(glob.glob(".claude/scripts/*.py")):
        try:
            ast.parse(read(script))
        except SyntaxError as e:
            problems.append(f"{script}: does not parse — {e}")
    for script in sorted(glob.glob(".claude/scripts/*.sh")):
        r = subprocess.run(["sh", "-n", script], capture_output=True, text=True)
        if r.returncode != 0:
            problems.append(f"{script}: shell syntax error — {r.stderr.strip()}")


def main():
    os.chdir(repo_root())
    verbose = "--verbose" in sys.argv

    rules = load_rules()
    if not rules:
        print(f"No rules found in {RULES_DIR}/ — nothing to check.")
        return 0

    problems, notes = [], []
    check(rules, problems, notes)

    if verbose:
        print(f"{len(rules)} rules, {sum(r['lines'] for r in rules.values())} lines total")
        for target, cap in sorted(INJECTION_CAPS.items()):
            total = sum(
                r["lines"] for r in rules.values()
                if r["paths"] is None or matches(target, r["paths"])
            )
            print(f"  {target:38} {total:>5} / {cap}")

    for n in notes:
        print(f"  note — {n}")

    if not problems:
        print(f"AI config OK ({len(rules)} rules checked).")
        return 0

    print()
    print("=" * 74)
    print(f"  COMMIT BLOCKED — {len(problems)} problem(s) in the AI configuration")
    print("=" * 74)
    print()
    print("  These are structural, not stylistic: a rule that cannot load, is")
    print("  scoped more widely than it earns, contradicts another, or is missing")
    print("  from the inventory that tells people it exists.")
    print()
    for p in problems:
        print(f"    - {p}")
        print()
    print("-" * 74)
    print("  Detail:  python3 .claude/scripts/check-ai-config.py --verbose")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
