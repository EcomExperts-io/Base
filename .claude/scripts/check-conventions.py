#!/usr/bin/env python3
"""Mechanical checks for the conventions in .claude/rules that a grep can decide.

Why this exists
---------------
The rules run to about 3,700 lines. Before this script the gate enforced four
setting ids, a `presets` entry and bare schema labels — roughly five percent of
what the rules ask for. Everything else depended on the model reading the rule
and obeying it, and the audit of 14 Sep 2026 measured what that produced in
Base itself: 38 CSS files with `max-width` queries against a rule that says
never, raw hex in 9 of 29 section stylesheets, four sections still on
`{% stylesheet %}`. None of those needs judgment to find. They need a regex.

Two of the checks catch things that take the whole theme down with a 500 on
every route and that Theme Check does not report: a `range` setting with fewer
than three steps, and a `t:` key left in a template value. Both happened on a
client build before they were written down.

Scope model — you answer for what you ADD
------------------------------------------
A finding is *blocking* only when it has error severity AND sits in a file that
is new. Modified files are reported, never gated: Base carries legacy that
predates every one of these rules, and a gate that fires on inherited offenses
during unrelated work is switched off within a week. The Bites Vitamins hook
was exactly that — it logged and exited 0 and nobody read the log.

Modes
-----
  --files <paths...>   report on these working-tree files; never blocks
  --staged             pre-commit: added files block, modified files warn
  --changed            working tree vs HEAD (the Stop hook): new files block
  --all                every tracked theme file; report only
                       (also sweeps docs/ for pages whose section or snippet is gone)
  --block              with --changed or --all, exit 1 on blocking findings
  --quiet              print nothing when there is nothing to say
"""

import glob
import json
import os
import re
import subprocess
import sys

THEME_DIRS = ("sections/", "snippets/", "assets/", "layout/", "templates/",
              "locales/", "config/", "blocks/")

# Files whose whole job is to hold the merchant's raw values. Hex is not a
# finding there. snippets/css-variables.liquid is deliberately NOT here any
# more: a literal hex in it is a brand colour no merchant setting controls,
# and GitBot reports it (Pique, Oct 2026, `--brand-rule-silver: #c8c8c8`).
TOKEN_FILES = {"config/settings_schema.json", "config/settings_data.json"}

