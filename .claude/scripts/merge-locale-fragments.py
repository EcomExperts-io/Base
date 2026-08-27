#!/usr/bin/env python3
"""Merge agent locale fragments into the two locale files.

Agents cannot write locales/*.json concurrently without corrupting them, so each
writes {"schema": {...}, "storefront": {...}} to a fragment. This merges every
fragment present, refusing to overwrite an existing key.

Usage: python3 .claude/scripts/merge-locale-fragments.py <fragment-dir>
"""
import json, re, pathlib, subprocess, sys

if len(sys.argv) != 2:
    sys.exit("usage: merge-locale-fragments.py <fragment-dir>")

SP = pathlib.Path(sys.argv[1]).expanduser()
if not SP.is_dir():
    sys.exit(f"not a directory: {SP}")

# Resolve the repo from git rather than a hardcoded path, so this script is
# portable between the client themes forked from Base.
REPO = pathlib.Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

def load(p):
    raw = p.read_text()
    m = re.match(r'^\s*/\*.*?\*/\s*', raw, re.S)
    header = m.group(0) if m else ''
    return header, json.loads(raw[len(header):])

def deep_merge(dst, src, path, conflicts):
    for k, v in src.items():
        if isinstance(v, dict):
            if k in dst and not isinstance(dst[k], dict):
                conflicts.append(f"{path}.{k} (type clash)"); continue
            deep_merge(dst.setdefault(k, {}), v, f"{path}.{k}", conflicts)
        else:
            if k in dst and dst[k] != v:
                conflicts.append(f"{path}.{k}: existing {dst[k]!r} kept, fragment wanted {v!r}")
            else:
                dst[k] = v

frags = sorted(SP.glob("*.json"))
if not frags:
    print("no fragments yet"); sys.exit(0)

targets = {
    "schema":     REPO / "locales/en.default.schema.json",
    "storefront": REPO / "locales/en.default.json",
}
loaded = {k: load(p) for k, p in targets.items()}
conflicts, added = [], {k: 0 for k in targets}

def count_leaves(d):
    return sum(count_leaves(v) if isinstance(v, dict) else 1 for v in d.values())

for f in frags:
    frag = json.loads(f.read_text())
    for key in targets:
        block = frag.get(key) or {}
        if block:
            added[key] += count_leaves(block)
            deep_merge(loaded[key][1], block, key, conflicts)
    print(f"  merged {f.name}")

for key, path in targets.items():
    header, data = loaded[key]
    path.write_text(header + json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{path.name}: +{added[key]} keys")

if conflicts:
    print("\nCONFLICTS (existing values kept):")
    for c in conflicts: print("  -", c)
