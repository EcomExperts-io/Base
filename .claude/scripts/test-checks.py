#!/usr/bin/env python3
"""The checks check themselves: one fixture per behaviour a check promises, run
by the pre-commit hook and CI. Exits 1 the moment a check stops doing what its
docstring says. Add a case here with every change to a check.

Usage: test-checks.py [--verbose]
"""

import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

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


# --- what GitBot reports ---
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

# --- commerce first: the cart engine owns every mutation ---
def js(text, path="assets/component-x.js"):
    f = []
    conv.scan_js(path, text, f)
    return f


f = js("await fetch(`${window.Shopify.routes.root}cart/add.js`, { method: 'POST', body: fd });\n")
case("js: fetch to /cart/add outside cart.js is an error", rules(f) == ["js-raw-cart-request"] and f[0].severity == "error", rules(f))
f = js("const r = await fetch('/cart/change.js', { method: 'POST' });\nxhr.open('POST', '/cart/clear.js');\n")
case("js: change and clear requests are errors too", rules(f) == ["js-raw-cart-request"] * 2, rules(f))
f = js("const res = await fetch(`${window.Shopify.routes.root}cart/update.js`, { method: 'POST' });\n")
case("js: a /cart/update request is a warning (the discount-form pattern)", rules(f) == ["js-raw-cart-update"] and f[0].severity == "warn", rules(f))
f = js("return this.rootElement.querySelectorAll('[action*=\"/cart/add\"]');\nif (!(form.getAttribute('action') || '').includes('/cart/add')) return;\nCart.add(new FormData(form), form);\n")
case("js: cart URLs in selectors and Cart.add() calls are not requests", not f, rules(f))
f = js("fetch('/cart/add.js')", path="assets/cart.js")
case("js: cart.js itself is exempt", not f, rules(f))
f = liquid("<script>fetch('/cart/add.js', {method: 'POST'})</script>\n", path="sections/x.liquid")
case("liquid: an inline script with a raw cart request is an error", "js-raw-cart-request" in rules(f), rules(f))

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
# compare.py, live-parity.py, recon-theme.py — the reference-aware tools
# ---------------------------------------------------------------------------
try:
    from PIL import Image
except ImportError:
    Image = None
if Image is not None:
    with tempfile.TemporaryDirectory() as d:
        a = Image.new("RGB", (100, 60), (255, 255, 255)); a.save(os.path.join(d, "ref.png"))
        b = Image.new("RGB", (100, 60), (255, 255, 255))
        for x in range(50):
            for y in range(60):
                b.putpixel((x, y), (0, 0, 0))
        b.save(os.path.join(d, "ours.png"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "compare.py"), "--reference", os.path.join(d, "ref.png"),
                            "--rendered", os.path.join(d, "ours.png"), "--out", d, "--width", "100", "--reference-label", "Live"],
                           capture_output=True, text=True)
        try:
            res = json.loads(r.stdout)
        except ValueError:
            res = {}
        case("compare: --reference is accepted and a half-black image diffs at 50%",
             r.returncode == 0 and res.get("diff_pct") == 50.0 and res.get("reference", {}).get("kind") == "Live",
             (r.returncode, r.stdout[:120], r.stderr[:120]))
else:
    case("compare: Pillow present for the fixture", False, "Pillow missing — doctor.py says how to install it")

r = subprocess.run([sys.executable, os.path.join(HERE, "live-parity.py"), "--help"], capture_output=True, text=True)
case("live-parity: --help lists the six subcommands", r.returncode == 0 and all(s in r.stdout for s in ("section", "regress", "states", "page", "hoverstyles", "motion")), r.stdout[:80])
r = subprocess.run([sys.executable, os.path.join(HERE, "live-parity.py"), "regress", "--out", "/tmp/x", "--url", "https://example.com"],
                   capture_output=True, text=True)
case("live-parity: regress without --main-theme is a usage error, not a run", r.returncode == 2 and "--main-theme" in r.stderr, (r.returncode, r.stderr[:80]))
r = subprocess.run([sys.executable, os.path.join(HERE, "live-parity.py"), "section", "--out", "/tmp/x", "--live-url", "https://example.com",
                    "--ours-url", "https://example.com/?preview_theme_id=123"], capture_output=True, text=True)
case("live-parity: section without a selector is a usage error", r.returncode == 2 and "--key" in r.stderr, (r.returncode, r.stderr[:80]))

recon = load("recon-theme")
inv = recon.inventory_html('''<html><head><script src="https://cdn.shopify.com/extensions/abc/app.js"></script>
<script src="https://static.klaviyo.com/onsite/js/klaviyo.js"></script><script>window.Shopify={};Shopify.theme={"id":1,"role":"main"};</script>
<script src="https://www.googletagmanager.com/gtm.js?id=GTM-1"></script><script src="https://static.rechargecdn.com/static/js/recharge.js"></script>
<link rel="alternate" hreflang="en-gb" href="/"><style>.replo{}</style></head><body><div id="shopify-section-header"></div>
<div id="shopify-section-template--1__hero"></div><form action="/localization"></form><div class="metafield-rich_text_field"></div></body></html>''', "https://x.test")
case("recon: the live inventory names the vendors it sees",
     "Google Tag Manager" in inv["vendors"]["tracking"] and "Klaviyo" in inv["vendors"]["tracking"]
     and "Recharge" in inv["vendors"]["apps acting on the theme"] and "Replo" in inv["vendors"]["page builders"], inv["vendors"])
