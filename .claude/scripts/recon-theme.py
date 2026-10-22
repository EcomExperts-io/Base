#!/usr/bin/env python3
"""Measure a theme before touching it — lineage, conventions, compliance, what is left.

Writes the answers to docs/ai-workflow/state-of-the-theme.md (or stdout). The
/recon-theme skill reads the result and copies the measured conventions into
the fork's rules. Where the fork's convention and Base's rule disagree, the
fork's wins in the fork.

Usage
-----
  python3 .claude/scripts/recon-theme.py [--base-path ../Base | --ref base/development]
                                         [--live-url https://www.example.com] [--stdout] [--json]

--live-url adds the live feature inventory: what the published storefront
loads that the theme code does not show — app embeds, tracking pixels, popup
and chat scripts, markets, a page builder, rich-text metafield HTML.
Base is read from --base-path, else the worktree recorded by base-link.sh,
else the `base` remote. Without any, the lineage section is skipped.
"""

import collections
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

THEME_DIRS = ("sections", "snippets", "assets", "templates", "layout", "locales", "config", "blocks")
OUT = "docs/ai-workflow/state-of-the-theme.md"


def sh(*args, cwd=None):
    r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    return r.stdout if r.returncode == 0 else ""


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def tracked():
    return [p for p in sh("git", "ls-files").split("\n") if p]


# ---------------------------------------------------------------------------
# Base source
# ---------------------------------------------------------------------------
class Base:
    def __init__(self, argv):
        self.kind, self.where = None, None
        if "--base-path" in argv:
            self.kind, self.where = "path", argv[argv.index("--base-path") + 1]
        else:
            try:
                wt = json.load(open(".claude/.cache/base-link.json"))["worktree"]
                if os.path.isdir(wt):
                    self.kind, self.where = "path", wt
            except (OSError, json.JSONDecodeError, KeyError):
                pass
            if not self.kind and sh("git", "remote", "get-url", "base").strip():
                ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "base/development"
                if sh("git", "rev-parse", "--verify", ref).strip():
                    self.kind, self.where = "ref", ref
        self.sha = None
        if self.kind == "path":
            self.sha = sh("git", "rev-parse", "HEAD", cwd=self.where).strip()[:9]
        elif self.kind == "ref":
            self.sha = sh("git", "rev-parse", self.where).strip()[:9]

    def files(self):
        if self.kind == "path":
            out = sh("git", "ls-files", cwd=self.where)
        elif self.kind == "ref":
            out = sh("git", "ls-tree", "-r", "--name-only", self.where)
        else:
            return []
        return [p for p in out.split("\n") if p and p.startswith(tuple(d + "/" for d in THEME_DIRS))]

    def read(self, path):
        if self.kind == "path":
            return read(os.path.join(self.where, path))
        if self.kind == "ref":
            return sh("git", "show", f"{self.where}:{path}")
        return ""


# ---------------------------------------------------------------------------
# measurements
# ---------------------------------------------------------------------------
def lineage(base, fork_files):
    base_files = set(base.files())
    fork_set = set(p for p in fork_files if p.startswith(tuple(d + "/" for d in THEME_DIRS)))
    out = {}
    for d in THEME_DIRS:
        b = {p for p in base_files if p.startswith(d + "/")}
        f = {p for p in fork_set if p.startswith(d + "/")}
        unchanged = modified = 0
        for p in sorted(b & f):
            if read(p) == base.read(p):
                unchanged += 1
            else:
                modified += 1
        out[d] = {"unchanged": unchanged, "modified": modified,
                  "deleted": sorted(b - f), "new": sorted(f - b)}
    return out


def breakpoints(files):
    mins, maxs = collections.Counter(), collections.Counter()
    for p in files:
        if not p.endswith((".css", ".liquid")):
            continue
        text = read(p)
        for m in re.finditer(r"min-width:\s*(\d+)px", text):
            mins[int(m.group(1))] += 1
        for m in re.finditer(r"max-width:\s*(\d+)px", text):
            maxs[int(m.group(1))] += 1
    return {"min_width": mins.most_common(6), "max_width": maxs.most_common(6)}