# ---------------------------------------------------------------------------
# rule definitions — id, severity, one-line reason, and the rule file it serves
# ---------------------------------------------------------------------------
RULES = {
    "css-max-width-query": ("error", "mobile-first: media queries are `min-width` only", "css-standards.md"),
    "css-raw-hex":         ("warn",  "use a `var(--color-*)` token, not a raw hex", "css-standards.md"),
    "css-important":       ("warn",  "`!important` needs a comment on the same or previous line saying why", "css-standards.md"),
    "js-domcontentloaded": ("error", "wrap the logic in a custom element; no `DOMContentLoaded`", "javascript-standards.md"),
    "js-jquery":           ("error", "jQuery is never added to this codebase", "rules-of-engagement.md"),
    "liquid-stylesheet-tag": ("error", "sections load CSS with `asset_url | stylesheet_tag` and JS as type=\"module\", not `{% stylesheet %}` / `{% javascript %}`", "sections.md"),
    "liquid-script-not-module": ("warn", "section and snippet scripts load as `type=\"module\"`", "sections.md"),
    "liquid-output-in-string": ("error", "an output tag inside a Liquid string literal is a parse error — every route 500s", "liquid.md"),
    "liquid-raw-in-comment": ("error", "`{% raw %}` inside `{% comment %}` unbalances the comment — every route 500s", "liquid.md"),
    "schema-range-steps":  ("error", "a `range` needs at least 3 steps between min and max or the theme upload fails", "schemas.md"),
    "template-t-key":      ("error", "Shopify does not resolve `t:` in template values — the key path renders to the customer", "templates.md"),
    "section-asset-shared": ("error", "a `section-*` asset is loaded by more than one section; rename to `component-*` or confirm the sections are one feature", "naming-conventions.md"),
    # --- harvested from the Pique rebuild, Sep–Oct 2026 ---
    "css-duplicate-block": ("warn", "this run of lines repeats an earlier block in the same file; the later copy silently wins — delete it", "css-standards.md"),
    "schema-t-key-missing": ("error", "a `t:` key in the schema has no entry in locales/en.default.schema.json — the theme editor shows a missing-translation label", "localization.md"),
    "liquid-t-key-missing": ("error", "a `| t` key has no entry in locales/en.default.json — the key path renders as visible text", "localization.md"),
    "schema-product-setting-twice": ("error", "only one `product` setting in a section's own settings uploads; put the second picker in a block", "schemas.md"),
    "schema-visible-if-resource": ("error", "Shopify rejects `visible_if` on an `article_list` or `blog` setting at upload; Theme Check passes it", "schemas.md"),
    "template-setting-unknown": ("warn", "a template sets a key its section or block schema does not define — Shopify drops it silently on upload", "templates.md"),
    "docs-orphan-page": ("warn", "a docs page describes a section or snippet that no longer exists — delete or rewrite it", "living-documents.md"),
    # --- what GitBot reports on every push that the gate did not (Pique, Oct 2026).
    # Severity follows GitBot's: its Minor is a warning here, its Major and
    # Critical are errors. Errors still block only in a file the change adds.
    "css-hardcoded-length": ("warn", "px/rem values are set on a namespaced custom property first, then used (`--x-gap: 16px;` … `gap: var(--x-gap)`)", "css-standards.md"),
    "css-physical-property": ("warn", "use the logical property (`padding-inline`, `margin-block-start`, `inset-inline-end`, `text-align: start`) for RTL", "css-standards.md"),
    "a11y-css-order": ("error", "`order` makes visual order differ from DOM and tab order (WCAG 2.4.3); reorder the markup instead", "accessibility.md"),
    "a11y-nowrap": ("warn", "`white-space: nowrap` on text can overflow at 200% zoom or in a longer locale (WCAG 1.4.10); let it wrap or justify why", "accessibility.md"),
    "a11y-focus-outline-none": ("error", "a `:focus` rule removes the outline and replaces it with nothing (WCAG 2.4.7); style `:focus-visible` with a visible outline", "accessibility.md"),
    "a11y-motion-no-reduced-motion": ("warn", "an infinite animation with no `prefers-reduced-motion: reduce` override in the file (WCAG 2.3.3)", "accessibility.md"),
    "a11y-div-as-button": ("error", "a click handler on a div, span, li or href-less `<a>`: not focusable, not keyboard-operable — use `<button type=\"button\">`", "accessibility.md"),
    "a11y-img-no-alt": ("error", "an `<img>` with no `alt` attribute at all; `alt=\"\"` when decorative, the merchant value escaped otherwise", "accessibility.md"),
    "security-unescaped-metafield-attr": ("error", "a metafield output inside a quoted attribute without `| escape` can inject markup", "accessibility.md"),
    # --- commerce first: the cart engine owns every cart mutation.
    "js-raw-cart-request": ("error", "a request to /cart/add, /cart/change or /cart/clear outside assets/cart.js bypasses the queue, the section render and `cart:change`; use `window.Cart.add/change`", "javascript-standards.md"),
    "js-raw-cart-update": ("warn", "a request to /cart/update outside assets/cart.js: allowed for a form that then calls `Cart.refresh()` (the discount form), wrong anywhere else", "javascript-standards.md"),
}

# A locale file that cannot be read or parsed switches the key checks off
# rather than reporting every key as missing.
LOCALE_SCHEMA = "locales/en.default.schema.json"
LOCALE_RUNTIME = "locales/en.default.json"

# A repeated stylesheet block is only worth reporting at a size no two rules
# reach by coincidence. Pique's featured-product stylesheet carried three
# copies of 100–200 lines; 40 is well under that and well over any legitimate
# repeat of a short reset.
DUP_RUN = 40

SEVERITY_ORDER = {"error": 0, "warn": 1}


class Finding:
    __slots__ = ("path", "line", "rule", "detail")

    def __init__(self, path, line, rule, detail=""):
        self.path, self.line, self.rule, self.detail = path, line, rule, detail

    @property
    def severity(self):
        return RULES[self.rule][0]


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def repo_root():
    return git("rev-parse", "--show-toplevel").strip()


