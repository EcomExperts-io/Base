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
  --block              with --changed or --all, exit 1 on blocking findings
  --quiet              print nothing when there is nothing to say
"""

import json
import os
import re
import subprocess
import sys

THEME_DIRS = ("sections/", "snippets/", "assets/", "layout/", "templates/",
              "locales/", "config/", "blocks/")

# Files whose whole job is to define raw values. Hex is not a finding there.
TOKEN_FILES = {"snippets/css-variables.liquid", "config/settings_schema.json",
               "config/settings_data.json"}

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
}

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
def scan_css(path, text, findings, offset=0, hex_check=True):
    for m in re.finditer(r"@media[^{]*max-width", text):
        findings.append(Finding(path, offset + line_of(text, m.start()), "css-max-width-query"))

    if hex_check:
        # Only a hex in a property VALUE counts — `#product-grid` is an id selector.
        for m in re.finditer(r":[^;{}\n]*?(#[0-9a-fA-F]{3,8})\b", text):
            snippet = text[max(0, m.start() - 40):m.end()]
            if "url(" in snippet:
                continue
            findings.append(Finding(path, offset + line_of(text, m.start(1)), "css-raw-hex", m.group(1)))

    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if "!important" in ln:
            prev = lines[i - 1] if i else ""
            if "/*" not in ln and "/*" not in prev and "//" not in ln:
                findings.append(Finding(path, offset + i + 1, "css-important"))


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


def scan_schema_ranges(path, text, findings):
    m = SCHEMA_RE.search(text)
    if not m:
        return
    schema = parse_json_tolerant(m.group(1))
    if not isinstance(schema, dict):
        return
    offset = line_of(text, m.start())

    def walk(settings):
        for s in settings or []:
            if not isinstance(s, dict) or s.get("type") != "range":
                continue
            try:
                lo, hi, step = float(s.get("min", 0)), float(s.get("max", 0)), float(s.get("step", 1))
            except (TypeError, ValueError):
                continue
            if step <= 0 or (hi - lo) / step < 3:
                findings.append(Finding(path, offset, "schema-range-steps",
                                        f'id "{s.get("id")}" min {s.get("min")} max {s.get("max")} step {s.get("step", 1)}'))

    walk(schema.get("settings"))
    for b in schema.get("blocks") or []:
        if isinstance(b, dict):
            walk(b.get("settings"))


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

    for m in OUTPUT_IN_STRING_RE.finditer(text):
        findings.append(Finding(path, line_of(text, m.start()), "liquid-output-in-string"))
    for m in COMMENT_RE.finditer(text):
        if re.search(r"\{%-?\s*raw\s*-?%\}", m.group(1)):
            findings.append(Finding(path, line_of(text, m.start()), "liquid-raw-in-comment"))

    if path.startswith(("sections/", "blocks/")):
        scan_schema_ranges(path, text, findings)


def scan_js(path, text, findings):
    for m in re.finditer(r"DOMContentLoaded", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-domcontentloaded"))
    for m in re.finditer(r"\bjQuery\b|(?<![\w$.])\$\(", text):
        findings.append(Finding(path, line_of(text, m.start()), "js-jquery"))


def scan_template_json(path, text, findings):
    for m in re.finditer(r':\s*"t:[^"]*"', text):
        findings.append(Finding(path, line_of(text, m.start()), "template-t-key", m.group(0).strip()))


def scan_file(path, findings):
    text = read(path)
    if text is None:
        return
    if path.endswith(".css"):
        scan_css(path, text, findings, hex_check=path not in TOKEN_FILES
                 and bool(re.match(r"assets/(section|component)-", path)))
    elif path.endswith(".liquid"):
        scan_liquid(path, text, findings)
    elif path.endswith(".js") and path.startswith("assets/") and not re.search(r"(\.min\.js|@|swiper|alpine)", path):
        scan_js(path, text, findings)
    elif path.startswith("templates/") and path.endswith(".json"):
        scan_template_json(path, text, findings)


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
    """Return (new, modified) as sets of theme paths for the given mode."""
    if mode == "staged":
        status = git("diff", "--cached", "--name-status", "--diff-filter=ACMR")
        new, mod = set(), set()
        for line in status.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            (new if parts[0].startswith("A") else mod).add(parts[-1])
    elif mode == "changed":
        new = {p for p in git("ls-files", "--others", "--exclude-standard").split("\n") if p}
        mod = set()
        for line in git("diff", "--name-status", "HEAD").splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            (new if parts[0].startswith("A") else mod).add(parts[-1])
        mod -= new
    elif mode == "all":
        new, mod = set(), {p for p in git("ls-files").split("\n") if p}
    else:
        return set(), set()
    return {p for p in new if is_theme_file(p)}, {p for p in mod if is_theme_file(p)}


def main(argv):
    os.chdir(repo_root())
    quiet = "--quiet" in argv
    block = "--block" in argv
    verbose = "--verbose" in argv

    if "--files" in argv:
        paths = [a for a in argv[argv.index("--files") + 1:] if not a.startswith("--")]
        paths = [os.path.normpath(p) for p in paths]
        new, mod = set(), {p for p in paths if is_theme_file(p) and os.path.exists(p)}
        mode = "files"
    else:
        mode = next((m for m in ("staged", "changed", "all") if f"--{m}" in argv), None)
        if mode is None:
            print(__doc__)
            return 2
        new, mod = file_sets(mode)
        if mode == "all" and block:
            new, mod = new | mod, set()
        if mode == "staged":
            block = True

    checked = new | mod
    if not checked:
        return 0

    findings = []
    for p in sorted(checked):
        scan_file(p, findings)
    scan_shared_section_assets(checked, findings)

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
