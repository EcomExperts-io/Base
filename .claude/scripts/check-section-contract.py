#!/usr/bin/env python3
"""Pre-commit check: new sections must expose the merchant settings contract.

Usage
-----
  check-section-contract.py                  sections ADDED in the staged changeset (the pre-commit hook)
  check-section-contract.py --files <paths>  these working-tree sections, judged as if new (the runtime hooks)
  check-section-contract.py --quiet          say nothing when everything passes

Notes:
- Only sections added in this commit: Base's legacy predates the standard, and a template main section or a
  section-group member would be wrong with a `presets` entry.
- A Liquid comment mentioning `presets` marks a section as not merchant-addable and exempts it from the whole contract,
  with or without a `{% schema %}`; a Liquid comment mentioning `color_scheme` exempts that one setting.
- Padding has no exception: `padding_top`, `padding_bottom`, `padding_top_mobile`, `padding_bottom_mobile`; mobile is its own value.
"""

import json
import os
import re
import subprocess
import sys

# Bare English labels block by default. Flip this to False if that proves noisy
# enough that people start reaching for --no-verify.
BLOCK_ON_HARDCODED_STRINGS = True

REFERENCE = ".claude/skills/scaffold-section/reference-section.liquid"
RULE = ".claude/rules/sections.md"

SCHEMA_RE = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.S)
COMMENT_RE = re.compile(r"\{%-?\s*comment\s*-?%\}(.*?)\{%-?\s*endcomment\s*-?%\}", re.S)
# A schema label that is a bare string rather than a `t:` key.
BARE_LABEL_RE = re.compile(r'"(?:label|content|info)"\s*:\s*"(?!t:)([^"]+)"')

# An accessibility attribute holding a literal string. `{`/`}` in the value is Liquid output and fine; an empty value is
# a legitimate decorative `alt=""`. Visible body text is deliberately NOT checked: most of it is merchant settings, which
# correctly do not use `| t`, and telling the two apart in freeform markup is not reliable enough for a blocking gate.
A11Y_ATTR_RE = re.compile(r'\b(aria-label|alt|title)="([^"{}]+)"')