def is_theme_file(path):
    return path.startswith(THEME_DIRS)


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# CSS — runs on .css files and on the CSS blocks inside .liquid files
# ---------------------------------------------------------------------------
def blank_css_comments(text):
    """Replace every `/* … */` body with spaces, keeping newlines.

    Comments are prose. A note explaining why a pattern was *avoided* — "Base
    expressed this as a max-width override", "this is why the !important is not
    carried over" — must not be reported as a use of it, and the two ways out of
    a false error are to delete the explanation or paraphrase around the word.
    Blanking rather than deleting keeps every byte offset, so `line_of` and the
    `offset` used for CSS inside Liquid stay exact.

    See docs/ai-workflow/incidents/2026-09-16-conventions-checker-reads-css-comments-as-code.md
    """
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def scan_css(path, text, findings, offset=0, hex_check=True):
    raw_lines = text.split("\n")
    text = blank_css_comments(text)

    for m in re.finditer(r"@media[^{]*max-width", text):
        findings.append(Finding(path, offset + line_of(text, m.start()), "css-max-width-query"))

    if hex_check:
        # Only a hex in a property VALUE counts — `#product-grid` is an id selector.
        for m in re.finditer(r":[^;{}\n]*?(#[0-9a-fA-F]{3,8})\b", text):
            snippet = text[max(0, m.start() - 40):m.end()]
            if "url(" in snippet:
                continue
            findings.append(Finding(path, offset + line_of(text, m.start(1)), "css-raw-hex", m.group(1)))

    # The `!important` itself is looked for in the blanked text, so one inside
    # a comment is not a finding. The comment that excuses it is looked for in
    # the ORIGINAL lines: after blanking there is no `/*` left anywhere, and
    # for ten days this rule could not be satisfied in a .css file at all
    # (Pique, Sep 2026) — a warning nobody can clear is a warning everyone
    # learns to skim.
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if "!important" in ln:
            raw, prev = raw_lines[i], (raw_lines[i - 1] if i else "")
            if "/*" not in raw and "/*" not in prev and "//" not in raw:
                findings.append(Finding(path, offset + i + 1, "css-important"))

    scan_css_duplicates(path, raw_lines, findings, offset)
    scan_css_gitbot(path, text, findings, offset)


LENGTH_RE = re.compile(r"(?<![\w.-])(\d*\.?\d+)(px|rem)\b")
DECL_RE = re.compile(r"(?<![\w-])([a-zA-Z-]+)\s*:\s*([^;{}]+);")
PHYSICAL_RE = re.compile(
    r"^(?:(?:margin|padding)-(?:top|bottom|left|right)|border-(?:top|bottom|left|right)(?:-(?:width|color|style))?"
    r"|top|bottom|left|right)$")
BLOCK_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def scan_css_gitbot(path, text, findings, offset=0):
    """The CSS findings GitBot raised on push after the local gate passed.

    Measured on Pique's last 30 days of reviews (Oct 2026): every Minor
    css-standards finding was a hardcoded length, a physical property or a
    hex; every Major accessibility finding in CSS was `order`, `nowrap`, an
    `outline: none` on `:focus`, or a spinner with no reduced-motion override.
    The high-volume pair (lengths, physical) is ONE finding per file with a
    count, the way the review policy asks a reviewer to report them.
    """
    hard, phys = [], []
    for m in DECL_RE.finditer(text):
        prop, value = m.group(1).lower(), m.group(2).strip()
        line = offset + line_of(text, m.start())
        if prop.startswith("--") or prop in ("content",):
            continue
        # Lengths: anything over 2px. Hairlines, 1px borders and a 2px
        # outline-offset are universal values, not design tokens, and GitBot's
        # own suggested fixes use them.
        lengths = [(float(n), u) for n, u in LENGTH_RE.findall(value)]
        if any(u == "rem" or n > 2 for n, u in lengths):
            hard.append((line, f"{prop}: {value}"))
        if prop == "order":
            findings.append(Finding(path, line, "a11y-css-order", f"{prop}: {value}"))
        elif prop == "white-space" and "nowrap" in value:
            findings.append(Finding(path, line, "a11y-nowrap"))
        elif PHYSICAL_RE.match(prop):
            phys.append((line, f"{prop}: {value}"))
        elif prop == "text-align" and re.match(r"(left|right)\b", value):
            phys.append((line, f"{prop}: {value}"))
        elif prop in ("margin", "padding"):
            # A one-value shorthand is symmetric and RTL-safe. Two or more
            # values set sides by physical position. (GitBot has also flagged
            # the one-value form; this check does not, on purpose.)
            parts = [p for p in value.split() if p != "!important"]
            if len(parts) >= 2:
                phys.append((line, f"{prop}: {value}"))
    for items, rule in ((hard, "css-hardcoded-length"), (phys, "css-physical-property")):
        if items:
            shown = "; ".join(v for _, v in items[:3])
            more = f" … and {len(items) - 3} more" if len(items) > 3 else ""
            findings.append(Finding(path, items[0][0], rule, f"{len(items)} declaration(s): {shown}{more}"))

    for m in BLOCK_RE.finditer(text):
        selector, body = m.group(1), m.group(2)
        if ":focus" not in selector or "focus-visible)" in selector:
            continue
        outlines = [v.strip() for v in re.findall(r"(?<![\w-])outline\s*:\s*([^;]+)", body)]
        if outlines and all(v in ("none", "0") for v in outlines) and "box-shadow" not in body:
            findings.append(Finding(path, offset + line_of(text, m.start(2)), "a11y-focus-outline-none",
                                    selector.strip().splitlines()[-1].strip()[:60]))

    m = re.search(r"animation[^;{}]*\binfinite\b", text)
    if m and "prefers-reduced-motion" not in text:
        findings.append(Finding(path, offset + line_of(text, m.start()), "a11y-motion-no-reduced-motion"))


