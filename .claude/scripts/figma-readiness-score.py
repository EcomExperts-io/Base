#!/usr/bin/env python3
"""Score a Figma frame's structure for the things that make it buildable in one pass.

Why this exists
---------------
The designer practices document is 414 lines and calls itself aspirational —
designers do not read it, and nothing in the workflow checked a frame before a
build started. Every re-prompting cycle it describes comes from the same four
structural facts: default layer names, absolute positioning, no width in the
frame name, hidden leftovers. `get_metadata` exposes three of them as data.
This turns them into a score and a message the AI can send back to the
designer with the specific layers to fix, before anyone builds anything.

Input is the XML `get_metadata` returns, saved to a file. Auto layout is not
visible in metadata — the skill checks that half through the design context.

Usage: figma-readiness-score.py <metadata.xml> [--width 1440] [--json]
Exit 0 always; the verdict is in the output. "send back" means do not build yet.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET

DEFAULT_NAME = re.compile(
    r"^(Frame|Group|Rectangle|Ellipse|Vector|Line|Polygon|Star|Union|Subtract|Intersect|Exclude|"
    r"Component|Instance|Slice|image|Image|img|Mask|Boolean|Arrow|Text)(\s*\d+)?(\s+copy(\s*\d+)?)?$", re.I)


def walk(el, depth=0, out=None):
    out = [] if out is None else out
    out.append((el, depth))
    for child in el:
        walk(child, depth + 1, out)
    return out


def area(el):
    try:
        return float(el.get("width", 0)) * float(el.get("height", 0))
    except ValueError:
        return 0.0


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    width = int(argv[argv.index("--width") + 1]) if "--width" in argv else None
    try:
        root = ET.parse(paths[0]).getroot()
    except ET.ParseError as e:
        print(json.dumps({"error": f"not parseable metadata XML: {e}"}))
        return 1

    nodes = walk(root)
    total = len(nodes)
    default_named = [(el, d) for el, d in nodes if DEFAULT_NAME.match((el.get("name") or "").strip())]
    hidden = [el for el, _ in nodes if (el.get("hidden") or "").lower() == "true"]
    instances = [el for el, _ in nodes if el.tag == "instance"]
    texts = [el for el, _ in nodes if el.tag == "text"]
    vectors = [el for el, _ in nodes if el.tag in ("vector", "boolean-operation", "boolean")]
    max_depth = max(d for _, d in nodes)

    top_name = root.get("name") or ""
    top_w = root.get("width")
    width_in_name = bool(re.search(r"\b(\d{3,4})\b", top_name)) and (
        width is None or str(width) in top_name or (top_w and str(int(float(top_w))) in top_name))

    default_pct = round(100.0 * len(default_named) / max(1, total), 1)
    worst = sorted(default_named, key=lambda t: area(t[0]), reverse=True)[:8]

    checks = [
        {"check": "layer naming", "value": f"{default_pct}% of layers carry a default name",
         "verdict": "pass" if default_pct <= 20 else ("warn" if default_pct <= 40 else "send back"),
         "practice": 4},
        {"check": "hidden layers", "value": f"{len(hidden)} hidden",
         "verdict": "pass" if not hidden else "warn", "practice": 12},
        {"check": "frame width in name", "value": f'"{top_name}" (frame is {top_w}px wide)',
         "verdict": "pass" if width_in_name else "ask", "practice": 3},
        {"check": "components used", "value": f"{len(instances)} instance(s) of components",
         "verdict": "pass" if instances else "warn", "practice": 7},
        {"check": "text as text", "value": f"{len(texts)} text layer(s), {len(vectors)} vector(s)",
         "verdict": "pass" if texts or not vectors else "ask", "practice": 10},
    ]
    overall = "send back" if any(c["verdict"] == "send back" for c in checks) else (
        "ask" if any(c["verdict"] == "ask" for c in checks) else (
            "warn" if any(c["verdict"] == "warn" for c in checks) else "pass"))

    result = {
        "frame": {"id": root.get("id"), "name": top_name, "width": top_w, "height": root.get("height")},
        "layers": total, "max_depth": max_depth,
        "default_named": len(default_named), "default_pct": default_pct,
        "hidden": len(hidden), "instances": len(instances), "texts": len(texts),
        "checks": checks, "overall": overall,
        "worst_default_names": [{"id": el.get("id"), "name": el.get("name"), "w": el.get("width"), "h": el.get("height"), "depth": d} for el, d in worst],
        "hidden_layers": [{"id": el.get("id"), "name": el.get("name")} for el in hidden[:10]],
        "not_measurable_here": ["auto layout vs absolute positioning (read the design context)",
                                "variables/tokens (call get_variable_defs)",
                                "behaviour notes (look for text layers or comments beside the frame)"],
    }
    if "--json" in argv:
        print(json.dumps(result, indent=2))
        return 0

    print(f"Figma readiness — {top_name} ({root.get('id')}, {top_w}×{root.get('height')})")
    print(f"  {total} layers, depth {max_depth}.  Overall: {overall.upper()}")
    print()
    for c in checks:
        print(f"  {c['verdict']:<9} {c['check']:<22} {c['value']}   (practice {c['practice']})")
    print()
    if worst:
        print("  Largest default-named layers — the ones to rename first:")
        for w in result["worst_default_names"]:
            print(f"    {w['id']:<14} {w['name']:<28} {w['w']}×{w['h']}  depth {w['depth']}")
    if hidden:
        print("  Hidden layers to delete or move outside the handoff frame:")
        for h in result["hidden_layers"]:
            print(f"    {h['id']:<14} {h['name']}")
    print()
    print("  Not measurable from metadata: " + "; ".join(result["not_measurable_here"]) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