# Regions to ignore when scanning markup: Liquid comments, the schema block
# (labels are checked separately), and style/stylesheet blocks.
IGNORED_REGIONS = [
    re.compile(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", re.S),
    re.compile(r"\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}", re.S),
    re.compile(r"\{%-?\s*style(?:sheet)?\s*-?%\}.*?\{%-?\s*endstyle(?:sheet)?\s*-?%\}", re.S),
]


def markup_only(src):
    """Strip regions where a literal attribute value is not a finding."""
    for rx in IGNORED_REGIONS:
        src = rx.sub(" ", src)
    return src


def added_sections():
    """Paths of section files added (not modified) in the staged changeset."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-status", "--diff-filter=A"],
        capture_output=True, text=True, check=True,
    ).stdout
    paths = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].startswith("A"):
            p = parts[-1]
            if re.fullmatch(r"sections/[^/]+\.liquid", p):
                paths.append(p)
    return paths


def staged_content(path):
    return subprocess.run(
        ["git", "show", f":{path}"], capture_output=True, text=True, check=True
    ).stdout


def parse_schema(src):
    """Return (schema_dict, error). Tolerates trailing commas, as Shopify does."""
    m = SCHEMA_RE.search(src)
    if not m:
        return None, "no {% schema %} block found"
    raw = m.group(1)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", raw)), None
    except json.JSONDecodeError as e:
        return None, f"{{% schema %}} is not valid JSON: {e}"


def comments_mentioning(src, needle):
    return any(needle in c for c in COMMENT_RE.findall(src))


def check(path, src):
    """Return (blocking, advisory) lists of problem strings for one section."""
    # The presets exemption is resolved BEFORE the schema is parsed: a render-target section legitimately has no
    # {% schema %} at all. A malformed schema still blocks regardless.
    schema, err = parse_schema(src)
    if err == "no {% schema %} block found" and comments_mentioning(src, "presets"):
        return [], []
    if err:
        return [err], []

    setting_ids = {
        s.get("id") for s in (schema.get("settings") or []) if isinstance(s, dict)
    }
    schema_raw = SCHEMA_RE.search(src).group(1)
    problems = []
    advisory = []

    has_presets = bool(schema.get("presets"))
    declared_not_addable = comments_mentioning(src, "presets")

    if not has_presets and declared_not_addable:
        # Not merchant-addable and says so. The contract does not apply.
        return [], []

    if not has_presets:
        problems.append(
            'no "presets" entry — a merchant cannot add this section at all.\n'
            "      If that is deliberate (a template main section or a section-group\n"
            "      member), say so in a Liquid comment mentioning `presets` and this\n"
            "      check will skip the section entirely."
        )

    for key in ("padding_top", "padding_bottom"):
        if key not in setting_ids:
            problems.append(f'missing "{key}" setting — required, no exceptions.')
    for key in ("padding_top_mobile", "padding_bottom_mobile"):
        if key not in setting_ids:
            problems.append(
                f'missing "{key}" setting — required, no exceptions.\n'
                "      Mobile padding is its own merchant value, not `padding_top | times: 0.75`;\n"
                "      read it outside the media query and the desktop pair inside it."
            )

    if "color_scheme" not in setting_ids and not comments_mentioning(src, "color_scheme"):
        problems.append(
            'missing "color_scheme" setting.\n'
            "      If the design fixes this section's surface, keep it hardcoded and\n"
            "      add a Liquid comment mentioning `color_scheme` that says why."
        )

    # A preset that seeds blocks hands the merchant blank blocks, so unless the loop skips an empty block the section
    # renders a coloured band around nothing. Advisory: the markup may test emptiness some other way.
    seeded = sum(len(p.get("blocks") or []) for p in (schema.get("presets") or []) if isinstance(p, dict))
    markup = markup_only(src)
    if seeded and "section.blocks" in markup and "blank" not in markup:
        advisory.append(
            f"the preset seeds {seeded} block(s) with no content and the markup never tests `blank`:\n"
            "      a merchant who adds this section sees an empty coloured band. Skip a block whose\n"
            "      content settings are blank and render nothing when none survives (sections.md,\n"
            "      'A preset-seeded block renders nothing until it has content')."
        )

    bare = BARE_LABEL_RE.findall(schema_raw)
    if bare:
        shown = ", ".join(f'"{b}"' for b in bare[:3])
        more = f" (+{len(bare) - 3} more)" if len(bare) > 3 else ""
        msg = (
            f"{len(bare)} schema label(s) are hardcoded English, not `t:` keys: "
            f"{shown}{more}\n"
            "      Schema strings use a `t:` key resolving in\n"
            "      locales/en.default.schema.json. Note that older Base sections\n"
            "      use bare labels — do not copy that pattern forward."
        )
        (problems if BLOCK_ON_HARDCODED_STRINGS else advisory).append(msg)

    hardcoded = A11Y_ATTR_RE.findall(markup_only(src))
    if hardcoded:
        shown = ", ".join(f'{a}="{v}"' for a, v in hardcoded[:3])
        more = f" (+{len(hardcoded) - 3} more)" if len(hardcoded) > 3 else ""
        msg = (
            f"{len(hardcoded)} accessibility attribute(s) hold hardcoded English: "
            f"{shown}{more}\n"
            "      These are theme-authored strings, so they need a locale key:\n"
            '      aria-label="{{ \'sections.example.label\' | t }}"\n'
            "      Keys go in locales/en.default.json."
        )
        (problems if BLOCK_ON_HARDCODED_STRINGS else advisory).append(msg)

    return problems, advisory


def working_tree_content(path):
    return open(path, encoding="utf-8", errors="replace").read()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    quiet = "--quiet" in argv

    if "--files" in argv:
        mode = "files"
        given = [os.path.normpath(a) for a in argv[argv.index("--files") + 1:] if not a.startswith("--")]
        paths = [p for p in given if re.fullmatch(r"sections/[^/]+\.liquid", p) and os.path.exists(p)]
        content = working_tree_content
    else:
        mode = "staged"
        paths = added_sections()
        content = staged_content
    if not paths:
        return 0

    failures = {}
    notes = {}
    for p in paths:
        problems, advisory = check(p, content(p))
        if problems:
            failures[p] = problems
        if advisory:
            notes[p] = advisory

    if not failures:
        # --quiet silences the all-clear, not a note: the runtime hooks run
        # with it, and a note nobody can see is not advisory, it is absent.
        if not quiet:
            print(f"Section contract OK ({len(paths)} new section(s) checked).")
        for path, advisory in notes.items():
            print(f"  note — {path}")
            for a in advisory:
                print(f"    {a}")
        return 0

    n = sum(len(v) for v in failures.values())
    banner = "COMMIT BLOCKED" if mode == "staged" else "BLOCKED"
    print()
    print("=" * 74)
    print(f"  {banner} — {n} problem(s) in {len(failures)} new section(s)")
    print("=" * 74)
    print()
    print("  Every merchant-addable section must expose padding_top,")
    print("  padding_bottom, padding_top_mobile, padding_bottom_mobile and")
    print("  color_scheme, plus a presets entry. Without them the page renders")
    print("  correctly and the merchant cannot change anything in the theme editor.")
    print()

    for path, problems in failures.items():
        print(f"  {path}")
        for pr in problems:
            print(f"    - {pr}")
        print()

    print("-" * 74)
    print(f"  Working example: {REFERENCE}")
    print(f"  The rule and why it exists: {RULE}")
    if mode == "staged":
        print()
        print("  To bypass for a genuine emergency: git commit --no-verify")
        print("  If you find yourself doing that twice, the check is wrong — say so.")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