def scan_css_duplicates(path, lines, findings, offset=0):
    """A run of DUP_RUN lines that already appeared earlier in the file.

    An edit to the first copy of a property both copies declare is overridden
    by the second, silently. Whole-line comparison after stripping indentation;
    a window has to hold at least ten distinct non-blank lines so a stretch of
    closing braces and blank lines never counts.
    """
    stripped = [ln.strip() for ln in lines]
    seen = {}
    i = 0
    while i + DUP_RUN <= len(stripped):
        window = tuple(stripped[i:i + DUP_RUN])
        if len({w for w in window if w}) < 10:
            i += 1
            continue
        first = seen.setdefault(window, i)
        if first + DUP_RUN <= i:
            j = i + DUP_RUN
            while j < len(stripped) and first + (j - i) < i and stripped[j] == stripped[first + (j - i)]:
                j += 1
            findings.append(Finding(path, offset + i + 1, "css-duplicate-block",
                                    f"{j - i} lines repeat lines {offset + first + 1}–{offset + first + (j - i)}"))
            i = j
            continue
        i += 1


# ---------------------------------------------------------------------------
# Liquid
# ---------------------------------------------------------------------------
STYLE_BLOCK_RE = re.compile(
    r"(\{%-?\s*style(?:sheet)?\s*-?%\}|<style[^>]*>)(.*?)(\{%-?\s*endstyle(?:sheet)?\s*-?%\}|</style>)", re.S)
SCHEMA_RE = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.S)
COMMENT_RE = re.compile(r"\{%-?\s*comment\s*-?%\}(.*?)\{%-?\s*endcomment\s*-?%\}", re.S)
# `'{{ amount }}'` inside a tag: a string literal that contains an output tag.
OUTPUT_IN_STRING_RE = re.compile(r"\{%-?[^%]*?(['\"])[^'\"\n]*\{\{[^'\"\n]*\1", re.S)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*\basset_url\b[^>]*>", re.I)


def parse_json_tolerant(raw):
    """Shopify tolerates trailing commas and /* */ comments; strict json does not."""
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", raw))
    except json.JSONDecodeError:
        return None


_LOCALES = {}


def locale(path):
    """The parsed locale file, or None when it is absent or unparsable."""
    if path not in _LOCALES:
        text = read(path)
        _LOCALES[path] = parse_json_tolerant(text) if text else None
    return _LOCALES[path]


def key_exists(tree, key):
    node = tree
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def scan_schema_t_keys(path, text, findings, offset=0):
    """Every `t:` value in a schema must resolve in the schema locale.

    The contract check verifies the SHAPE of a label — that it is a `t:` key
    and not bare English. A key with a typo, a key for a section that was
    renamed, and a key nobody added all read as correct to it, and none shows
    until a merchant opens the theme editor (Pique, Sep 2026, three sections).
    """
    tree = locale(LOCALE_SCHEMA)
    if not isinstance(tree, dict):
        return
    for m in re.finditer(r'"t:([A-Za-z0-9_.\-]+)"', text):
        if not key_exists(tree, m.group(1)):
            findings.append(Finding(path, offset + line_of(text, m.start()), "schema-t-key-missing", m.group(1)))