def container_classes(files):
    c = collections.Counter()
    for p in files:
        if not (p.startswith(("sections/", "snippets/")) and p.endswith(".liquid")):
            continue
        for m in re.finditer(r'class="([^"]*)"', read(p)):
            for cls in m.group(1).split():
                if (re.search(r"(page-width|container|wrapper|inner|content-width|max-width)", cls)
                        and "{" not in cls
                        and not re.search(r"(svg|swiper|spinner|filter|overlay|icon|badge|info-wrapper)", cls)):
                    c[cls] += 1
    return c.most_common(8)


def units(files):
    px = rem = 0
    for p in files:
        if re.match(r"assets/(section|component)-[^/]+\.css$", p):
            text = read(p)
            px += len(re.findall(r"\b\d+(?:\.\d+)?px\b", text))
            rem += len(re.findall(r"\b\d+(?:\.\d+)?rem\b", text))
    return {"px": px, "rem": rem}


def liquiddoc_forms(files):
    a = b = 0
    for p in files:
        if p.startswith("snippets/") and p.endswith(".liquid"):
            text = read(p)
            a += len(re.findall(r"@param\s+\{[^}]+\}\s+\[?\w+\]?\s+-", text))
            b += len(re.findall(r"@param\s+\w+\s+\{", text))
    return {"@param {type} name - description": a, "@param name {type}": b}


def custom_elements(files):
    defined, used = set(), collections.Counter()
    for p in files:
        if p.startswith("assets/") and p.endswith(".js"):
            defined.update(re.findall(r"customElements\.define\(\s*['\"]([a-z][a-z0-9-]*)['\"]", read(p)))
    for p in files:
        if p.endswith(".liquid"):
            for tag in re.findall(r"<([a-z][a-z0-9]*-[a-z0-9-]+)[\s>]", read(p)):
                used[tag] += 1
    undefined = sorted(t for t in used if t not in defined and not t.startswith(("x-", "swiper-")))
    return {"defined": sorted(defined), "used_but_undefined": undefined}


def section_css_loading(files):
    stylesheet_tag = legacy_tag = inline_style = 0
    for p in files:
        if p.startswith("sections/") and p.endswith(".liquid"):
            text = read(p)
            stylesheet_tag += bool(re.search(r"asset_url\s*\|\s*stylesheet_tag", text))
            legacy_tag += bool(re.search(r"\{%-?\s*stylesheet\s*-?%\}", text))
            inline_style += bool(re.search(r"\{%-?\s*style\s*-?%\}|<style", text))
    return {"stylesheet_tag": stylesheet_tag, "legacy_stylesheet_tag": legacy_tag, "inline_style_block": inline_style}


def compliance():
    spec = importlib.util.spec_from_file_location("rc", ".claude/scripts/report-compliance.py")
    if spec is None or not os.path.exists(".claude/scripts/report-compliance.py"):
        return None
    try:
        rc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rc)
        contract = rc.load_contract()
        rows = [rc.audit(p, read(p), contract) for p in sorted(
            p for p in os.listdir("sections") if p.endswith(".liquid")) for p in [os.path.join("sections", p)]]
        t = rc.tally(rows)
        violators = sorted(r["path"] for r in rows if r["status"] == "violation")
        return {"tally": t, "violators": violators}
    except Exception as e:  # noqa: BLE001 — a recon must not die on a report bug
        return {"error": str(e)}


def pages(files):
    templates = sorted(p for p in files if p.startswith("templates/") and p.endswith(".json"))
    page_templates = [os.path.basename(p)[len("page."):-5] for p in templates
                      if os.path.basename(p).startswith("page.") and os.path.basename(p) != "page.json"]
    section_types = collections.Counter()
    for p in templates:
        raw = re.sub(r"/\*.*?\*/", "", read(p), flags=re.S)
        for m in re.finditer(r'"type"\s*:\s*"([a-z0-9-]+)"', raw):
            section_types[m.group(1)] += 1
    sections = {os.path.basename(p)[:-7] for p in files if p.startswith("sections/") and p.endswith(".liquid")}
    unused = sorted(s for s in sections if s not in section_types and not s.startswith(("header", "footer", "announcement", "predictive", "pickup")))
    return {"templates": [os.path.basename(p) for p in templates], "page_templates": page_templates,
            "sections_in_no_template": unused}


