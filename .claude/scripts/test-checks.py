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

block = "".join(f".rule-{i} {{ color: red; z-index: {i}; }}\n" for i in range(45))
f = css(block + ".other { color: blue; }\n" + block)
case("css: a repeated 45-line block is one finding",
     rules(f) == ["css-duplicate-block"] and f[0].line == 47, [(x.rule, x.line) for x in f])
f = css(block)
case("css: a block that appears once is not a duplicate", not f, rules(f))

def liquid(text, path="sections/x.liquid"):
    f = []
    conv.scan_liquid(path, text, f)
    return f


# --- what GitBot reports (Pique, Oct 2026) ---
f = css(".a { gap: 16px; padding-inline: 2.4rem; }\n.b { inline-size: 51.2rem; }\n")
case("css: hardcoded lengths are ONE finding per file with a count",
     rules(f) == ["css-hardcoded-length"] and f[0].detail.startswith("3 declaration"), [(x.rule, x.detail) for x in f])
f = css(".a { border: 1px solid currentColor; outline-offset: 2px; margin: 0; }\n")
case("css: 1px, 2px and 0 are not hardcoded lengths", not f, rules(f))
f = css(".a { --a-gap: 16px; gap: var(--a-gap); }\n@media (min-width: 750px) { .a { gap: var(--a-gap); } }\n")
case("css: a length on a custom property and a media query width pass", not f, rules(f))
f = css(".a { margin-left: auto; padding: 1rem 2rem; text-align: left; top: 0; }\n")
case("css: physical properties are ONE finding per file",
     rules(f) == ["css-hardcoded-length", "css-physical-property"] and "4 declaration" in f[-1].detail, [(x.rule, x.detail) for x in f])
f = css(".a { padding: 1rem; margin-inline: auto; inset: 0; text-align: start; }\n")
case("css: one-value shorthand and logical properties pass", rules(f) == ["css-hardcoded-length"], rules(f))
f = css(".a:nth-child(3) { order: 4; }\n")
case("css: order is an error", rules(f) == ["a11y-css-order"] and f[0].severity == "error", rules(f))
f = css(".a { white-space: nowrap; }\n")
case("css: white-space nowrap is a warning", rules(f) == ["a11y-nowrap"] and f[0].severity == "warn", rules(f))
f = css(".a:focus { outline: none; }\n")
case("css: outline none on :focus is an error", rules(f) == ["a11y-focus-outline-none"], rules(f))
f = css(".a:focus:not(:focus-visible) { outline: none; }\n.a:focus-visible { outline: 2px solid currentColor; }\n")
case("css: outline none behind :not(:focus-visible) passes", not f, rules(f))
f = css(".a:focus { outline: none; box-shadow: 0 0 0 2px currentColor; }\n")
case("css: outline none replaced by a box-shadow passes", "a11y-focus-outline-none" not in rules(f), rules(f))
f = css(".spin { animation: spin 1s linear infinite; }\n")
case("css: an infinite animation with no reduced-motion override warns", rules(f) == ["a11y-motion-no-reduced-motion"], rules(f))
f = css(".spin { animation: spin 1s linear infinite; }\n@media (prefers-reduced-motion: reduce) { .spin { animation: none; } }\n")
case("css: an infinite animation with the override passes", not f, rules(f))
f = css(".a { color: #c8c8c8; }\n")
case("css: a hex in a plain stylesheet is reported", rules(f) == ["css-raw-hex"], rules(f))

f = liquid('<div class="x" onclick="go()">a</div>\n<span role="button">b</span>\n<a @click="open = true">c</a>\n<a href="/x" @click="track()">d</a>\n<button type="button" @click="go()">e</button>\n',
           path="snippets/x.liquid")
case("liquid: div/span/href-less a with a click handler are errors; a with href and button pass",
     rules(f) == ["a11y-div-as-button"] * 3, rules(f))
f = liquid('<img src="{{ img | image_url: width: 800 }}">\n<img src="x" alt="">\n<img src="y" alt="{{ image.alt | escape }}">\n', path="snippets/x.liquid")
case("liquid: an img with no alt attribute at all is one error", rules(f) == ["a11y-img-no-alt"], rules(f))
f = liquid('<meta content="{{ product.metafields.seo.image }}">\n<meta content="{{ product.metafields.seo.image | escape }}">\n<img src="{{ product.metafields.x.img | image_url: width: 100 }}" alt="">\n', path="snippets/x.liquid")
case("liquid: a metafield in an attribute without escape is one security error",
     rules(f) == ["security-unescaped-metafield-attr"], rules(f))
f = liquid('{% comment %} <div onclick="x()"> {% endcomment %}\n', path="snippets/x.liquid")
case("liquid: a div-as-button inside a comment is skipped", not f, rules(f))
f = []
conv.scan_js("assets/section-x.js", 'el.innerHTML = `<div class="close" onclick="c()">x</div>`;\n', f)
case("js: a div with onclick in a template string is an error", rules(f) == ["a11y-div-as-button"], rules(f))

# ---------------------------------------------------------------------------
# check-conventions.py — Liquid schema and locale keys
# ---------------------------------------------------------------------------
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
# preflight-status.py — in a throwaway client repo
# ---------------------------------------------------------------------------
def preflight(cwd, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "preflight-status.py"), *args],
                       capture_output=True, text=True, cwd=cwd)
    return r.stdout.strip()


with tempfile.TemporaryDirectory() as d:
    g = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True)
    g("init", "-q", "-b", "Develop")
    g("config", "user.email", "t@example.com"); g("config", "user.name", "t")
    g("remote", "add", "origin", "https://github.com/EcomExperts-io/Example-Client.git")
    open(os.path.join(d, "a.txt"), "w").write("a\n")
    g("add", "."); g("commit", "-q", "-m", "one")
    case("preflight: silent on a trunk branch", preflight(d, "--changed") == "")
    g("checkout", "-q", "-b", "feature/x")
    out = preflight(d, "--changed")
    case("preflight: a client feature branch with unread findings gets one line", out.startswith("gitbot:") and "feature/x" in out, out[:80])
    preflight(d, "--record", "0", "2", "1")
    case("preflight: silent once HEAD is recorded with nothing open", preflight(d, "--changed") == "")
    preflight(d, "--record", "3", "0", "0")
    out = preflight(d, "--changed")
    case("preflight: open findings on the recorded HEAD are named", "3 GitBot finding(s)" in out, out[:80])
    open(os.path.join(d, "a.txt"), "w").write("b\n"); g("commit", "-qam", "two")
    out = preflight(d, "--changed")
    case("preflight: a new commit after the record is unread again", out.startswith("gitbot:"), out[:80])
    g("remote", "set-url", "origin", "git@github.com:EcomExperts-io/Base.git")
    case("preflight: silent in Base", preflight(d, "--changed") == "")

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