T_FILTER_RE = re.compile(r"""(['"])([A-Za-z0-9_.\-]+)\1\s*\|\s*t\b""")


def scan_runtime_t_keys(path, text, findings):
    """Every literal `'key' | t` must resolve in the runtime locale.

    Only a string literal directly before `| t` is checked; a key built with
    `append` is skipped rather than reported, so a runtime-composed key never
    cries wolf. Liquid comments and the schema block are blanked first.
    """
    tree = locale(LOCALE_RUNTIME)
    if not isinstance(tree, dict):
        return
    blanked = COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    blanked = SCHEMA_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), blanked)
    for m in T_FILTER_RE.finditer(blanked):
        if not key_exists(tree, m.group(2)):
            findings.append(Finding(path, line_of(blanked, m.start()), "liquid-t-key-missing", m.group(2)))


def scan_schema(path, text, findings):
    m = SCHEMA_RE.search(text)
    if not m:
        return
    offset = line_of(text, m.start())
    scan_schema_t_keys(path, m.group(1), findings, offset=offset - 1)
    schema = parse_json_tolerant(m.group(1))
    if not isinstance(schema, dict):
        return

    def walk(settings, where, section_level):
        products = []
        for s in settings or []:
            if not isinstance(s, dict):
                continue
            if s.get("type") == "range":
                try:
                    lo, hi, step = float(s.get("min", 0)), float(s.get("max", 0)), float(s.get("step", 1))
                except (TypeError, ValueError):
                    continue
                if step <= 0 or (hi - lo) / step < 3:
                    findings.append(Finding(path, offset, "schema-range-steps",
                                            f'id "{s.get("id")}" min {s.get("min")} max {s.get("max")} step {s.get("step", 1)}'))
            if s.get("type") == "product":
                products.append(str(s.get("id")))
            # Only the two types Shopify has been seen to reject (Pique, Sep
            # 2026). Other resource pickers were not tested; do not widen this
            # on a guess — a check that fails valid code is switched off.
            if s.get("type") in ("article_list", "blog") and "visible_if" in s:
                findings.append(Finding(path, offset, "schema-visible-if-resource",
                                        f'{where}: id "{s.get("id")}" ({s.get("type")})'))
        # Section-level only. Base's shop-the-look block carries four product
        # settings and uploads; Pique's rejection was in the section's own
        # settings array, and moving the picker into a block was the fix.
        if section_level and len(products) > 1:
            findings.append(Finding(path, offset, "schema-product-setting-twice",
                                    f'{where}: ids {", ".join(products)}'))

    walk(schema.get("settings"), "section settings", True)
    for b in schema.get("blocks") or []:
        if isinstance(b, dict):
            walk(b.get("settings"), f'block "{b.get("type")}"', False)