def tooling():
    out = {"claude_rules": len([p for p in os.listdir(".claude/rules") if p.endswith(".md")]) if os.path.isdir(".claude/rules") else 0,
           "cursor_rules": len([p for p in os.listdir(".cursor/rules") if p.endswith(".mdc")]) if os.path.isdir(".cursor/rules") else 0,
           "hooks": ("husky" if os.path.isdir(".husky") else "") + (" .githooks" if os.path.isdir(".githooks") else ""),
           "hooks_path": sh("git", "config", "core.hooksPath").strip(),
           "runtime_hooks": bool(json.loads(read(".claude/settings.json") or "{}").get("hooks")) if os.path.exists(".claude/settings.json") else False,
           "ci": sorted(os.listdir(".github/workflows")) if os.path.isdir(".github/workflows") else [],
           "stamp": json.loads(read(".base-version") or "null") if os.path.exists(".base-version") else None,
           "frame_map": os.path.exists("docs/ai-workflow/reference-map.md") or os.path.exists("docs/ai-workflow/figma-frame-map.md"),
           "incidents": len([p for p in os.listdir("docs/ai-workflow/incidents") if p.endswith(".md") and p != "README.md"]) if os.path.isdir("docs/ai-workflow/incidents") else 0}
    if os.path.exists(".claude/scripts/check-tooling-drift.py") and out["stamp"]:
        out["drift"] = sh(sys.executable, ".claude/scripts/check-tooling-drift.py", "--brief", "--no-fetch").strip()
    return out


# ---------------------------------------------------------------------------
# live feature inventory — what the published storefront loads
# ---------------------------------------------------------------------------
# Vendor fingerprints, by what they do to a build. A match is a name in the
# report, not a verdict; the skill says what each class means for the work.
VENDORS = {
    "tracking": [
        ("Google Tag Manager", r"googletagmanager\.com/gtm"), ("GA4 / gtag", r"gtag\(|googletagmanager\.com/gtag"),
        ("Meta pixel", r"connect\.facebook\.net|fbq\("), ("TikTok", r"analytics\.tiktok\.com|ttq\.load"),
        ("Pinterest", r"ct\.pinterest\.com|pintrk"), ("Snap", r"sc-static\.net|snaptr\("),
        ("Klaviyo", r"klaviyo\.com|klaviyo\.js"), ("Hotjar", r"hotjar\.com"), ("Microsoft Clarity", r"clarity\.ms"),
        ("Northbeam", r"northbeam"), ("Triple Whale", r"triplewhale"), ("Elevar", r"elevar"),
        ("Attentive", r"attn\.tv"), ("Postscript", r"postscript\.io"), ("Shopify Web Pixels", r"web-pixels-manager"),
    ],
    "popups and chat": [
        ("Klaviyo forms", r"klaviyo.*(forms|onsite)"), ("Justuno", r"justuno"), ("Privy", r"privy\.com|privy-"),
        ("Alia", r"alia-root|alia\.app"), ("Wisepops", r"wisepops"), ("OptiMonk", r"optimonk"),
        ("Gorgias chat", r"gorgias"), ("Tidio", r"tidio"), ("Zendesk", r"zendesk|zopim"), ("Intercom", r"intercom"),
        ("Shopify Inbox", r"shopify-chat|inbox\.shopify"),
    ],
    "apps acting on the theme": [
        ("Recharge", r"rechargepayments|rechargeapps|recharge"), ("Skio", r"skio"), ("Loop subscriptions", r"loopwork|loopsubscriptions"),
        ("Rebuy", r"rebuyengine"), ("Yotpo", r"yotpo"), ("Judge.me", r"judge\.me"), ("Okendo", r"okendo"),
        ("Stamped", r"stamped\.io"), ("Loox", r"loox\.io"), ("Smile", r"smile\.io"), ("Bold", r"boldapps"),
        ("Globo", r"globosoftware|globo\."), ("Weglot", r"weglot"), ("Langify", r"langify"),
    ],
    "page builders": [
        ("Replo", r"replo"), ("Shogun", r"getshogun|shogun"), ("PageFly", r"pagefly"), ("GemPages", r"gempages"),
        ("Zipify", r"zipify"), ("Tapita", r"tapita"),
    ],
}


