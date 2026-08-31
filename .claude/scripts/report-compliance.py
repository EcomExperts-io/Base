#!/usr/bin/env python3
"""Standing count: how much of this theme honours the merchant settings contract.

Why this exists
---------------
The Bites Vitamins failure — 30 of 31 new sections shipped with spacing and
colour hardcoded and no merchant settings behind them — ran for five weeks
because nobody was counting. Every individual section looked finished, so the
absence of a control was invisible until an audit went looking for it.

`check-section-contract.py` closes that hole going forward: it blocks a commit
that adds a non-compliant section. But a gate only ever sees new work, by
design — 23 of Base's 48 sections predate the standard and the gate will never
mention them again. That leaves the actual state of the theme unmeasured, which
is the exact condition the incident needed.

This prints the number. It is not a gate — it always exits 0 — it is a figure
you can put in front of someone weekly and watch move. A number that is
reported is a number that cannot quietly drift for five weeks.

Scope
-----
The whole theme, every `sections/*.liquid`, staged or not. That is the
difference from the gate and the reason both exist.

Capability, not spelling
------------------------
See CONTRACT NOTE below. This reports whether a merchant *has* a control, not
whether it is spelled the way the worked example spells it.

Usage:
    python3 .claude/scripts/report-compliance.py
    python3 .claude/scripts/report-compliance.py --json
"""

import glob
import importlib.util
import json
import os
import re
import subprocess
import sys

# The gate. Its parsing and its exemption rules are imported rather than
# copied: two definitions of "compliant" that drift apart would be worse than
# having no report, because the report is the one people would believe.
SELF = ".claude/scripts/report-compliance.py"
CONTRACT_CHECK = ".claude/scripts/check-section-contract.py"
RULE = ".claude/rules/sections.md"
REFERENCE = ".claude/skills/scaffold-section/reference-section.liquid"

# ---------------------------------------------------------------------------
# CONTRACT NOTE — why this does not test for `padding_top` / `padding_bottom`
# ---------------------------------------------------------------------------
# check-section-contract.py tests for those two literal setting ids. For a gate
# on new work that is correct: one spelling keeps new sections uniform, and a
# gate has to be mechanical.
#
# For a standing count it is wrong, and `sections/dynamic-grid.liquid` is the
# proof. It exposes `spacing_top_desktop`, `spacing_bottom_desktop`,
# `spacing_top_mobile` and `spacing_bottom_mobile` — four range controls where
# the contract asks for two, giving the merchant independent desktop and mobile
# vertical rhythm. It is MORE capable than the contract requires, and the id
# check calls it a violation. Counting it as one would park a permanent phantom
# in a number whose entire value is that people trust it.
#
# So the question asked here is the one the rule is actually about: **does a
# merchant have a numeric control over the space above and below this section?**
# A section that answers yes under a different spelling is counted compliant and
# reported separately as "compliant, non-standard ids" — so the naming drift
# stays visible without being scored as a missing control. Fix the spelling in
# new work; do not let it distort the measurement of old work.
SPACING_WORDS = ("padding", "spacing", "margin", "space")

# `range` is what the contract's worked example uses and what every compliant
# Base section uses. `number` is accepted because it is still a merchant
# control over vertical rhythm, which is the capability being measured; nothing
# in Base uses it today. Types that cannot express a spacing value — `select`,
# `checkbox` — deliberately do not count.
SPACING_CONTROL_TYPES = {"range", "number"}

STANDARD_IDS = {"top": "padding_top", "bottom": "padding_bottom"}

WIDTH = 74