def scan_liquid(path, text, findings):
    in_sections_or_snippets = path.startswith(("sections/", "snippets/"))

    for m in STYLE_BLOCK_RE.finditer(text):
        scan_css(path, m.group(2), findings, offset=line_of(text, m.start(2)) - 1,
                 hex_check=path not in TOKEN_FILES)

    if in_sections_or_snippets:
        for m in re.finditer(r"\{%-?\s*(stylesheet|javascript)\s*-?%\}", text):
            findings.append(Finding(path, line_of(text, m.start()), "liquid-stylesheet-tag"))
        for m in SCRIPT_TAG_RE.finditer(text):
            if 'type="module"' not in m.group(0) and "type='module'" not in m.group(0):
                findings.append(Finding(path, line_of(text, m.start()), "liquid-script-not-module"))

    for m in re.finditer(r"DOMContentLoaded", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-domcontentloaded"))
    for m in re.finditer(r"\bjQuery\b|(?<![\w$.])\$\(", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-jquery"))
    scan_js_cart_requests(path, text, findings)

    for m in OUTPUT_IN_STRING_RE.finditer(text):
        findings.append(Finding(path, line_of(text, m.start()), "liquid-output-in-string"))
    for m in COMMENT_RE.finditer(text):
        if re.search(r"\{%-?\s*raw\s*-?%\}", m.group(1)):
            findings.append(Finding(path, line_of(text, m.start()), "liquid-raw-in-comment"))

    if path.startswith(("sections/", "blocks/", "snippets/")):
        scan_runtime_t_keys(path, text, findings)
    if path.startswith(("sections/", "blocks/", "snippets/", "layout/")):
        scan_markup_a11y(path, text, findings)
    if path.startswith(("sections/", "blocks/")):
        scan_schema(path, text, findings)


DIV_AS_BUTTON_RE = re.compile(
    r"""<(?:div|span|li|p)\b[^>]*?(?:\sonclick=|\srole=["']button["']|\s@click|\sx-on:click)""", re.I)
A_NO_HREF_CLICK_RE = re.compile(r"""<a\b(?![^>]*\bhref=)[^>]*?(?:\sonclick=|\s@click|\sx-on:click)""", re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.S)
METAFIELD_ATTR_RE = re.compile(r"""=\s*(["'])\s*\{\{([^}]*\bmetafields\b[^}]*)\}\}\s*\1""")
SAFE_FILTERS_RE = re.compile(r"\|\s*(escape|escape_once|image_url|file_url|url|asset_url|metafield_tag|strip_html|handleize|json|img_url)\b")


def blank_liquid_prose(text):
    """Liquid comments and the schema block, blanked with line breaks kept."""
    text = COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return SCHEMA_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def scan_markup_a11y(path, text, findings):
    """The markup findings GitBot raises as Critical or Major (accessibility.md
    sections 1, 2, 5 and 11). Each is decidable from the tag alone."""
    body = blank_liquid_prose(text)
    for rx in (DIV_AS_BUTTON_RE, A_NO_HREF_CLICK_RE):
        for m in rx.finditer(body):
            findings.append(Finding(path, line_of(body, m.start()), "a11y-div-as-button",
                                    re.sub(r"\s+", " ", m.group(0))[:50]))
    for m in IMG_RE.finditer(body):
        if not re.search(r"\salt\s*=", m.group(0)):
            findings.append(Finding(path, line_of(body, m.start()), "a11y-img-no-alt"))
    for m in METAFIELD_ATTR_RE.finditer(body):
        if not SAFE_FILTERS_RE.search(m.group(2)):
            findings.append(Finding(path, line_of(body, m.start()), "security-unescaped-metafield-attr",
                                    m.group(2).strip()[:60]))


# A cart URL inside a request call — fetch(), XMLHttpRequest.open(), axios,
# $.ajax — on the same statement. A cart URL in a selector string
# (`[action*="/cart/add"]`, the engine's own delegation) is not a request.
RAW_CART_RE = re.compile(
    r"""(?:\bfetch\s*\(|\.open\s*\(\s*['"`][A-Z]+['"`]\s*,|\baxios\s*[.(]|\$\.(?:ajax|post|get)\s*\()[^;]{0,160}?cart/(add|change|clear|update)(?:\.js)?\b""")


def scan_js_cart_requests(path, text, findings):
    if path == "assets/cart.js":
        return
    for m in RAW_CART_RE.finditer(text):
        rule = "js-raw-cart-update" if m.group(1) == "update" else "js-raw-cart-request"
        findings.append(Finding(path, line_of(text, m.start()), rule, f"cart/{m.group(1)}"))


def scan_js(path, text, findings):
    scan_js_cart_requests(path, text, findings)
    for m in DIV_AS_BUTTON_RE.finditer(text):
        findings.append(Finding(path, line_of(text, m.start()), "a11y-div-as-button",
                                re.sub(r"\s+", " ", m.group(0))[:50]))
    for m in re.finditer(r"DOMContentLoaded", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-domcontentloaded"))
    for m in re.finditer(r"\bjQuery\b|(?<![\w$.])\$\(", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-jquery"))


def scan_template_json(path, text, findings):
    for m in re.finditer(r':\s*"t:[^"]*"', text):
        findings.append(Finding(path, line_of(text, m.start()), "template-t-key", m.group(0).strip()))


_SCHEMA_IDS = {}


def schema_ids(section_type):
    """(setting ids, {block type: setting ids}) for sections/<type>.liquid,
    or None when the section or its schema cannot be read."""
    path = f"sections/{section_type}.liquid"
    if path not in _SCHEMA_IDS:
        result = None
        text = read(path)
        m = SCHEMA_RE.search(text) if text else None
        schema = parse_json_tolerant(m.group(1)) if m else None
        if isinstance(schema, dict):
            ids = {s.get("id") for s in schema.get("settings") or [] if isinstance(s, dict)}
            blocks = {}
            for b in schema.get("blocks") or []:
                if isinstance(b, dict):
                    blocks[b.get("type")] = {s.get("id") for s in b.get("settings") or [] if isinstance(s, dict)}
            result = (ids, blocks)
        _SCHEMA_IDS[path] = result
    return _SCHEMA_IDS[path]


def scan_template_settings(path, text, findings):
    """A template key its section's schema does not define is dropped on upload.

    Shopify validates a template against the schema the store holds at that
    moment; `theme dev` syncs files in watcher order, so a new setting and its
    template value in one change lose the value silently when the template
    goes up first (Pique, twice). A typo in a key is the same finding.
    """
    data = parse_json_tolerant(text)
    if not isinstance(data, dict):
        return

    def line_of_id(ident):
        m = re.search(r'"%s"\s*:' % re.escape(ident), text)
        return line_of(text, m.start()) if m else 1

    for sid, sec in (data.get("sections") or {}).items():
        if not isinstance(sec, dict):
            continue
        stype = str(sec.get("type", ""))
        if not stype or stype.startswith("shopify://"):
            continue
        known = schema_ids(stype)
        if known is None:
            continue
        ids, blocks = known
        unknown = [k for k in (sec.get("settings") or {}) if k not in ids]
        if unknown:
            findings.append(Finding(path, line_of_id(sid), "template-setting-unknown",
                                    f'section "{sid}" ({stype}): {", ".join(unknown)}'))
        for bid, blk in (sec.get("blocks") or {}).items():
            if not isinstance(blk, dict):
                continue
            btype = str(blk.get("type", ""))
            if btype.startswith("shopify://") or btype in ("@app", "@theme"):
                continue
            if btype not in blocks:
                # A theme block from blocks/ or an app block the section
                # accepts wholesale; its settings live elsewhere.
                if "@theme" in blocks or "@app" in blocks:
                    continue
                findings.append(Finding(path, line_of_id(bid), "template-setting-unknown",
                                        f'block "{bid}": type "{btype}" is not in the {stype} schema'))
                continue
            unknown = [k for k in (blk.get("settings") or {}) if k not in blocks[btype]]
            if unknown:
                findings.append(Finding(path, line_of_id(bid), "template-setting-unknown",
                                        f'block "{bid}" ({btype}): {", ".join(unknown)}'))


def scan_docs_orphans(deleted, findings, sweep=False):
    """A docs page for a section or snippet that no longer exists.

    Pure filename arithmetic: docs/sections/x.md needs sections/x.liquid.
    Reported for the files this change deletes, or for every orphan on a
    sweep. Four consecutive Pique pull requests left such pages behind; each
    was caught by a reviewer reading docs/ against the diff, never by a check.
    """
    for kind in ("sections", "snippets"):
        for page in sorted(glob.glob(f"docs/{kind}/*.md")):
            src = f"{kind}/{os.path.basename(page)[:-3]}.liquid"
            if os.path.exists(src):
                continue
            if sweep or src in deleted:
                findings.append(Finding(page, 1, "docs-orphan-page", f"{src} does not exist"))


def scan_file(path, findings):
    text = read(path)
    if text is None:
        return
    if path.endswith(".css"):
        # Every stylesheet the theme wrote, not only section-*/component-*:
        # GitBot reports a hex anywhere (cart.css, critical.css included).
        scan_css(path, text, findings, hex_check=not re.search(r"(\.min\.|swiper|alpine)", path))
    elif path.endswith(".liquid"):
        scan_liquid(path, text, findings)
    elif path.endswith(".js") and path.startswith("assets/") and not re.search(r"(\.min\.js|@|swiper|alpine)", path):
        scan_js(path, text, findings)
    elif path.startswith("templates/") and path.endswith(".json"):
        scan_template_json(path, text, findings)
        scan_template_settings(path, text, findings)
    elif path.startswith("sections/") and path.endswith(".json"):
        scan_template_settings(path, text, findings)
    elif path == "config/settings_schema.json":
        scan_schema_t_keys(path, text, findings)


# ---------------------------------------------------------------------------
# cross-file: a section-* asset loaded by more than one section
# ---------------------------------------------------------------------------
def scan_shared_section_assets(checked, findings):
    referrers = {}
    try:
        sections = [p for p in git("ls-files", "sections").split("\n") if p.endswith(".liquid")]
    except subprocess.CalledProcessError:
        return
    for sec in sections + [p for p in checked if p.startswith("sections/") and p not in sections]:
        text = read(sec)
        if text is None:
            continue
        for m in re.finditer(r"['\"](section-[a-z0-9-]+\.(?:css|js))['\"]", text):
            referrers.setdefault(m.group(1), set()).add(sec)
    for asset, secs in referrers.items():
        if len(secs) < 2:
            continue
        for sec in sorted(secs):
            if sec in checked:
                others = ", ".join(sorted(secs - {sec}))
                findings.append(Finding(sec, 1, "section-asset-shared", f"{asset} also loaded by {others}"))


# ---------------------------------------------------------------------------
# file selection
# ---------------------------------------------------------------------------
def file_sets(mode):
    """Return (new, modified, deleted) as sets of theme paths for the given mode."""
    new, mod, gone = set(), set(), set()
    if mode == "staged":
        status = git("diff", "--cached", "--name-status", "--diff-filter=ACDMR")
        for line in status.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            (gone if parts[0].startswith("D") else new if parts[0].startswith("A") else mod).add(parts[-1])
    elif mode == "changed":
        new = {p for p in git("ls-files", "--others", "--exclude-standard").split("\n") if p}
        for line in git("diff", "--name-status", "HEAD").splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            (gone if parts[0].startswith("D") else new if parts[0].startswith("A") else mod).add(parts[-1])
        mod -= new
    elif mode == "all":
        mod = {p for p in git("ls-files").split("\n") if p}
    else:
        return set(), set(), set()
    return ({p for p in new if is_theme_file(p)}, {p for p in mod if is_theme_file(p)},
            {p for p in gone if is_theme_file(p)})


def main(argv):
    os.chdir(repo_root())
    quiet = "--quiet" in argv
    block = "--block" in argv
    verbose = "--verbose" in argv

    if "--files" in argv:
        paths = [a for a in argv[argv.index("--files") + 1:] if not a.startswith("--")]
        paths = [os.path.normpath(p) for p in paths]
        new, mod, gone = set(), {p for p in paths if is_theme_file(p) and os.path.exists(p)}, set()
        mode = "files"
    else:
        mode = next((m for m in ("staged", "changed", "all") if f"--{m}" in argv), None)
        if mode is None:
            print(__doc__)
            return 2
        new, mod, gone = file_sets(mode)
        if mode == "all" and block:
            new, mod = new | mod, set()
        if mode == "staged":
            block = True

    checked = new | mod
    if not checked and not gone:
        return 0

    findings = []
    for p in sorted(checked):
        scan_file(p, findings)
    scan_shared_section_assets(checked, findings)
    scan_docs_orphans(gone, findings, sweep=(mode == "all"))

    if not findings:
        if verbose and not quiet:
            print(f"Conventions OK ({len(checked)} file(s) checked).")
        return 0

    blocking = [f for f in findings if f.severity == "error" and f.path in new]
    findings.sort(key=lambda f: (f.path, SEVERITY_ORDER[f.severity], f.line))

    by_file = {}
    for f in findings:
        by_file.setdefault(f.path, []).append(f)

    if blocking:
        print()
        print("=" * 74)
        print(f"  BLOCKED — {len(blocking)} convention error(s) in new file(s)")
        print("=" * 74)
    for path, items in by_file.items():
        tag = "NEW" if path in new else "modified — reported, not gated"
        print(f"  {path}  [{tag}]")
        for f in items:
            sev, why, rule = RULES[f.rule]
            marker = "error" if sev == "error" else "warn "
            detail = f"  ({f.detail})" if f.detail else ""
            print(f"    {marker}  :{f.line:<5} {f.rule}{detail}")
            print(f"           {why}  — .claude/rules/{rule}")
    errors = sum(1 for f in findings if f.severity == "error")
    warns = len(findings) - errors
    print()
    print(f"  Conventions: {errors} error(s) ({len(blocking)} blocking), {warns} warning(s), "
          f"{len(by_file)} file(s).")
    if blocking:
        print("  A finding blocks only in a file this change ADDS. Fix it, or if the rule is")
        print("  wrong for this theme, say so in the rule file rather than working around it.")
    print()
    return 1 if (blocking and block) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