def inventory_html(html, url=""):
    """What one rendered storefront page says about the platform around the theme."""
    low = html.lower()
    out = {"url": url, "bytes": len(html), "vendors": {}, "counts": {}}
    for group, items in VENDORS.items():
        hits = [name for name, rx in items if re.search(rx, low)]
        out["vendors"][group] = hits
    scripts = re.findall(r"""<script\b[^>]*\bsrc=["']([^"']+)""", html, flags=re.I)
    out["counts"] = {
        "scripts": len(re.findall(r"<script\b", html, flags=re.I)),
        "external_scripts": len(scripts),
        "app_embeds": len([s for s in scripts if "/extensions/" in s or "cdn.shopify.com/extensions" in s]),
        "sections": len(re.findall(r'id="shopify-section-', html)),
        "inline_style_blocks": len(re.findall(r"<style\b", html, flags=re.I)),
        "inline_style_bytes": sum(len(m) for m in re.findall(r"<style\b[^>]*>(.*?)</style>", html, flags=re.I | re.S)),
        "rich_text_metafields": len(re.findall(r"metafield-rich_text_field", html)),
        "hreflang_alternates": len(re.findall(r'hreflang=', html, flags=re.I)),
        "localization_forms": len(re.findall(r'action="[^"]*/localization"|shopify-localization|localization-form', html)),
        "iframes": len(re.findall(r"<iframe\b", html, flags=re.I)),
    }
    m = re.search(r"Shopify\.theme\s*=\s*(\{[^}]*\})", html)
    out["theme"] = m.group(1)[:200] if m else None
    hosts = collections.Counter()
    for s in scripts:
        h = urllib.parse.urlsplit(s if "//" in s else "https:" + s if s.startswith("//") else "").netloc
        if h and "shopify" not in h:
            hosts[h] += 1
    out["third_party_script_hosts"] = hosts.most_common(15)
    return out


def live_inventory(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (recon-theme.py; Base tooling)",
                                               "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            final = r.geturl()
            html = r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"url": url, "error": str(e)}
    inv = inventory_html(html, url)
    inv["final_url"] = final
    inv["redirected"] = final.rstrip("/") != url.rstrip("/")
    return inv


