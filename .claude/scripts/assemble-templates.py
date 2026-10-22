#!/usr/bin/env python3
"""Assemble a page template from per-agent fragments, or validate one, against the section schemas.

Usage
-----
  assemble-templates.py --fragments <dir> --templates a,b [--live-path <live theme dir> | --orders orders.json]
                        [--layout landing] [--write]
  assemble-templates.py --validate-file templates/page.x.json [templates/...]

Without --write it only reports. Exit 1 on any error or missing fragment.

Notes
-----
Shopify reports none of these before the push: a `t:` value left in a template
renders the key path to the shopper; a range off its step or a `<br>` in an
`inline_richtext` is rejected on upload and 500s every route; an unknown
setting is dropped without a word.

Fragments
---------
<fragments>/<agent>/<template>.json holds, per live section key:
  { "<key>": { "type": "...", "settings": {...}, "blocks": {...}, "block_order": [...],
               "disabled": false,
               "_position": "start" | "end" | {"after": "<key>"}   (new sections only) }
    | { "<key>": { "_merged_into": "<other key>" } }   (a live section absorbed by another)
    | { "<key>": { "_skip": "why" } } }                 (deliberately not built)
Keys starting with `_` never reach the template.

Order comes from the live template when --live-path points at a pulled live
theme (templates/page.<name>.json there); otherwise from --orders, a JSON file
{"<template>": ["key", ...]}; otherwise from the fragments as found.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
RICHTEXT_OK = re.compile(r"^\s*<(p|h[1-6]|ul|ol)[\s>]", re.I)
_SCHEMAS = {}


def load_json(path):
    raw = open(path, encoding="utf-8").read()
    raw = re.sub(r"^\s*/\*.*?\*/", "", raw, count=1, flags=re.S)
    return json.loads(raw)


def section_schema(stype):
    if stype in _SCHEMAS:
        return _SCHEMAS[stype]
    result = (None, f"no sections/{stype}.liquid")
    for base in ("sections", "blocks"):
        f = os.path.join(ROOT, base, stype + ".liquid")
        if os.path.exists(f):
            src = open(f, encoding="utf-8").read()
            m = re.search(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", src, re.S)
            if not m:
                result = (None, f"{f}: no schema")
                break
            raw = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
            try:
                result = (json.loads(raw), None)
            except json.JSONDecodeError:
                try:
                    result = (json.loads(re.sub(r",(\s*[}\]])", r"\1", raw)), None)
                except json.JSONDecodeError as e:
                    result = (None, f"{f}: schema is not valid JSON ({e})")
            break
    _SCHEMAS[stype] = result
    return result


def check_value(setting, value, where, errs):
    t = setting.get("type")
    if isinstance(value, str) and value.startswith("t:"):
        errs.append(f"{where}: `t:` value not allowed in a template: {value!r}")
    if isinstance(value, str) and value.strip().startswith("{{") and value.strip().endswith("}}"):
        return  # dynamic source — resolved by Shopify, not typed here
    if t == "range":
        try:
            v = float(value)
        except (TypeError, ValueError):
            errs.append(f"{where}: range needs a number, got {value!r}")
            return
        lo, hi, st = setting.get("min"), setting.get("max"), setting.get("step", 1)
        if lo is not None and (v < lo or v > hi):
            errs.append(f"{where}: {v} outside range {lo}..{hi}")
        elif lo is not None and st and abs(((v - lo) / st) - round((v - lo) / st)) > 1e-9:
            errs.append(f"{where}: {v} not on step {st} from {lo}")
    elif t in ("select", "radio"):
        opts = [o.get("value") for o in setting.get("options", [])]
        if value not in opts:
            errs.append(f"{where}: {value!r} not in options {opts}")
    elif t == "checkbox":
        if not isinstance(value, bool):
            errs.append(f"{where}: checkbox needs true/false, got {value!r}")
    elif t == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errs.append(f"{where}: number needs a number, got {value!r}")
    elif t == "richtext":
        if isinstance(value, str) and value.strip() and not RICHTEXT_OK.match(value):
            errs.append(f"{where}: richtext must start with <p>, <h1-6>, <ul> or <ol>: {value[:50]!r}")
    elif t == "inline_richtext":
        if isinstance(value, str) and re.search(r"</?(p|br)[\s>/]", value):
            errs.append(f"{where}: inline_richtext must not contain <p> or <br> (the upload rejects it)")
    elif t == "image_picker":
        if value not in ("", None) and not (isinstance(value, str) and value.startswith("shopify://shop_images/")):
            errs.append(f"{where}: image_picker should be shopify://shop_images/<file>, got {str(value)[:60]!r}")
    elif t == "color":
        if value not in ("", None) and not (isinstance(value, str) and re.match(r"^(#[0-9a-fA-F]{3,8}|rgba?\(|hsla?\()", value)):
            errs.append(f"{where}: color should be hex/rgb, got {value!r}")
    elif t in ("text", "textarea", "url", "html", "liquid", "video_url"):
        if value is not None and not isinstance(value, str):
            errs.append(f"{where}: {t} needs a string, got {type(value).__name__}")


def validate_section(key, entry, errs):
    stype = entry.get("type")
    if not stype:
        errs.append(f"{key}: no type")
        return
    if str(stype).startswith("shopify://"):
        return
    schema, err = section_schema(stype)
    if err:
        errs.append(f"{key}: {err}")
        return
    sset = {s["id"]: s for s in schema.get("settings", []) if isinstance(s, dict) and s.get("id")}
    for sid, val in (entry.get("settings") or {}).items():
        if sid not in sset:
            errs.append(f"{key}: unknown setting {sid!r} for {stype} — Shopify drops it on upload")
        else:
            check_value(sset[sid], val, f"{key}.settings.{sid}", errs)
    blocks = entry.get("blocks") or {}
    btypes = {b["type"]: b for b in schema.get("blocks", []) if isinstance(b, dict) and b.get("type")}
    if schema.get("max_blocks") and len(blocks) > schema["max_blocks"]:
        errs.append(f"{key}: {len(blocks)} blocks > max_blocks {schema['max_blocks']}")
    for bid, b in blocks.items():
        bt = b.get("type")
        if bt not in btypes and not (bt and str(bt).startswith("shopify://apps")) and bt not in ("@app", "@theme"):
            if "@theme" in btypes or "@app" in btypes:
                continue
            errs.append(f"{key}.blocks.{bid}: unknown block type {bt!r} for {stype} (has {list(btypes)})")
            continue
        bs = btypes.get(bt)
        if bs is None:
            continue
        bset = {s["id"]: s for s in bs.get("settings", []) if isinstance(s, dict) and s.get("id")}
        for sid, val in (b.get("settings") or {}).items():
            if sid not in bset:
                errs.append(f"{key}.blocks.{bid}: unknown setting {sid!r} for block {bt}")
            else:
                check_value(bset[sid], val, f"{key}.blocks.{bid}.settings.{sid}", errs)
        if bs.get("limit"):
            n = sum(1 for x in blocks.values() if x.get("type") == bt)
            if n > bs["limit"]:
                errs.append(f"{key}: block {bt} used {n}x > limit {bs['limit']}")
    order = entry.get("block_order")
    if order is not None:
        for bid in order:
            if bid not in blocks:
                errs.append(f"{key}: block_order names missing block {bid!r}")
        for bid in blocks:
            if bid not in order:
                errs.append(f"{key}: block {bid!r} missing from block_order")


def scan_t_prefix(obj, path, errs):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan_t_prefix(v, f"{path}.{k}", errs)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan_t_prefix(v, f"{path}[{i}]", errs)
    elif isinstance(obj, str) and obj.startswith("t:"):
        errs.append(f"{path}: `t:` value in a template: {obj!r}")


def validate_template(data):
    errs = []
    for k in data.get("order", []):
        if k not in data.get("sections", {}):
            errs.append(f"order names missing section {k!r}")
            continue
        validate_section(k, data["sections"][k], errs)
    for k in data.get("sections", {}):
        if k not in data.get("order", []):
            errs.append(f"section {k!r} missing from order")
    scan_t_prefix(data, "template", errs)
    return errs


def assemble(tpl, fragments_dir, live_path, orders_file, layout):
    live = None
    live_file = os.path.join(live_path, "templates", f"page.{tpl}.json") if live_path else None
    if live_file and os.path.exists(live_file):
        live = load_json(live_file)
    elif orders_file:
        keys = json.load(open(orders_file)).get(tpl, [])
        live = {"order": keys, "sections": {k: {"type": "?"} for k in keys}}
    frags, owners, errs, notes = {}, {}, [], []
    for f in sorted(glob.glob(os.path.join(fragments_dir, "*", f"{tpl}.json"))):
        agent = os.path.basename(os.path.dirname(f))
        try:
            d = load_json(f)
        except (OSError, ValueError) as e:
            errs.append(f"{f}: not valid JSON ({e})")
            continue
        for k, v in d.items():
            if k in frags:
                errs.append(f"key {k} defined by both {owners[k]} and {agent}")
            frags[k] = v
            owners[k] = agent
    if live is None:
        live = {"order": list(frags), "sections": {k: {"type": v.get("type", "?")} for k, v in frags.items()}}
        notes.append("no live template and no --orders: section order follows the fragments")
    sections, order, missing, skipped = {}, [], [], []
    for k in live["order"]:
        ls = live["sections"].get(k, {})
        v = frags.get(k)
        if v is None:
            (skipped if ls.get("disabled") else missing).append(f"{k} ({ls.get('type')})")
            continue
        if "_merged_into" in v:
            notes.append(f"{k} merged into {v['_merged_into']} ({owners[k]})")
            continue
        if v.get("_skip"):
            notes.append(f"{k} deliberately not built: {v['_skip']} ({owners[k]})")
            continue
        sections[k] = {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
        order.append(k)
    for k, v in frags.items():
        if k in live["sections"] or "_merged_into" in v or v.get("_skip"):
            continue
        pos = v.get("_position", "end")
        sections[k] = {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
        if pos == "start":
            order.insert(0, k)
        elif isinstance(pos, dict) and pos.get("after") in order:
            order.insert(order.index(pos["after"]) + 1, k)
        else:
            order.append(k)
        notes.append(f"{k}: new section from {owners[k]} placed {pos}")
    out = {"sections": sections, "order": order}
    if layout:
        out["layout"] = layout
    errs += validate_template(out)
    return out, missing, skipped, notes, errs


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fragments", help="directory holding <agent>/<template>.json fragments")
    ap.add_argument("--templates", help="comma-separated template names (page.<name>.json)")
    ap.add_argument("--live-path", help="a pulled live theme; its templates give the section order")
    ap.add_argument("--orders", help='JSON {"<template>": ["key", ...]} when there is no live template')
    ap.add_argument("--layout", help="layout name to set on the assembled template (e.g. landing)")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--validate-file", nargs="+", help="validate these template files and exit")
    a = ap.parse_args(argv)
    os.chdir(ROOT)
    if a.validate_file:
        rc = 0
        for path in a.validate_file:
            try:
                errs = validate_template(load_json(path))
            except (OSError, ValueError) as e:
                errs = [f"cannot read: {e}"]
            print(f"{path}: " + ("no schema errors" if not errs else f"{len(errs)} error(s)"))
            for e in errs:
                print("  ", e)
            rc = rc or (1 if errs else 0)
        return rc
    if not a.fragments or not a.templates:
        ap.print_usage()
        print("assemble needs --fragments and --templates; or use --validate-file", file=sys.stderr)
        return 2
    rc = 0
    for tpl in [t for t in a.templates.split(",") if t.strip()]:
        out, missing, skipped, notes, errs = assemble(tpl, a.fragments, a.live_path, a.orders, a.layout)
        print(f"\n=== page.{tpl}.json: {len(out['order'])} sections assembled")
        if skipped:
            print(f"  skipped (disabled on live, no fragment): {skipped}")
        for n in notes:
            print("  note:", n)
        if missing:
            print(f"  MISSING fragments for enabled live sections: {missing}")
            rc = 1
        for e in errs:
            print("  ERROR:", e)
        if errs:
            rc = 1
        if a.write and not errs:
            path = os.path.join(ROOT, "templates", f"page.{tpl}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("  wrote", path, f"({len(missing)} enabled live section(s) still missing)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
