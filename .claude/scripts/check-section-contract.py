#!/usr/bin/env python3
"""Pre-commit check: new sections must expose the merchant settings contract.

Why this exists
---------------
On the Bites Vitamins build, 30 of 31 new sections shipped with spacing and
colour hardcoded into CSS and no merchant settings behind them. Nothing caught
it: the pre-commit hook logged to a file and carried on, `shopify theme check`
was commented out, and the review agents did not look for it. The pages looked
finished, so nobody noticed for five weeks.

This blocks instead of logging, and only on checks that need no judgment.

Scope
-----
Only sections *added* in this commit. Modifying an existing section does not
trigger it — 23 of Base's 48 sections predate this standard, and most of those
are template main sections or section-group members for which a `presets` entry
would actually be wrong (a merchant should not be able to add a second cart to
a page).

Escape hatches, both requiring a written reason
----------------------------------------------
A Liquid comment mentioning `presets` marks a section as not merchant-addable
and exempts it from the whole contract — the contract is about merchant
editability, so a section a merchant cannot place is out of scope. This works
whether or not the section has a `{% schema %}`: a render-target section may
legitimately have none.

A Liquid comment mentioning `color_scheme` exempts that one setting, for
designs that fix the surface on purpose.

Padding has no exception on a merchant-addable section.
"""

import json
import re
import subprocess
import sys

# Hardcoded English is a rule breach, but it is a different kind of work from a
# missing setting: a section copied from an older Base section can carry 20+
# bare schema labels, each needing a locale key written. These block by default
# — flip this to False if that proves noisy enough that people start reaching
# for --no-verify, which would cost more than the checks are worth.
BLOCK_ON_HARDCODED_STRINGS = True

REFERENCE = ".claude/skills/scaffold-section/reference-section.liquid"
RULE = ".claude/rules/sections.md"

SCHEMA_RE = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.S)
COMMENT_RE = re.compile(r"\{%-?\s*comment\s*-?%\}(.*?)\{%-?\s*endcomment\s*-?%\}", re.S)
# A schema label that is a bare string rather than a `t:` key.
BARE_LABEL_RE = re.compile(r'"(?:label|content|info)"\s*:\s*"(?!t:)([^"]+)"')

# An accessibility attribute holding a literal string. Values containing `{` or
# `}` are Liquid output and therefore fine; `alt=""` is legitimately empty on a
# decorative image, so a value is only flagged when it has at least one char.
#
# Deliberately narrow. Visible body text is NOT checked here: in a Shopify
# content section most of it comes from merchant settings
# (`{{ section.settings.heading | escape }}`), which correctly does not use
# `| t` — `| t` is for theme-provided strings. Detecting the difference in
# freeform markup is not reliable enough for a blocking gate, so that judgment
# stays with the review agents. These attributes are always theme-authored,
# which is what makes them safe to check mechanically.
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
    """Return (schema_dict, error). Tolerates trailing commas — Shopify does,
    and sections/dynamic-grid.liquid in this repo actually has two."""
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
    # The presets exemption is resolved BEFORE the schema is parsed, because a
    # render-target section (rendered by another section, never placed by a
    # merchant) legitimately has no {% schema %} at all. Checking the schema
    # first made the exemption unreachable for exactly the sections it was
    # written for: they had to carry a stub schema to satisfy a check whose own
    # docstring says they are out of scope. sections/pickup-availability.liquid
    # and sections/predictive-results.liquid are both in this state.
    #
    # A malformed schema still blocks regardless — that breaks the theme, and
    # no exemption should hide it.
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

    if "color_scheme" not in setting_ids and not comments_mentioning(src, "color_scheme"):
        problems.append(
            'missing "color_scheme" setting.\n'
            "      If the design fixes this section's surface, keep it hardcoded and\n"
            "      add a Liquid comment mentioning `color_scheme` that says why."
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
            "      Keys go in locales/en.default.json. Five of these shipped to a\n"
            "      client on the Bites Vitamins build."
        )
        (problems if BLOCK_ON_HARDCODED_STRINGS else advisory).append(msg)

    return problems, advisory


def main():
    paths = added_sections()
    if not paths:
        return 0

    failures = {}
    notes = {}
    for p in paths:
        problems, advisory = check(p, staged_content(p))
        if problems:
            failures[p] = problems
        if advisory:
            notes[p] = advisory

    if not failures:
        print(f"Section contract OK ({len(paths)} new section(s) checked).")
        for path, advisory in notes.items():
            print(f"  note — {path}")
            for a in advisory:
                print(f"    {a}")
        return 0

    n = sum(len(v) for v in failures.values())
    print()
    print("=" * 74)
    print(f"  COMMIT BLOCKED — {n} problem(s) in {len(failures)} new section(s)")
    print("=" * 74)
    print()
    print("  Every merchant-addable section must expose padding_top,")
    print("  padding_bottom and color_scheme, plus a presets entry. Without")
    print("  them the page renders correctly and the merchant cannot change")
    print("  anything in the theme editor.")
    print()

    for path, problems in failures.items():
        print(f"  {path}")
        for pr in problems:
            print(f"    - {pr}")
        print()

    print("-" * 74)
    print(f"  Working example: {REFERENCE}")
    print(f"  The rule and why it exists: {RULE}")
    print()
    print("  To bypass for a genuine emergency: git commit --no-verify")
    print("  If you find yourself doing that twice, the check is wrong — say so.")
    print("-" * 74)
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