def render_live(w, inv):
    w("## Live site inventory")
    w("")
    if not inv:
        w("Not measured — pass `--live-url https://www.<store>` to list what the published storefront loads: app embeds, pixels, popups, markets, a page builder. Each of those changes what a section must do, and none shows in the theme code.")
        w("")
        return
    if "error" in inv:
        w(f"`{inv['url']}` could not be fetched: {inv['error']}.")
        w("")
        return
    w(f"Fetched `{inv['url']}`" + (f" (redirected to `{inv['final_url']}` — the canonical host is the one to verify against)" if inv.get("redirected") else "") + f"; `Shopify.theme` {inv['theme'] or 'not found on the page'}.")
    w("")
    c = inv["counts"]
    w(f"- **Scripts:** {c['scripts']} total, {c['external_scripts']} external, {c['app_embeds']} app embeds (`/extensions/`); {c['iframes']} iframes. Third-party hosts: " + (", ".join(f"`{h}`×{n}" for h, n in inv["third_party_script_hosts"]) or "none") + ".")
    for group, hits in inv["vendors"].items():
        w(f"- **{group.capitalize()}:** " + (", ".join(hits) if hits else "none detected") + ".")
    w(f"- **Markets:** {c['hreflang_alternates']} hreflang alternates, {c['localization_forms']} localization form(s) — verify logged in and out in each market the store sells to.")
    w(f"- **Content outside sections:** {c['inline_style_blocks']} inline `<style>` blocks ({c['inline_style_bytes']:,} bytes) and {c['rich_text_metafields']} rich-text metafield wrappers on the page; a page-builder's HTML is a template to migrate, not a section to style.")
    w("")
    w("What each line means for the build: a subscription or review app that injects into the product form has to be switched off or driven by the section that replaces it (`javascript-standards.md`, Product forms); a popup paints over every capture and is hidden by `live-parity.py`; a page builder owns template names until admin is changed (`build-section-from-live` §3); tracking is the platform's and stays out of the theme (`storefront-infrastructure.md`).")
    w("")


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------
def render(d):
    L = []
    w = L.append
    w(f"# State of the theme — {d['repo']}")
    w("")
    w(f"Measured by `recon-theme.py` on {d['date']} at `{d['head']}`"
      + (f", against Base `{d['base']['sha']}` ({d['base']['kind']}: `{d['base']['where']}`)" if d["base"]["sha"] else ", with no Base to compare against") + ".")
    w("")
    w("Numbers first; judgment in `/recon-theme`. Where this theme's convention and Base's rule disagree, this theme's wins here — half the theme already uses it. Record the measured values in this repo's `.claude/rules/sections.md` and `snippets.md`, not Base's.")
    w("")
    if d.get("lineage"):
        w("## Lineage against Base")
        w("")
        w("| directory | unchanged | modified | deleted | new |")
        w("|---|---|---|---|---|")
        for dname, v in d["lineage"].items():
            w(f"| `{dname}/` | {v['unchanged']} | {v['modified']} | {len(v['deleted'])} | {len(v['new'])} |")
        w("")
        for dname in ("sections", "snippets"):
            v = d["lineage"][dname]
            if v["deleted"]:
                w(f"Deleted from Base's `{dname}/`: " + ", ".join(f"`{os.path.basename(p)}`" for p in v["deleted"]))
            if v["new"]:
                w(f"New in `{dname}/` ({len(v['new'])}): " + ", ".join(f"`{os.path.basename(p)}`" for p in v["new"][:40]) + (" …" if len(v["new"]) > 40 else ""))
        w("")
    w("## Measured conventions")
    w("")
    bp = d["breakpoints"]
    w("**Breakpoints** (occurrences across CSS and Liquid): min-width " + ", ".join(f"`{v}px`×{n}" for v, n in bp["min_width"]) + "; max-width " + (", ".join(f"`{v}px`×{n}" for v, n in bp["max_width"]) or "none") + ".")
    if bp["min_width"]:
        w(f"The majority min-width breakpoint is **`{bp['min_width'][0][0]}px`**. The rules say min-width only; every max-width above is a legacy query the conventions check reports.")
    w("")
    w("**Container classes** (by use in sections and snippets): " + ", ".join(f"`{c}`×{n}" for c, n in d["containers"]) + ".")
    w("")
    u = d["units"]
    w(f"**Units in section-* and component-* CSS:** `px`×{u['px']}, `rem`×{u['rem']} — the majority unit is "
      f"**{'px' if u['px'] >= u['rem'] else 'rem'}**; the parallel-build brief says px, so new work follows the majority here and says so if it differs.")
    w("")
    ld = d["liquiddoc"]
    w("**LiquidDoc form:** " + "; ".join(f"`{k}`×{v}" for k, v in ld.items()) + ".")
    w("")
    ce = d["custom_elements"]
    w(f"**Custom elements:** {len(ce['defined'])} defined in `assets/`. " + (f"Used in markup with no literal `customElements.define` (semantic tags, defined dynamically, or missing JS): " + ", ".join(f"`{t}`" for t in ce["used_but_undefined"][:12]) if ce["used_but_undefined"] else "Every tag used in markup has a definition."))
    w("")
    sc = d["section_css"]
    w(f"**How sections load CSS:** `stylesheet_tag` in {sc['stylesheet_tag']}, legacy `{{% stylesheet %}}` in {sc['legacy_stylesheet_tag']}, an inline style block in {sc['inline_style_block']}.")
    w("")
    w("## Compliance")
    w("")
    c = d["compliance"]
    if c and "tally" in c:
        t = c["tally"]
        w(f"**{t['compliant']}/{t['in_scope']}** sections meet the settings contract ({t['violations']} do not: {t['missing_padding']} missing padding, {t['missing_color_scheme']} missing color_scheme, {t['missing_presets']} missing presets). {t['bare_labels_total']} bare schema labels across {t['bare_label_sections']} sections.")
        if d.get("lineage"):
            new_secs = set(d["lineage"]["sections"]["new"])
            theirs = [p for p in c["violators"] if p in new_secs]
            w(f"Of the {len(c['violators'])} non-compliant sections, **{len(theirs)} were added by this build** (the rest are Base's legacy): " + ", ".join(f"`{os.path.basename(p)}`" for p in theirs[:30]) + ".")
    else:
        w("Compliance report unavailable" + (f": {c['error']}" if c and "error" in c else " — no report-compliance.py in this repo; pull the tooling first.") + ".")
    w("")
    w("## Pages and templates")
    w("")
    pg = d["pages"]
    w(f"{len(pg['templates'])} templates; page templates: " + (", ".join(f"`{p}`" for p in pg["page_templates"]) or "none") + ".")
    w("")
    w("A page template renders nothing until a page with that template exists in admin — confirm each against the store (`/store-recon`), and against the Figma frame map" + (" (a reference map exists under `docs/ai-workflow/`)" if d["tooling"]["frame_map"] else " (no reference map in this repo yet — one row per band: Figma node ids, live URL and section key, which is the reference)") + ".")
    if pg["sections_in_no_template"]:
        w("")
        w("Sections referenced by no template (built, unassigned, or dead): " + ", ".join(f"`{s}`" for s in pg["sections_in_no_template"][:40]) + ".")
    w("")
    render_live(w, d.get("live"))
    w("## Tooling")
    w("")
    t = d["tooling"]
    w(f"- `.claude/rules`: {t['claude_rules']} files; `.cursor/rules`: {t['cursor_rules']}; runtime hooks configured: {'yes' if t['runtime_hooks'] else 'no'}")
    w(f"- commit hooks: {t['hooks'].strip() or 'none'} (core.hooksPath = `{t['hooks_path'] or 'unset'}`)")
    w(f"- CI: " + (", ".join(f"`{c}`" for c in t["ci"]) or "none"))
    w(f"- Base tooling stamp: " + (f"`{t['stamp'].get('sha', '?')[:9]}` ({t['stamp'].get('date', '?')})" if t["stamp"] else "none — run `sh .claude/scripts/base-link.sh` then `python3 .claude/scripts/pull-base-tooling.py`"))
    if t.get("drift"):
        w(f"- {t['drift']}")
    w(f"- incidents recorded: {t['incidents']}")
    w("")
    w("## What the numbers cannot see")
    w("")
    w("Filled in by `/recon-theme`: the design system actually in use (tokens vs raw values), which Base components were generalised and how, what the previous team documented in the rules, which pages are half-built, and the three decisions to make before the next section is written.")
    return "\n".join(L) + "\n"


def main(argv):
    root = sh("git", "rev-parse", "--show-toplevel").strip()
    if not root:
        print("not a git repository")
        return 1
    os.chdir(root)
    files = tracked()
    base = Base(argv)
    d = {
        "repo": os.path.basename(root),
        "date": datetime.date.today().isoformat(),
        "head": sh("git", "rev-parse", "--short", "HEAD").strip(),
        "base": {"kind": base.kind, "where": base.where, "sha": base.sha},
        "lineage": lineage(base, files) if base.kind else None,
        "breakpoints": breakpoints(files),
        "containers": container_classes(files),
        "units": units(files),
        "liquiddoc": liquiddoc_forms(files),
        "custom_elements": custom_elements(files),
        "section_css": section_css_loading(files),
        "compliance": compliance(),
        "pages": pages(files),
        "tooling": tooling(),
        "live": live_inventory(argv[argv.index("--live-url") + 1]) if "--live-url" in argv else None,
    }
    if "--json" in argv:
        print(json.dumps(d, indent=2, default=str))
        return 0
    text = render(d)
    if "--stdout" in argv:
        print(text)
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
