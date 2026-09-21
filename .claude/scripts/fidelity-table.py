#!/usr/bin/env python3
"""Turn two box lists — the frame's and the DOM's — into a fidelity table.

Why this exists
---------------
The build workflow says "measure, don't eyeball", and every agent duly reported
a fidelity table it had typed by hand, which is where 614 became "matches 615".
This computes the deltas from two JSON files so the table is arithmetic, not
prose, and so the same properties are compared every time: position, size,
type scale, colour, gap — whatever both sides supply.

Inputs
------
Both files map a layer/element name to its properties. Numbers are compared
with a tolerance; strings (colour, font family) must match exactly.

  {"hero/heading": {"x": 120, "y": 96, "w": 640, "h": 56, "font_size": 45, "line_height": 52,
                    "color": "#17212b"},
   "hero/cta":     {"x": 120, "y": 184, "w": 189, "h": 46}}

The Figma side is written from get_metadata (positions and sizes — subtract the
frame's own x,y so both sides are frame-relative) and get_variable_defs or the
design context (type, colour). The rendered side comes from measure-boxes.js
run in the browser tools.

Usage: fidelity-table.py figma-boxes.json rendered-boxes.json [--tolerance 2] [--json out.json]
Exit 0 always — a report, not a gate.
"""

import json
import sys

NUMERIC_ORDER = ("x", "y", "w", "h", "font_size", "line_height", "letter_spacing", "gap",
                 "padding_top", "padding_bottom", "padding_left", "padding_right", "radius")


def main(argv):
    paths = [a for a in argv if not a.startswith("--") and a.endswith(".json")]
    if len(paths) < 2:
        print(__doc__)
        return 2
    tol = float(argv[argv.index("--tolerance") + 1]) if "--tolerance" in argv else 2.0
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None

    figma = json.load(open(paths[0]))
    rendered = json.load(open(paths[1]))

    rows, off, missing = [], 0, []
    for name in figma:
        f = figma[name]
        r = rendered.get(name)
        if r is None:
            missing.append(name)
            rows.append((name, "—", "present", "missing in DOM", "", "missing"))
            continue
        keys = [k for k in NUMERIC_ORDER if k in f] + [k for k in f if k not in NUMERIC_ORDER]
        for k in keys:
            fv, rv = f.get(k), r.get(k)
            if rv is None:
                rows.append((name, k, fv, "—", "", "unmeasured"))
                continue
            if isinstance(fv, (int, float)) and isinstance(rv, (int, float)):
                d = rv - fv
                status = "ok" if abs(d) <= tol else "off"
                rows.append((name, k, fv, rv, f"{d:+.1f}", status))
            else:
                status = "ok" if str(fv).strip().lower() == str(rv).strip().lower() else "off"
                rows.append((name, k, fv, rv, "", status))
            if status == "off":
                off += 1
    extra = [n for n in rendered if n not in figma]

    print(f"| element | property | Figma | rendered | Δ | |")
    print(f"|---|---|---|---|---|---|")
    for name, k, fv, rv, d, status in rows:
        mark = {"ok": "ok", "off": "**off**", "missing": "**missing**", "unmeasured": "unmeasured"}[status]
        print(f"| {name} | {k} | {fv} | {rv} | {d} | {mark} |")
    print()
    print(f"{len(rows)} comparison(s), {off} off by more than {tol:g}, {len(missing)} element(s) missing in the DOM"
          + (f", {len(extra)} measured but not in the frame list: {', '.join(extra)}" if extra else ""))

    if out_json:
        json.dump({"tolerance": tol, "off": off, "missing": missing, "extra": extra,
                   "rows": [dict(zip(("element", "property", "figma", "rendered", "delta", "status"), r)) for r in rows]},
                  open(out_json, "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
