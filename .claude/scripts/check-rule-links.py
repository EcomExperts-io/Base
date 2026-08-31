#!/usr/bin/env python3
"""Pre-commit check: paths referenced inside AI config must actually resolve.

Why this exists
---------------
A rule that links a file the repo does not have is silently useless — worse
than useless in a fork, where it sends the reader looking for something that
was never copied down. Two live examples, both found by an audit rather than by
any check:

  * `snippets.md` linked `.cursor/rules/examples/snippet-example.liquid`, which
    exists in Base and not in the client theme forked from it, because the
    examples lived under `.cursor/` and only `.claude/` was carried across.
  * `prompts-and-references.md` was an always-apply rule entirely about
    `.cursor/prompts/` and `.cursor/references/`, neither of which exists in
    that fork.

`sync-ai-config.sh --check` already detects a related kind of drift (an orphan
`.mdc` with no source), so putting this there was tempting. It lives in its own
script instead for two reasons: that script's `--check` contract is "the mirror
is stale, re-run me to fix it", and a broken link is not fixable by running the
sync — the printed remedy would be a lie. And it lets this check follow the
same scoping rule as every other blocking check in this repo.

Scope
-----
Only files **staged in this commit**. A pre-existing broken link in a file you
did not touch is not your commit's problem, and blocking on one would be the
fastest possible way to teach people `--no-verify`. Run with `--all` to sweep
the whole tree — worth doing when you have just forked Base.
"""

import os
import re
import subprocess
import sys

# A markdown link, [text](path). Anchors, URLs and mailto are not paths.
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# A path named in prose or inside backticks. Deliberately conservative: it must
# start with a known config root or a theme directory, and end in a file
# extension or a slash. Anything looser produces false positives on prose like
# "the sections/ directory" — which is why a bare word is never a candidate.
INLINE_PATH_RE = re.compile(
    r"`([^`\s]*?(?:\.claude|\.cursor|sections|snippets|blocks|assets|locales|"
    r"templates|config|layout|docs)/[^`\s]*?)`"
)

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "<")


def repo_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [p for p in out.splitlines() if p]


def all_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def in_scope(path):
    # .cursor/ is generated from .claude/ by sync-ai-config.sh. Checking it
    # would report every finding twice and point the fix at a file that gets
    # overwritten. Fix the source; the mirror follows.
    if path.startswith(".cursor/"):
        return False
    return path.endswith(".md") and (path.startswith(".claude/") or path == "CLAUDE.md")


def candidates(text):
    """Yield (path, kind) pairs worth resolving."""
    for m in MD_LINK_RE.finditer(text):
        yield m.group(1), "link"
    for m in INLINE_PATH_RE.finditer(text):
        yield m.group(1), "path"


def resolve(ref, source):
    """Resolve a reference relative to its source file, then to the repo root."""
    ref = ref.split("#", 1)[0].strip()
    if not ref or ref.startswith(SKIP_PREFIXES):
        return None
    # A glob is a pattern, not a path — `**/*.liquid` in frontmatter, and the
    # `sections/**/*.liquid` forms rules use when describing their own scope.
    if any(ch in ref for ch in "*?"):
        return None
    # A placeholder is a naming template, not a file: `sections/<name>.liquid`,
    # `assets/section-[section-name].js`. Both bracket styles are used in this
    # repo's scaffolding docs and neither is meant to resolve.
    if any(ch in ref for ch in "<>[]{}"):
        return None
    rel = os.path.normpath(os.path.join(os.path.dirname(source), ref))
    if os.path.exists(rel):
        return None
    root_rel = os.path.normpath(ref.lstrip("/"))
    if os.path.exists(root_rel):
        return None
    return rel if ref.startswith((".", "/")) else root_rel


def main():
    os.chdir(repo_root())
    sweep = "--all" in sys.argv
    files = [f for f in (all_files() if sweep else staged_files()) if in_scope(f)]
    if not files:
        return 0

    broken = {}
    for f in files:
        try:
            text = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        seen = set()
        for ref, kind in candidates(text):
            if ref in seen:
                continue
            seen.add(ref)
            missing = resolve(ref, f)
            if missing:
                line = next(
                    (i for i, l in enumerate(text.splitlines(), 1) if ref in l), 0
                )
                broken.setdefault(f, []).append((line, ref, kind))

    if not broken:
        scope = "whole tree" if sweep else f"{len(files)} staged file(s)"
        print(f"Rule cross-references OK ({scope}).")
        return 0

    n = sum(len(v) for v in broken.values())
    print()
    print("=" * 74)
    print(f"  COMMIT BLOCKED — {n} unresolvable path(s) in {len(broken)} file(s)")
    print("=" * 74)
    print()
    print("  A rule that points at a file which is not there sends the reader")
    print("  looking for something that does not exist. In a client fork that")
    print("  is the normal case, not the rare one.")
    print()
    for f, refs in broken.items():
        print(f"  {f}")
        for line, ref, kind in refs:
            where = f":{line}" if line else ""
            print(f"    - {ref}   ({kind}, {f}{where})")
        print()
    print("-" * 74)
    print("  Fix the path, or delete the reference if the file is gone.")
    print("  If it is a file that should be mirrored into .cursor/, add it to")
    print("  .claude/scripts/sync-ai-config.sh instead of relinking.")
    print()
    print("  Sweep the whole tree:  python3 .claude/scripts/check-rule-links.py --all")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