def repo_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def load_contract():
    """Import the gate by path — its filename is hyphenated, so `import` won't."""
    if not os.path.exists(CONTRACT_CHECK):
        return None
    spec = importlib.util.spec_from_file_location("check_section_contract", CONTRACT_CHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spacing_side(setting):
    """'top', 'bottom' or None — which edge this setting controls, if any.

    Matched on whole words so that an id like `bottomless_grid` cannot pass and
    `spacing_bottom_mobile` can.
    """
    if not isinstance(setting, dict):
        return None
    if setting.get("type") not in SPACING_CONTROL_TYPES:
        return None
    sid = str(setting.get("id") or "").lower()
    if not any(word in sid for word in SPACING_WORDS):
        return None
    words = set(re.split(r"[^a-z0-9]+", sid))
    if "top" in words:
        return "top"
    if "bottom" in words:
        return "bottom"
    return None


def has_color_scheme(settings):
    """Capability again: the control is a `color_scheme` setting, whatever its id.

    The gate tests `id == "color_scheme"`. A section that typed the setting
    correctly and named it `colour_scheme` gives the merchant exactly the same
    control, so it is counted here.
    """
    for s in settings:
        if not isinstance(s, dict):
            continue
        if s.get("type") == "color_scheme" or s.get("id") == "color_scheme":
            return True
    return False


def schema_body(contract, src):
    """The raw text inside {% schema %}, for the regex counts."""
    m = contract.SCHEMA_RE.search(src)
    return m.group(1) if m else ""


def audit(path, src, contract):
    """Classify one section. Returns a dict; `status` is the headline."""
    row = {
        "path": path,
        "status": None,
        "has_padding": False,
        "padding_ids": [],
        "standard_padding_ids": False,
        "has_color_scheme": False,
        "color_scheme_exempt": False,
        "padding_sides": [],
        "has_presets": False,
        "bare_labels": 0,
    }

    declared_exempt = contract.comments_mentioning(src, "presets")
    schema, err = contract.parse_schema(src)

    # Resolved before parsing, exactly as the gate does it: a render-target
    # section legitimately has no {% schema %} at all, and checking the schema
    # first would make the exemption unreachable for the sections it is for.
    if err == "no {% schema %} block found":
        row["status"] = "exempt" if declared_exempt else "undeclared"
        return row
    if err:
        row["status"] = "unparseable"
        row["error"] = err
        return row

    # Counted before the exemption returns below, and so deliberately wider
    # than the gate's count: the gate exempts a non-addable section from the
    # whole contract, but a hardcoded English label still needs a locale key
    # whether or not a merchant can place the section. `localization.md` has no
    # merchant-addability exception.
    row["bare_labels"] = len(contract.BARE_LABEL_RE.findall(schema_body(contract, src)))

    settings = [s for s in (schema.get("settings") or []) if isinstance(s, dict)]

    sides = {}
    for s in settings:
        side = spacing_side(s)
        if side:
            sides.setdefault(side, []).append(str(s.get("id")))

    row["padding_ids"] = sorted(sides.get("top", []) + sides.get("bottom", []))
    row["padding_sides"] = sorted(sides)
    row["has_padding"] = "top" in sides and "bottom" in sides
    row["standard_padding_ids"] = (
        STANDARD_IDS["top"] in sides.get("top", [])
        and STANDARD_IDS["bottom"] in sides.get("bottom", [])
    )
    row["has_color_scheme"] = has_color_scheme(settings)
    row["color_scheme_exempt"] = contract.comments_mentioning(src, "color_scheme")
    row["has_presets"] = bool(schema.get("presets"))

    if not row["has_presets"] and declared_exempt:
        row["status"] = "exempt"
        return row

    compliant = (
        row["has_padding"]
        and row["has_presets"]
        and (row["has_color_scheme"] or row["color_scheme_exempt"])
    )
    if compliant:
        row["status"] = "compliant" if row["standard_padding_ids"] else "compliant-nonstandard"
    else:
        row["status"] = "violation"
    return row


def tally(rows):
    """Roll the per-section rows up into the numbers the report prints."""
    scored = [r for r in rows if r["status"] in
              ("compliant", "compliant-nonstandard", "violation")]
    compliant = [r for r in scored if r["status"].startswith("compliant")]
    nonstandard = [r for r in scored if r["status"] == "compliant-nonstandard"]
    violations = [r for r in scored if r["status"] == "violation"]
    bare = [r for r in rows if r["bare_labels"]]
    return {
        "sections_total": len(rows),
        "in_scope": len(scored),
        "compliant": len(compliant),
        "compliant_standard_ids": len(compliant) - len(nonstandard),
        "compliant_non_standard_ids": len(nonstandard),
        # Every in-scope section whose padding control exists under ids the gate
        # does not match — the false-flag count, whatever else the section is
        # missing. dynamic-grid.liquid lives here.
        "padding_non_standard_ids": sum(
            1 for r in scored if r["has_padding"] and not r["standard_padding_ids"]
        ),
        "violations": len(violations),
        "missing_padding": sum(1 for r in violations if not r["has_padding"]),
        "missing_color_scheme": sum(
            1 for r in violations if not r["has_color_scheme"] and not r["color_scheme_exempt"]
        ),
        "missing_presets": sum(1 for r in violations if not r["has_presets"]),
        "bare_label_sections": len(bare),
        "bare_labels_total": sum(r["bare_labels"] for r in rows),
        "exempt_declared": sum(1 for r in rows if r["status"] == "exempt"),
        "exempt_undeclared": sum(1 for r in rows if r["status"] == "undeclared"),
        "unparseable": sum(1 for r in rows if r["status"] == "unparseable"),
    }


def pct(n, d):
    return f"{round(100 * n / d)}%" if d else "n/a"


def flags(row):
    """Compact marker of what a violating section is missing."""
    out = []
    if not row["has_padding"]:
        # Naming the half that is there stops "missing padding" reading as
        # "no spacing settings at all" — sections/footer.liquid has a top
        # control and no bottom one.
        half = row["padding_sides"][0] if row["padding_sides"] else ""
        out.append(f"padding ({half} control only)" if half else "padding")
    if not row["has_color_scheme"] and not row["color_scheme_exempt"]:
        out.append("color_scheme")
    if not row["has_presets"]:
        out.append("presets")
    return ", ".join(out)


def line(label, value, note=""):
    """One aligned row of the summary. Notes wrap under the note column."""
    head = f"  {label:<22}{value:>5}"
    if not note:
        print(head)
        return
    pad = " " * (len(head) + 3)
    for i, part in enumerate(note.split("\n")):
        print(f"{head}   {part}" if i == 0 else f"{pad}{part}")


def report(rows, t):
    print()
    print("=" * WIDTH)
    print("  SECTION SETTINGS CONTRACT — standing compliance report")
    print("=" * WIDTH)
    print()
    line("Sections", t["sections_total"], f"{t['in_scope']} in scope, "
         f"{t['exempt_declared'] + t['exempt_undeclared']} exempt, "
         f"{t['unparseable']} unreadable")
    print()
    line("COMPLIANT",
         f"{t['compliant']}/{t['in_scope']}",
         f"{pct(t['compliant'], t['in_scope'])} of sections in scope")
    line("  standard ids", t["compliant_standard_ids"])
    line("  non-standard ids", t["compliant_non_standard_ids"],
         "full contract met, padding spelled\ndifferently")
    print()
    line("NOT COMPLIANT", t["violations"])
    line("  missing padding", t["missing_padding"])
    line("  missing color_scheme", t["missing_color_scheme"])
    line("  missing presets", t["missing_presets"])
    print()
    line("Padding, other ids", t["padding_non_standard_ids"],
         "a range control over vertical space\n"
         "under ids the gate does not match.\n"
         "Present, not missing — see below.")
    print()
    line("Bare schema labels", t["bare_labels_total"],
         f"across {t['bare_label_sections']} section(s); labels not\nusing a `t:` key")
    print()
    line("Exempt, declared", t["exempt_declared"],
         "Liquid comment mentioning `presets`")
    line("Exempt, undeclared", t["exempt_undeclared"],
         "no {% schema %} and no comment — out\nof scope, but nothing says so")
    if t["unparseable"]:
        line("Unparseable schema", t["unparseable"], "broken JSON — fix these first")
    print()

    listed = [r for r in rows if r["status"] in ("violation", "unparseable", "undeclared")]
    if listed:
        print("-" * WIDTH)
        print(f"  {len(listed)} section(s) needing work — the whole list, never truncated.")
        print("  Truncating a compliance report is how the last one stayed hidden.")
        print()
        for r in sorted(listed, key=lambda r: r["path"]):
            if r["status"] == "unparseable":
                detail = r.get("error", "schema does not parse")
            elif r["status"] == "undeclared":
                detail = "no {% schema %}; add a comment mentioning `presets` if deliberate"
            else:
                detail = f"missing {flags(r)}"
                if r["has_padding"] and not r["standard_padding_ids"]:
                    detail += "; padding IS present, under non-standard ids"
            extra = f"  (+{r['bare_labels']} bare labels)" if r["bare_labels"] else ""
            print(f"    {r['path']}")
            print(f"        {detail}{extra}")
        print()

    nonstandard = [r for r in rows if r["has_padding"] and not r["standard_padding_ids"]]
    if nonstandard:
        print("-" * WIDTH)
        print("  Padding control present under non-standard ids. The merchant has")
        print("  the control; the gate matches ids and would call these missing.")
        print("  Rename in new work; do not score them as absent:")
        print()
        for r in sorted(nonstandard, key=lambda r: r["path"]):
            print(f"    {r['path']}")
            print(f"        {', '.join(r['padding_ids'])}")
        print()

    print("-" * WIDTH)
    print("  This reports, it does not block. The gate on newly added sections")
    print(f"  is {CONTRACT_CHECK}")
    print(f"  The rule and why it exists: {RULE}")
    print(f"  A compliant starting point: {REFERENCE}")
    print(f"  Machine-readable: python3 {SELF} --json")
    print("-" * WIDTH)
    print()


def main():
    os.chdir(repo_root())
    as_json = "--json" in sys.argv

    contract = load_contract()
    if contract is None:
        msg = (
            f"{CONTRACT_CHECK} not found — this report reuses its parsing and its "
            "exemption rules rather than keeping a second copy, so it cannot run "
            "without it."
        )
        print(json.dumps({"error": msg}) if as_json else f"  {msg}")
        return 0

    paths = sorted(glob.glob("sections/*.liquid"))
    if not paths:
        msg = "No sections/*.liquid found — nothing to report."
        print(json.dumps({"error": msg}) if as_json else f"  {msg}")
        return 0

    rows = []
    for p in paths:
        src = open(p, encoding="utf-8", errors="replace").read()
        rows.append(audit(p, src, contract))

    t = tally(rows)
    if as_json:
        print(json.dumps({**t, "sections": rows}, indent=2))
    else:
        report(rows, t)
    # Always 0. This is a measurement, not a gate; the moment it can fail a
    # build someone will stop running it.
    return 0


if __name__ == "__main__":
    sys.exit(main())
