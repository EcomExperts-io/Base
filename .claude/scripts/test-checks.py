#!/usr/bin/env python3
"""The checks check themselves.

Why this exists
---------------
There is no test suite (`npm test` is a stub), so every error path in the
gate scripts stayed unexercised until a client build hit it. Four incidents
on one build had that root cause: `check-json.py` crashed on the one file its
own docstring named; `check-rule-links.py` blocked the citation format
CLAUDE.md asks for; `check-conventions.py` read CSS comments as code, and
the fix for that made its `!important` rule unsatisfiable for ten days.
Each fix was written against the single failing case.

So: one fixture per behaviour a check promises, run by the pre-commit hook
and CI. Fast, no dependencies, and it exits 1 the moment a check stops doing
what its docstring says. Add a case here with every change to a check.

Usage: test-checks.py [--verbose]
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
os.chdir(ROOT)


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


conv = load("check-conventions")
contract = load("check-section-contract")

RESULTS = []


def case(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def rules(findings):
    return sorted(f.rule for f in findings)


# ---------------------------------------------------------------------------
# check-conventions.py — CSS
# ---------------------------------------------------------------------------
def css(text):
    f = []
    conv.scan_css("assets/section-x.css", text, f)
    return f


f = css("/* Base used @media (max-width: 768px) and #ff0000 and !important */\n"
        ".a { color: red; }\n")
case("css: patterns inside a comment are not findings", not f, rules(f))

f = css("@media (max-width: 900px) { .a { color: #ff0000; } }\n")
case("css: real max-width query and raw hex are found",
     rules(f) == ["css-max-width-query", "css-raw-hex"], rules(f))

f = css(".a { color: red !important; /* beats an inline style */ }\n")
case("css: !important with a same-line comment passes", "css-important" not in rules(f), rules(f))
f = css(".a {\n  /* beats an inline style */\n  color: red !important;\n}\n")
case("css: !important with a previous-line comment passes", "css-important" not in rules(f), rules(f))
f = css(".a { color: red !important; }\n")
case("css: !important with no comment is a finding", "css-important" in rules(f), rules(f))

block = "".join(f".rule-{i} {{ color: red; margin: {i}px; }}\n" for i in range(45))
f = css(block + ".other { color: blue; }\n" + block)
case("css: a repeated 45-line block is one finding",
     rules(f) == ["css-duplicate-block"] and f[0].line == 47, [(x.rule, x.line) for x in f])
f = css(block)
case("css: a block that appears once is not a duplicate", not f, rules(f))

# ---------------------------------------------------------------------------
# check-conventions.py — Liquid schema and locale keys
# ---------------------------------------------------------------------------
def liquid(text, path="sections/x.liquid"):
    f = []
    conv.scan_liquid(path, text, f)
    return f


def first_leaf(tree, prefix=""):
    for k, v in tree.items():
        if isinstance(v, dict):
            found = first_leaf(v, prefix + k + ".")
            if found:
                return found
        else:
            return prefix + k
    return None


schema_key = first_leaf(conv.locale(conv.LOCALE_SCHEMA))
runtime_key = first_leaf(conv.locale(conv.LOCALE_RUNTIME))
case("locale files load and hold keys", bool(schema_key and runtime_key), (schema_key, runtime_key))


def schema(settings, blocks=None):
    s = {"name": "x", "settings": settings, "blocks": blocks or []}
    return "{% schema %}\n" + json.dumps(s, indent=2) + "\n{% endschema %}\n"


f = liquid(schema([{"type": "text", "id": "a", "label": f"t:{schema_key}"}]))
case("schema: an existing t: key passes", not f, rules(f))
f = liquid(schema([{"type": "text", "id": "a", "label": "t:sections.__no_such_section__.label"}]))
case("schema: a missing t: key is an error",
     rules(f) == ["schema-t-key-missing"] and f[0].severity == "error", rules(f))

f = liquid("<p>{{ '" + runtime_key + "' | t }}</p>\n")
case("liquid: an existing | t key passes", not f, rules(f))
f = liquid("<p>{{ 'no.such.key' | t }}</p>\n")
case("liquid: a missing | t key is an error", rules(f) == ["liquid-t-key-missing"], rules(f))
f = liquid("<p>{{ 'no.such.' | append: status | t }}</p>\n")
case("liquid: a key built at runtime is skipped", not f, rules(f))
f = liquid("{% comment %} {{ 'no.such.key' | t }} {% endcomment %}\n")
case("liquid: a | t inside a Liquid comment is skipped", not f, rules(f))

f = liquid(schema([{"type": "product", "id": "p1", "label": f"t:{schema_key}"},
                   {"type": "product", "id": "p2", "label": f"t:{schema_key}"}]))
case("schema: two product settings in one array is an error", rules(f) == ["schema-product-setting-twice"], rules(f))
f = liquid(schema([{"type": "product", "id": "p1", "label": f"t:{schema_key}"}],
                  [{"type": "b", "name": f"t:{schema_key}", "settings": [{"type": "product", "id": "p2", "label": f"t:{schema_key}"}]}]))
case("schema: one section-level product setting plus one in a block passes", not f, rules(f))
f = liquid(schema([], [{"type": "slide", "name": f"t:{schema_key}", "settings": [
    {"type": "product", "id": "p1", "label": f"t:{schema_key}"}, {"type": "product", "id": "p2", "label": f"t:{schema_key}"}]}]))
case("schema: several product settings in one block pass (shop-the-look ships four)", not f, rules(f))

f = liquid(schema([{"type": "article_list", "id": "a", "label": f"t:{schema_key}", "visible_if": "{{ section.settings.x }}"}]))
case("schema: visible_if on article_list is an error", rules(f) == ["schema-visible-if-resource"], rules(f))
f = liquid(schema([{"type": "text", "id": "a", "label": f"t:{schema_key}", "visible_if": "{{ section.settings.x }}"}]))
case("schema: visible_if on a text setting passes", not f, rules(f))

f = liquid(schema([{"type": "range", "id": "r", "min": 0, "max": 10, "step": 5, "label": f"t:{schema_key}"}]))
case("schema: a two-step range is still an error", rules(f) == ["schema-range-steps"], rules(f))

# ---------------------------------------------------------------------------
# check-conventions.py — template settings against the section schema
# ---------------------------------------------------------------------------
section_type = None
for p in sorted(os.listdir("sections")):
    if p.endswith(".liquid"):
        ids = conv.schema_ids(p[:-7])
        if ids and ids[0]:
            section_type, known_id = p[:-7], sorted(i for i in ids[0] if i)[0]
            break
case("a section with settings exists to test templates against", bool(section_type), section_type)


def template(settings):
    return json.dumps({"sections": {"main": {"type": section_type, "settings": settings}}, "order": ["main"]})


f = []
conv.scan_template_settings("templates/x.json", template({known_id: 1}), f)
case("template: a key the schema defines passes", not f, rules(f))
f = []
conv.scan_template_settings("templates/x.json", template({"no_such_setting_xyz": 1}), f)
case("template: a key the schema does not define is a warning",
     rules(f) == ["template-setting-unknown"] and f[0].severity == "warn", rules(f))
f = []
conv.scan_template_settings("templates/x.json",
                            json.dumps({"sections": {"a": {"type": "shopify://apps/x/blocks/y", "settings": {"z": 1}}}}), f)
case("template: an app section is skipped", not f, rules(f))

# ---------------------------------------------------------------------------
# check-conventions.py — docs orphans
# ---------------------------------------------------------------------------
f = []
conv.scan_docs_orphans(set(), f, sweep=True)
case("docs: no orphan page in this repo (sweep)", not f, [x.path for x in f])

# ---------------------------------------------------------------------------
# check-json.py — locale key cap
# ---------------------------------------------------------------------------
def run_json(obj):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "locales"))
        p = os.path.join(d, "locales", "en.default.schema.json")
        open(p, "w").write(json.dumps(obj))
        r = subprocess.run([sys.executable, os.path.join(HERE, "check-json.py"), p], capture_output=True, text=True)
        return r.returncode, r.stdout


rc, out = run_json({"a": {str(i): "x" for i in range(3401)}})
case("json: a locale over 3,400 keys fails", rc == 1 and "error" in out, out.strip()[:80])
rc, out = run_json({"a": {str(i): "x" for i in range(3350)}})
case("json: a locale over 3,300 keys warns and passes", rc == 0 and "warn" in out, out.strip()[:80])
rc, out = run_json({"a": {"b": "x"}})
case("json: a small locale is silent", rc == 0 and not out.strip(), out.strip()[:80])
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "t.json")
    open(p, "w").write('{"a": 1,}')
    r = subprocess.run([sys.executable, os.path.join(HERE, "check-json.py"), p], capture_output=True, text=True)
    case("json: a trailing comma warns with a line number and passes",
         r.returncode == 0 and ":1 trailing comma" in r.stdout, r.stdout.strip()[:80])

# ---------------------------------------------------------------------------
# check-section-contract.py — preset-seeded blocks
# ---------------------------------------------------------------------------
def contract_src(markup, presets):
    s = {"name": "x", "settings": [
        {"type": "range", "id": k, "min": 0, "max": 100, "step": 4, "label": f"t:{schema_key}"}
        for k in ("padding_top", "padding_bottom", "padding_top_mobile", "padding_bottom_mobile")
    ] + [{"type": "color_scheme", "id": "color_scheme", "label": f"t:{schema_key}"}],
        "blocks": [{"type": "item", "name": f"t:{schema_key}", "settings": [{"type": "text", "id": "text", "label": f"t:{schema_key}"}]}],
        "presets": presets}
    return markup + "\n{% schema %}\n" + json.dumps(s) + "\n{% endschema %}\n"


problems, advisory = contract.check("sections/x.liquid", contract_src(
    "{% for block in section.blocks %}<p>{{ block.settings.text }}</p>{% endfor %}",
    [{"name": f"t:{schema_key}", "blocks": [{"type": "item"}]}]))
case("contract: seeded preset with no blank test is a note, not a block", not problems and len(advisory) == 1, (problems, advisory))
problems, advisory = contract.check("sections/x.liquid", contract_src(
    "{% for block in section.blocks %}{% if block.settings.text != blank %}<p>{{ block.settings.text }}</p>{% endif %}{% endfor %}",
    [{"name": f"t:{schema_key}", "blocks": [{"type": "item"}]}]))
case("contract: seeded preset with a blank test is clean", not problems and not advisory, (problems, advisory))

# ---------------------------------------------------------------------------
verbose = "--verbose" in sys.argv
failed = [r for r in RESULTS if not r[1]]
for name, ok, detail in RESULTS:
    if not ok or verbose:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if not ok else ""))
print(f"Check self-tests: {len(RESULTS) - len(failed)} passed, {len(failed)} failed.")
sys.exit(1 if failed else 0)