case("recon: the live inventory counts sections, embeds, markets and rich text",
     inv["counts"]["sections"] == 2 and inv["counts"]["app_embeds"] == 1 and inv["counts"]["hreflang_alternates"] == 1
     and inv["counts"]["localization_forms"] == 1 and inv["counts"]["rich_text_metafields"] == 1 and inv["theme"], inv["counts"])

# ---------------------------------------------------------------------------
# assemble-templates.py and push-dev-theme.sh — the landing-batch tools
# ---------------------------------------------------------------------------
asm = load("assemble-templates")
good = {"sections": {"main": {"type": section_type, "settings": {known_id: 1}}}, "order": ["main"]}
case("assemble: a template whose keys the schema defines validates clean", not asm.validate_template(good), asm.validate_template(good))
bad = {"sections": {"main": {"type": section_type, "settings": {known_id: 1, "no_such_setting_xyz": "t:sections.x.label"}}}, "order": ["main", "ghost"]}
errs = asm.validate_template(bad)
case("assemble: an unknown setting, a t: value and an order ghost are each an error",
     any("unknown setting" in e for e in errs) and any("`t:` value" in e for e in errs) and any("ghost" in e for e in errs), errs)
errs = []
asm.check_value({"type": "range", "min": 0, "max": 100, "step": 4}, 42, "x", errs)
asm.check_value({"type": "inline_richtext"}, "a<br>b", "y", errs)
asm.check_value({"type": "select", "options": [{"value": "a"}]}, "b", "z", errs)
asm.check_value({"type": "range", "min": 0, "max": 100, "step": 4}, "{{ page.metafields.x.y }}", "dyn", errs)
case("assemble: off-step range, <br> in inline_richtext and a bad option are errors; a dynamic source is not",
     len(errs) == 3 and "not on step" in errs[0] and "<br>" in errs[1] and "not in options" in errs[2], errs)
r = subprocess.run([sys.executable, os.path.join(HERE, "assemble-templates.py"), "--validate-file", "templates/index.json"], capture_output=True, text=True)
case("assemble: --validate-file runs on the repo's own index template", r.returncode in (0, 1) and "templates/index.json" in r.stdout, r.stdout[:80])

r = subprocess.run(["bash", os.path.join(HERE, "push-dev-theme.sh")], capture_output=True, text=True)
case("push-dev-theme: no paths is a usage error", r.returncode == 2 and "usage" in r.stderr, (r.returncode, r.stderr[:60]))
r = subprocess.run(["bash", os.path.join(HERE, "push-dev-theme.sh"), "--theme", "1", "docs/x.md"], capture_output=True, text=True)
case("push-dev-theme: an unknown or wrong-role theme id is refused before anything is pushed", r.returncode in (5, 9), (r.returncode, r.stderr[:80]))
with tempfile.TemporaryDirectory() as d:
    open(os.path.join(d, "protected-themes.txt"), "w").write("# live\n123456\n")
    # the guard reads .claude/protected-themes.txt in the repo root; test the match rule directly
    lines = [l.strip() for l in open(os.path.join(d, "protected-themes.txt")) if l.strip() and not l.startswith("#")]
    case("push-dev-theme: the protected list matches whole ids only", "123456" in lines and "12345" not in lines, lines)

tcs = load("check-theme-staged")
cli4 = [{"path": "/r/sections/a.liquid", "offenses": [{"check": "X", "severity": "error", "start_row": 3, "message": "m"}]}, "stray"]
cli5 = {"valid": False, "issues": [{"filePath": "/r/sections/a.liquid", "check": "X", "severity": "error", "startRow": 4, "message": "m"}], "errorCount": 1}
got4 = list(tcs.offenses(cli4, "/r")); got5 = list(tcs.offenses(cli5, "/r"))
case("theme-staged: both Theme Check JSON shapes (CLI 4 file list, CLI 5 flat issues) yield the same path and an error with its row",
     got4[0][0] == "sections/a.liquid" == got5[0][0] and got4[0][1]["start_row"] == 3 and got5[0][1]["start_row"] == 4 and len(got4) == len(got5) == 1, (got4, got5))

cdi = load("check-docs-interpolation")
doc = "\n".join(["```liquid", "{{ fenced }}", "```", "<code v-pre>{{ ok }}</code>", "`<code v-pre>{{ tag_escaped }}</code>`", "`{{ inline }}`", "plain {{ bare }}"])
hit = [n for n, _ in cdi.offenders_in(doc)]
case("docs-interpolation: a mustache in a fence or a v-pre element passes; inside backticks (even around a v-pre tag) or bare it is flagged", hit == [5, 6, 7], hit)

aic = load("check-ai-config")
with tempfile.TemporaryDirectory() as d:
    b = os.path.join(d, "b.sh"); open(b, "w").write("#!/bin/bash\nA=(1 2)\necho ${#A[@]}\n")
    p = os.path.join(d, "p.sh"); open(p, "w").write("#!/bin/sh\necho ok\n")
    case("ai-config: a shell script is parsed by the interpreter its shebang names, so bash arrays pass and a POSIX script is checked as sh",
         aic.shell_interpreter(b) == "bash" and aic.shell_interpreter(p) == "sh", (aic.shell_interpreter(b), aic.shell_interpreter(p)))

# ---------------------------------------------------------------------------
# where-are-we.py — the three situations, in throwaway repos
# ---------------------------------------------------------------------------
def www(cwd, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "where-are-we.py"), *args], capture_output=True, text=True, cwd=cwd, env=git_env())
    return r.stdout.strip()


def git_env():
    """A git hook exports GIT_DIR and GIT_INDEX_FILE; inherited by a throwaway repo's `git init` and
    `git config`, they rewrite the real repository's config instead. Strip them."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def fork(d, commits=1, subject="[BUILD]: Add a section"):
    g = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True, env=git_env())
    g("init", "-q", "-b", "Develop"); g("config", "user.email", "t@example.com"); g("config", "user.name", "t")
    g("remote", "add", "origin", "https://github.com/EcomExperts-io/Example-Client.git")
    for k in range(commits):
        open(os.path.join(d, "a.txt"), "a").write(str(k) + "\n"); g("add", "."); g("commit", "-q", "-m", subject)
    return g


with tempfile.TemporaryDirectory() as d:
    fork(d, 3)
    case("where-are-we: a bare fork with no state document reads as A", www(d).startswith("where-are-we: looks like A"), www(d)[:90])
with tempfile.TemporaryDirectory() as d:
    g = fork(d, 2)
    os.makedirs(os.path.join(d, "docs/ai-workflow/verify/hero"))
    open(os.path.join(d, "docs/ai-workflow/verify/hero/report.md"), "w").write("x")
    open(os.path.join(d, "docs/ai-workflow/state-of-the-theme.md"), "w").write("# State\n\nMeasured by `recon-theme.py` on 2026-09-01 at `abc`.\n")
    open(os.path.join(d, "docs/ai-workflow/reference-map.md"), "w").write("| Page | Band | Reference | a | b | c | d | e |\n|---|---|---|---|---|---|---|---|\n| Home | Hero | figma | | | | yes | |\n| Home | Offer | live | | | | yes | |\n")
    www(d, "--close-stage", "3", "chrome")
    out = www(d)
    case("where-are-we: an old state document, reports, a closed stage read as B", out.startswith("where-are-we: looks like B") and "last stage closed 3" in out and "2 band(s)" in out, out[:160])
    case("where-are-we: --close-stage wrote progress.json", os.path.exists(os.path.join(d, "docs/ai-workflow/progress.json")))
with tempfile.TemporaryDirectory() as d:
    fork(d, 8, "[FIX]: Something the client found")
    case("where-are-we: a history of fixes reads as C", www(d).startswith("where-are-we: looks like C"), www(d)[:90])
with tempfile.TemporaryDirectory() as d:
    g = fork(d, 2); g("checkout", "-q", "-b", "304.1/Task-QiRoundTwo")
    case("where-are-we: a QA-named branch reads as C", www(d).startswith("where-are-we: looks like C"), www(d)[:90])
with tempfile.TemporaryDirectory() as d:
    fork(d, 2); www(d, "--qa-round", "5")
    out = www(d)
    case("where-are-we: a recorded QA round reads as C with the count", out.startswith("where-are-we: looks like C") and "5 open issue" in out, out[:120])
with tempfile.TemporaryDirectory() as d:
    g = fork(d, 1); g("remote", "set-url", "origin", "git@github.com:EcomExperts-io/Base.git")
    case("where-are-we: Base reads as Base itself", www(d).startswith("where-are-we: Base itself"), www(d)[:60])
with tempfile.TemporaryDirectory() as decoy, tempfile.TemporaryDirectory() as d:
    subprocess.run(["git", "init", "-q", decoy], check=True, env=git_env())
    os.environ["GIT_DIR"] = os.path.join(decoy, ".git"); os.environ["GIT_INDEX_FILE"] = os.path.join(decoy, ".git", "index")
    try:
        fork(d, 1)
    finally:
        del os.environ["GIT_DIR"], os.environ["GIT_INDEX_FILE"]
    bare = subprocess.run(["git", "config", "--local", "core.bare"], cwd=decoy, capture_output=True, text=True).stdout.strip()
    user = subprocess.run(["git", "config", "--local", "user.name"], cwd=decoy, capture_output=True, text=True).stdout.strip()
    case("test-checks: a throwaway repo ignores the GIT_DIR a hook exports, so the real repo's config is untouched",
         os.path.isdir(os.path.join(d, ".git")) and bare == "false" and user == "", (bare, user))

lp = load("live-parity")
os.environ["PROGRAMFILES"] = r"C:\Program Files"
try:
    cands = lp.chrome_candidates()
finally:
    del os.environ["PROGRAMFILES"]
rs = load("render-screenshot")
case("chrome lookup: live-parity and render-screenshot try the Windows install path and bare `chrome` on PATH",
     any(c.endswith(os.path.join("Google", "Chrome", "Application", "chrome.exe")) for c in cands) and "chrome" in cands
     and callable(getattr(rs, "chrome_candidates", None)) and callable(getattr(rs, "kill_tree", None)) and callable(getattr(lp, "kill_tree", None)),
     cands)

# Every script compiles on the oldest Python doctor.py accepts (3.9): a backslash inside an f-string expression,
# fine on 3.12, is a SyntaxError there and takes the whole script down before main() runs.
def oldest_python():
    found = []
    for cand in ("python3.9", "python3.10", "python3.11", "/usr/bin/python3", sys.executable):
        exe = shutil.which(cand) if not os.path.isabs(cand) else (cand if os.path.isfile(cand) else None)
        if not exe:
            continue
        v = subprocess.run([exe, "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"], capture_output=True, text=True)
        if v.returncode == 0:
            found.append((tuple(int(x) for x in v.stdout.split()), exe))
    return min(found)

py_version, py_exe = oldest_python()
sources = sorted(glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "..", "hooks", "*.py")))
r = subprocess.run([py_exe, "-c", "import sys\nfor f in sys.argv[1:]:\n    compile(open(f, encoding='utf-8').read(), f, 'exec')"] + sources,
                   capture_output=True, text=True)
case(f"portability: every script and hook compiles on Python {py_version[0]}.{py_version[1]} (the oldest on this machine; the floor is 3.9)",
     r.returncode == 0 and len(sources) > 10, (py_exe, r.stderr[-200:]))

# The run slots are per machine, not per checkout, and finding them needs no git: a laptop's browser cap is one
# number across every repo on it, and the scripts also run on a machine with no git at all.
with tempfile.TemporaryDirectory() as d:
    os.environ["LIVE_PARITY_SLOTS_DIR"] = os.path.join(d, "slots")
    try:
        lp2 = load("live-parity")
    finally:
        del os.environ["LIVE_PARITY_SLOTS_DIR"]
    nogit = {k: v for k, v in os.environ.items() if k != "PATH"}
    nogit["PATH"] = os.path.join(d, "empty-path")
    os.makedirs(nogit["PATH"])
    r = subprocess.run([sys.executable, os.path.join(HERE, "live-parity.py"), "--help"], capture_output=True, text=True, env=nogit)
    case("live-parity: run slots honour LIVE_PARITY_SLOTS_DIR, default under ~/.cache, and --help works with git off the PATH",
         lp2.SLOTS_DIR == os.path.join(d, "slots") and lp.SLOTS_DIR.startswith(os.path.expanduser("~")) and ".claude" not in lp.SLOTS_DIR
         and r.returncode == 0 and "section" in r.stdout, (lp2.SLOTS_DIR, lp.SLOTS_DIR, r.returncode, r.stderr[-120:]))

with open(os.path.join(HERE, "live-parity.py"), encoding="utf-8") as f:
    lp_src = f.read()
case("live-parity: third-party review widgets are in the known-overlay list, so page mode hides them on both sides",
     all(sel in lp_src for sel in (".jdgm-widget", ".yotpo", "#stamped-main-widget", "#looxReviews", "[data-oke-widget]", '[class*="junip-"]')),
     "")

# ---------------------------------------------------------------------------
# preflight-status.py — in a throwaway client repo
# ---------------------------------------------------------------------------
def preflight(cwd, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "preflight-status.py"), *args],
                       capture_output=True, text=True, cwd=cwd, env=git_env())
    return r.stdout.strip()


with tempfile.TemporaryDirectory() as d:
    g = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True, env=git_env())
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
# check-plugin-contract.py — against a throwaway plugin
# ---------------------------------------------------------------------------
plugin = load("check-plugin-contract")

with tempfile.TemporaryDirectory() as d:
    for skill, phrases in plugin.CONTRACT.items():
        os.makedirs(os.path.join(d, "skills", skill))
        open(os.path.join(d, "skills", skill, "SKILL.md"), "w").write("\n".join(p for p, _ in phrases))
    case("plugin: a plugin carrying every phrase is clean", plugin.check(d) == [], plugin.check(d))
    open(os.path.join(d, "skills", "handoff", "SKILL.md"), "w").write("_Dev checks_")
    out = plugin.check(d)
    case("plugin: a dropped phrase is named with what in Base depends on it",
         any(s == "handoff" and "_Known gaps_" in p and w for s, p, w in out), out)
    shutil.rmtree(os.path.join(d, "skills", "fix-issues"))
    case("plugin: a renamed or removed skill is named", ("fix-issues", "skill not found") in [(s, p) for s, p, _ in plugin.check(d)])
    r = subprocess.run([sys.executable, os.path.join(HERE, "check-plugin-contract.py"), "--brief", "--plugin-dir", d],
                       capture_output=True, text=True)
    case("plugin: drift exits 1 with one line under --brief", r.returncode == 1 and r.stdout.count("\n") == 1, r.stdout)

with tempfile.TemporaryDirectory() as d:
    r = subprocess.run([sys.executable, os.path.join(HERE, "check-plugin-contract.py")],
                       capture_output=True, text=True, env=dict(os.environ, HOME=d, USERPROFILE=d))
    case("plugin: no plugin installed exits 0 and names the fallback", r.returncode == 0 and "fallback" in r.stdout, r.stdout)

# ---------------------------------------------------------------------------
# the store's own area — a pull and the drift report against a throwaway Base and fork
# ---------------------------------------------------------------------------
def put(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


def tool(cwd, script, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args], capture_output=True, text=True, cwd=cwd, env=git_env())


def developer(cwd, *args):
    """new-incident.py as the developer at their terminal: the answer a subprocess without a terminal cannot give."""
    code = ("import importlib.util, sys; s = importlib.util.spec_from_file_location('ni', sys.argv[1]); m = importlib.util.module_from_spec(s); "
            "s.loader.exec_module(m); sys.exit(m.main(sys.argv[2:], developer=True))")
    return subprocess.run([sys.executable, "-c", code, os.path.join(HERE, "new-incident.py"), *args], capture_output=True, text=True, cwd=cwd, env=git_env())


STORE_RULE = ".claude/rules/this-store-breakpoints.md"
STORE_CHECKS = ".claude/this-store/checks.json"
HARVEST, COACH, REPORT = ".claude/scripts/harvest.sh", ".claude/agents/shopify-standards-coach.md", ".claude/scripts/learnings-report.py"

with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as d:
    gb = fork(base, 1)
    put(base, "CLAUDE.md", "# Base\n"); put(base, ".claude/rules/sections.md", "v1\n"); put(base, ".claude/rules/snippets.md", "v1\n")
    put(base, HARVEST, "shipped\n"); put(base, COACH, "shipped\n"); put(base, REPORT, "base only\n")
    gb("add", "."); gb("commit", "-q", "-m", "tooling v1")
    sha1 = gb("rev-parse", "HEAD").stdout.strip()
    g = fork(d, 1)
    put(d, "CLAUDE.md", "# Base\n"); put(d, ".claude/rules/sections.md", "v1\n"); put(d, ".claude/rules/snippets.md", "v1\n")
    put(d, ".base-version", json.dumps({"sha": sha1, "ref": "base/development", "date": "2026-01-01"}))
    put(d, STORE_RULE, "---\ndescription: x\npaths:\n  - \"sections/**\"\n---\nthe store's own line\n")
    put(d, STORE_CHECKS, "[]\n")
    put(d, HARVEST, "shipped\n"); put(d, COACH, "shipped\nthe store's edit\n"); put(d, REPORT, "base only\n")
    g("add", "."); g("commit", "-q", "-m", "fork")
    put(base, ".claude/rules/sections.md", "v2\n"); put(base, STORE_RULE, "BASE WROTE THIS\n")
    gb("rm", "-q", HARVEST, COACH)
    gb("add", "."); gb("commit", "-q", "-m", "tooling v2")
    r = tool(d, "pull-base-tooling.py", "--base-path", base)
    case("pull: a retired file and a Base-only file the store never edited are removed; an edited one is kept and listed",
         not os.path.exists(os.path.join(d, HARVEST)) and not os.path.exists(os.path.join(d, REPORT))
         and os.path.exists(os.path.join(d, COACH)) and "KEEP — retired in Base, edited here (1)" in r.stdout, r.stdout[-600:])
    put(d, HARVEST, "shipped\n")
    r2 = tool(d, "pull-base-tooling.py", "--base-path", base)
    case("pull: an untouched retired file still goes when the stamp already sits past the commit that removed it",
         not os.path.exists(os.path.join(d, HARVEST)) and "RETIRE (1)" in r2.stdout, r2.stdout[-600:])
    case("store area: a pull updates the Base rule the store never touched",
         open(os.path.join(d, ".claude/rules/sections.md")).read() == "v2\n", r.stdout[-400:] + r.stderr[-200:])
    case("store area: a pull never writes a store-owned file, even one Base carries by accident",
         "the store's own line" in open(os.path.join(d, STORE_RULE)).read()
         and not os.path.exists(os.path.join(d, ".claude/.cache/base-new", STORE_RULE)), r.stdout[-400:])
    case("store area: the pull report lists the store's files as store-owned, not fork-only",
         "store-owned (2)" in r.stdout and "fork-only" not in r.stdout, r.stdout[-400:])
    put(d, ".claude/rules/snippets.md", "v1\nthis store uses 769px\n")
    j = json.loads(tool(d, "check-tooling-drift.py", "--base-path", base, "--no-fetch", "--json").stdout or "{}")
    case("drift: a Base file the store edited is listed as edited here; the store's own files are counted apart",
         [e[0] for e in j.get("edited_here", [])] == [".claude/rules/snippets.md"]
         and j.get("store_owned") == [STORE_RULE, STORE_CHECKS] and "harvest" not in j, j)
    brief = tool(d, "check-tooling-drift.py", "--base-path", base, "--no-fetch", "--brief").stdout
    case("drift: the session line says to move the edit to the store area and never says harvest",
         "1 Base file(s) edited here (move to the store area)" in brief and "2 store-owned" in brief and "harvest" not in brief.lower(), brief)

with tempfile.TemporaryDirectory() as d:
    put(d, "rules/this-store-layout.md", "x\n")
    good = {"id": "old-container", "files": "sections/*.liquid", "pattern": r"class=\"[^\"]*\bcontainer\b",
            "severity": "error", "why": "this store's container is page-width", "rule": "this-store-layout.md"}
    put(d, "checks.json", json.dumps([
        good,
        dict(good, id="bad-regex", pattern="(unclosed"),
        dict(good, id="no-why", why=""),
        dict(good, id="no-rule", rule="this-store-missing.md"),
        dict(good, id="base-rule", rule="sections.md"),
        dict(good, id="matches-everything", pattern=".*"),
        dict(good, id="old-container"),
    ]))
    checks, problems = conv.load_store_checks(os.path.join(d, "checks.json"), os.path.join(d, "rules"))
    case("store checks: a usable entry loads; each unusable one is named and skipped without switching the rest off",
         [c[0] for c in checks] == ["store:old-container"] and len(problems) == 6
         and all(k in " ".join(problems) for k in ("bad-regex", "no-why", "no-rule", "base-rule", "matches-everything", "used twice")), problems)
    f = []
    conv.scan_store_checks("sections/hero.liquid", '<div>\n<div class="hero container">\n', checks, f)
    g2 = []
    conv.scan_store_checks("snippets/card.liquid", '<div class="container">', checks, g2)
    case("store checks: a match is a finding on its line, with the store's severity, only in the files the entry names",
         [(x.rule, x.line, x.severity) for x in f] == [("store:old-container", 2, "error")] and not g2, (rules(f), rules(g2)))
    put(d, "broken.json", "{not json")
    case("store checks: a file that is not JSON is one named problem, not a crash",
         conv.load_store_checks(os.path.join(d, "broken.json"), d) == ([], [conv.load_store_checks(os.path.join(d, "broken.json"), d)[1][0]])
         and "not valid JSON" in conv.load_store_checks(os.path.join(d, "broken.json"), d)[1][0])
    case("store checks: no file means no checks and no problems", conv.load_store_checks(os.path.join(d, "absent.json"), d) == ([], []))

with tempfile.TemporaryDirectory() as d:
    g = fork(d, 1)
    put(d, ".claude/rules/this-store-layout.md", "x\n")
    put(d, ".claude/this-store/checks.json", json.dumps([{"id": "old-container", "files": ["sections/*.liquid"], "pattern": "container",
        "severity": "error", "why": "this store's container is page-width", "rule": "this-store-layout.md"}]))
    g("add", "."); g("commit", "-q", "-m", "store check")
    put(d, "sections/hero.liquid", '<div class="container"></div>\n')
    r = tool(d, "check-conventions.py", "--changed", "--block", "--quiet")
    case("store checks: an error in a new file blocks the stop gate's run and names the store rule",
         r.returncode == 1 and "store:old-container" in r.stdout and ".claude/rules/this-store-layout.md" in r.stdout, r.stdout[-300:])
    put(d, ".claude/this-store/checks.json", "[{\"id\": \"x\"}]")
    r = tool(d, "check-conventions.py", "--changed", "--block", "--quiet")
    case("store checks: a check that cannot run fails a blocking run and says which", r.returncode == 1 and "cannot run" in r.stdout and "`x`" in r.stdout, r.stdout[-300:])
    r = tool(d, "check-conventions.py", "--files", "sections/hero.liquid", "--quiet")
    case("store checks: the per-edit run reports a broken check and never blocks", r.returncode == 0 and "cannot run" in r.stdout, r.stdout[-300:])

# ---------------------------------------------------------------------------
# learnings — recorded, answered, and a change to what exists is declared
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    g = fork(d, 1)
    base_sha = g("rev-parse", "HEAD").stdout.strip()
    r = tool(d, "new-incident.py", "--slug", "wrong-container", "--title", "Built with the wrong container", "--scope", "client",
             "--surfaced-by", "qa", "--should-have-caught", ".claude/rules/sections.md", "--date", "2026-01-02")
    inc_file = "docs/ai-workflow/incidents/2026-01-02-wrong-container.md"
    case("learnings: a new record is open and carries the proposed-change section",
         r.returncode == 0 and "status: open" in open(os.path.join(d, inc_file)).read()
         and "## Proposed change to this repo's setup" in open(os.path.join(d, inc_file)).read(), r.stdout + r.stderr)
    g("add", "."); g("commit", "-q", "-m", "record")
    gate = lambda *a: tool(d, "check-learnings.py", "--gate", *a)
    r = gate("--range", f"{base_sha}..HEAD")
    case("learnings: an open learning fails the pull-request gate and is named", r.returncode == 1 and inc_file in r.stdout, r.stdout)
    with tempfile.TemporaryDirectory() as old:
        shutil.copytree(HERE, os.path.join(old, "scripts"))
        put(old, "scripts/check-conventions.py", "# an edited copy from before store checks\n")
        put(d, STORE_CHECKS, "[]\n")
        r = subprocess.run([sys.executable, os.path.join(old, "scripts", "check-learnings.py"), "--gate", "--range", "HEAD..HEAD"],
                           capture_output=True, text=True, cwd=d, env=git_env())
        os.remove(os.path.join(d, STORE_CHECKS))
    case("learnings: store checks beside a checker too old to run them fail the gate and say so",
         r.returncode == 1 and "is NOT being run" in r.stdout, r.stdout + r.stderr)
    r = gate("--range", "HEAD..HEAD")
    case("learnings: a learning that was open before the change is listed and does not fail the gate",
         r.returncode == 0 and "1 older learning(s) still open" in r.stdout, r.stdout)
    brief = tool(d, "check-learnings.py", "--brief").stdout
    case("learnings: the session line lists open learnings by title", "1 open of 1 recorded" in brief and "Built with the wrong container" in brief, brief)
    put(d, STORE_RULE, "---\ndescription: x\npaths:\n  - \"sections/**\"\n---\nUse page-width.\n")
    r = tool(d, "new-incident.py", "--apply", inc_file, "--change", STORE_RULE)
    case("learnings: --apply refuses a learning the developer has not approved", r.returncode == 1 and "not approved" in r.stdout and "--approve" in r.stdout, r.stdout)
    r = tool(d, "new-incident.py", "--approve", inc_file); r_no = tool(d, "new-incident.py", "--decline", inc_file, "--reason", "no")
    case("learnings: with no person at a terminal, neither the yes nor the no can be given, and the developer's command is printed",
         r.returncode == 1 and r_no.returncode == 1 and "in your own terminal" in r.stdout and "status: open" in open(os.path.join(d, inc_file)).read(), r.stdout)
    r = developer(d, "--approve", inc_file)
    case("learnings: the developer's yes marks it approved, and it still fails the gate until applied",
         r.returncode == 0 and "status: approved" in open(os.path.join(d, inc_file)).read() and gate("--range", f"{base_sha}..HEAD").returncode == 1
         and "1 open of 1 recorded" in tool(d, "check-learnings.py", "--brief").stdout, r.stdout)
    put(d, ".claude/rules/sections.md", "x\n")
    r = tool(d, "new-incident.py", "--apply", inc_file, "--change", ".claude/rules/sections.md")
    case("learnings: in a client repo --apply refuses a change to a Base file", r.returncode == 1 and "not in the store's own area" in r.stdout, r.stdout)
    put(d, STORE_RULE, "---\ndescription: x\npaths:\n  - \"sections/**\"\n---\nUse page-width.\n")
    put(d, STORE_CHECKS, json.dumps([{"id": "old-container", "files": "sections/*.liquid", "pattern": "container", "severity": "error", "why": "w", "rule": "this-store-breakpoints.md"}]))
    r = tool(d, "new-incident.py", "--apply", inc_file, "--change", f"{STORE_RULE},{STORE_CHECKS}")
    text = open(os.path.join(d, inc_file)).read()
    case("learnings: --apply closes the record with the files changed and who approved",
         r.returncode == 0 and "status: applied" in text and f"change: {STORE_RULE}, {STORE_CHECKS}" in text and 'approved_by: "t"' in text
         and "## What happened" in text, text[:400])
    g("add", "."); g("commit", "-q", "-m", "[LEARN]: container")
    applied_sha = g("rev-parse", "HEAD").stdout.strip()
    r = gate("--range", f"{base_sha}..HEAD")
    case("learnings: an applied learning that only adds passes the gate", r.returncode == 0, r.stdout)
    put(d, STORE_CHECKS, json.dumps([{"id": "old-container", "files": "sections/*.liquid", "pattern": "container", "severity": "warn", "why": "w", "rule": "this-store-breakpoints.md"}]))
    put(d, STORE_RULE, "---\ndescription: x\npaths:\n  - \"sections/**\"\n---\nUse whatever container.\n")
    g("add", "."); g("commit", "-q", "-m", "loosen")
    r = gate("--range", f"{applied_sha}..HEAD")
    case("learnings: weakening a check or rewriting a store rule with no reason fails the gate and names both",
         r.returncode == 1 and "old-container" in r.stdout and STORE_RULE in r.stdout, r.stdout)
    tool(d, "new-incident.py", "--slug", "container-too-strict", "--title", "The container check was wrong for landing pages", "--date", "2026-01-03")
    inc2 = "docs/ai-workflow/incidents/2026-01-03-container-too-strict.md"
    developer(d, "--approve", inc2)
    tool(d, "new-incident.py", "--apply", inc2, "--change", STORE_CHECKS, "--changes-existing", "landing pages use a full-bleed wrapper")
    g("add", "."); g("commit", "-q", "-m", "[LEARN]: declare")
    r = gate("--range", f"{applied_sha}..HEAD")
    case("learnings: the same change passes once a learning in the diff says why", r.returncode == 0, r.stdout)
    tool(d, "new-incident.py", "--slug", "one-off", "--title", "A one-off", "--date", "2026-01-04")
    one_off = "docs/ai-workflow/incidents/2026-01-04-one-off.md"
    g("add", "."); g("commit", "-q", "-m", "one-off"); before = g("rev-parse", "HEAD").stdout.strip()
    g("rm", "-q", one_off); g("commit", "-q", "-m", "tidy")
    r = gate("--range", f"{before}..HEAD")
    case("learnings: deleting a learning that was still open fails the gate and names it", r.returncode == 1 and one_off in r.stdout and "deleted while still unanswered" in r.stdout, r.stdout)
    g("revert", "--no-edit", "HEAD")
    r = developer(d, "--decline", one_off, "--reason", "will not recur")
    case("learnings: a declined learning is closed with its reason",
         r.returncode == 0 and 'declined_reason: "will not recur"' in open(os.path.join(d, "docs/ai-workflow/incidents/2026-01-04-one-off.md")).read()
         and "0 open of 3 recorded" in tool(d, "check-learnings.py", "--brief").stdout, r.stdout)

with tempfile.TemporaryDirectory() as d:
    g = fork(d, 1)
    L = lambda *a: tool(d, "check-learnings.py", *a)
    L("--signal", "shopify", "a Shopify command failed: shopify theme push"); L("--signal", "shopify", "a Shopify command failed: shopify theme push")
    r1 = L("--pending", "--hold"); r2 = L("--pending", "--hold")
    case("signals: the same signal is raised once, holds the turn the first time it is shown and reports after that",
         r1.returncode == 3 and r1.stdout.count("[shopify]") == 1 and r2.returncode == 0 and "[shopify]" in r2.stdout, (r1.returncode, r2.returncode, r1.stdout))
    r = L("--dismiss", "a typo in the command"); r3 = L("--pending", "--hold")
    case("signals: a dismissal with a reason answers it", "1 signal(s) dismissed" in r.stdout and r3.returncode == 0 and not r3.stdout, r3.stdout)
    www(d, "--qa-round", "4")
    r4 = L("--pending")
    case("signals: a QA round with open issues raises one", "[qa] a QA round came back with 4 open issue(s)" in r4.stdout, r4.stdout)
    L("--signal", "shopify", "a Shopify command failed: shopify theme check")
    qa_id = re.search(r"\[qa\].*\(signal (\w+)\)", r4.stdout).group(1)
    tool(d, "new-incident.py", "--slug", "unrelated", "--title", "Something else", "--date", "2026-01-05")
    r5 = L("--pending")
    case("signals: a learning that names no signal answers none", "[qa]" in r5.stdout and "[shopify]" in r5.stdout, r5.stdout)
    r = tool(d, "new-incident.py", "--slug", "qa-misread", "--title", "Misread the QA note", "--date", "2026-01-05", "--signal", qa_id)
    r6 = L("--pending")
    case("signals: a learning answers the signal it names and leaves the other waiting",
         r.returncode == 0 and "[qa]" not in r6.stdout and "[shopify]" in r6.stdout, r.stdout + r6.stdout)
    r = tool(d, "new-incident.py", "--slug", "bad-id", "--title", "x", "--date", "2026-01-05", "--signal", "zzzzzz")
    case("signals: naming a signal that is not waiting is an error that lists the ones that are", r.returncode == 2 and "no unanswered signal" in r.stdout, r.stdout)
    L("--dismiss", "rehearsed")
    tool(d, "preflight-status.py", "--record", "1", "2", "0")
    case("signals: GitBot findings that needed a fix raise one", "[gitbot] GitBot reported 3 finding(s)" in L("--pending").stdout, L("--pending").stdout)
    hook = lambda: subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "hooks", "stop-gate.py")], input="{}", capture_output=True, text=True,
                                  cwd=d, env=dict(git_env(), CLAUDE_PROJECT_DIR=d))
    os.makedirs(os.path.join(d, ".claude/scripts"))
    for n in ("check-learnings.py", "new-incident.py", "pull_base_tooling_lib.py"):
        shutil.copy(os.path.join(HERE, n), os.path.join(d, ".claude/scripts", n))
    h1 = hook(); h2 = hook()
    case("stop gate: an unanswered signal holds the turn once with what to do, then is a report",
         h1.returncode == 2 and "/record-incident" in h1.stderr and "--dismiss" in h1.stderr and h2.returncode == 0 and "systemMessage" in h2.stdout,
         (h1.returncode, h1.stderr[:200], h2.returncode, h2.stdout[:200]))

with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as stores:
    gb = fork(base, 1); gb("remote", "set-url", "origin", "git@github.com:EcomExperts-io/Base.git")
    shutil.copy(os.path.join(ROOT, ".gitignore"), os.path.join(base, ".gitignore")); gb("add", "."); gb("commit", "-q", "-m", "ignore")
    for name, scope in (("store-a", "generic"), ("store-b", "client")):
        sd = os.path.join(stores, name); os.makedirs(sd); fork(sd, 1)
        tool(sd, "new-incident.py", "--slug", "trap", "--title", f"A trap in {name}", "--scope", scope, "--date", "2026-01-06")
    os.makedirs(os.path.join(stores, "store-c")); fork(os.path.join(stores, "store-c"), 1)
    R = lambda *a: tool(base, "learnings-report.py", "--path", stores, *a)
    out = R().stdout
    case("report: lists the generic learning from one store and not the store-only one from another",
         "store-a/2026-01-06-trap.md" in out and "A trap in store-a" in out and "store-b" not in out
         and "3 repo(s) read, 2 with learnings; 1 generic learning(s) listed" in out, out)
    R("--mark", "store-a/2026-01-06-trap.md", "taken")
    out2 = R().stdout
    case("report: a decided learning stops being listed, and the decision is kept outside git",
         "store-a/" not in out2 and "1 already decided" in out2 and "[taken]" in R("--all").stdout
         and not gb("status", "--porcelain").stdout.strip(), out2 + gb("status", "--porcelain").stdout)
    r = tool(os.path.join(stores, "store-a"), "learnings-report.py", "--path", stores)
    case("report: refuses to run in a store repo", r.returncode == 1 and "runs from Base" in r.stdout, r.stdout)
lib = load("pull_base_tooling_lib")
case("pull: the report is Base's own and never part of what a store pulls; harvest is retired from stores",
     not lib.is_tooling(".claude/scripts/learnings-report.py") and lib.is_tooling(".claude/scripts/check-learnings.py")
     and lib.RETIRED.get(".claude/skills/harvest/SKILL.md", 0) is None and lib.RETIRED.get(".claude/scripts/harvest.sh", 0) is None)

links = load("check-rule-links")
case("rule links: a path in the store's own area is not a broken link in Base; a missing Base path still is",
     links.resolve(".claude/this-store/checks.json", "CLAUDE.md") is None
     and links.resolve(".claude/rules/this-store-layout.md", "CLAUDE.md") is None
     and links.resolve(".claude/rules/not-there.md", "CLAUDE.md") == ".claude/rules/not-there.md")

store_rules = aic.load_rules()
store_rules["this-store-a"] = {"path": ".claude/rules/this-store-a.md", "text": "", "fm": "description: x", "body": "", "paths": None, "lines": 5}
store_rules["this-store-b"] = {"path": ".claude/rules/this-store-b.md", "text": "", "fm": "description: x\npaths:\n  - x", "body": "", "paths": ["sections/**"], "lines": 5000}
sp, sn = [], []
aic.check(store_rules, sp, sn)
case("ai-config: a store rule with no paths is refused; a scoped one is outside CLAUDE.md's inventory and Base's injection caps",
     len(sp) == 1 and "this-store-a.md: a store rule with no `paths:`" in sp[0], sp)
case("ai-config: the store's own rules are noted once they pass the line count",
     any("the store's own rules are 5005 lines" in n for n in sn), sn)

# ---------------------------------------------------------------------------
verbose = "--verbose" in sys.argv
failed = [r for r in RESULTS if not r[1]]
for name, ok, detail in RESULTS:
    if not ok or verbose:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if not ok else ""))
print(f"Check self-tests: {len(RESULTS) - len(failed)} passed, {len(failed)} failed.")
sys.exit(1 if failed else 0)
