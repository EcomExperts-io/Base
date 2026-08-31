#!/usr/bin/env python3
"""Scaffold a new section that already satisfies the merchant settings contract.

Why this exists
---------------
This is `.claude/skills/scaffold-section/SKILL.md` rewritten as something that
runs. The skill is correct, 156 lines long, and has been invoked zero times — on
Base or on any theme forked from it. An audit of this repo's AI tooling found
the same for every skill and every agent in `.claude/`, including on a task
written specifically for one of them. What has never failed is the pre-commit
hook: nobody chooses it, so it runs every time.

That is the pattern worth stating plainly, because it decides where new work
belongs: **in this codebase, things that must be chosen never run, and things
that run automatically always do.** A convention that depends on someone
remembering to invoke it is a convention that is not in force.

The cost of it not being in force is measured. On the Bites Vitamins build 30 of
31 new sections shipped with spacing and colour hardcoded into CSS and no
merchant settings behind them; 5 uses of `| t` against Base's 221; zero `t:`
schema keys against Base's 136. Every one of those sections would have been
compliant if it had started from a file like this one.

So: `python3 .claude/scripts/new-section.py testimonials` writes the four files,
and refuses to write any of them if what it just built would not pass
`.claude/scripts/check-section-contract.py` — the gate that would otherwise
block the commit hours later, after the section has been styled and reviewed.
It imports that checker rather than reimplementing it, so the two cannot drift.

What it does NOT do
-------------------
Design anything. The markup is a heading and a repeating block: a shape to
replace, not a section. What it guarantees is the part that gets skipped —
`padding_top`, `padding_bottom`, `color_scheme`, a `presets` entry, `t:` keys
throughout, the file naming, and a docs page that will not break the docs build.

It does not touch `locales/*.json`. Those carry an auto-generated header, are
rewritten by the Shopify admin language editor, and corrupt when two agents
write them at once — which is why `merge-locale-fragments.py` exists. The keys
are printed in that script's fragment format instead.

It does not touch `templates/*.json` or the docs sidebar. Both are one line, and
a script guessing at either buys a merge conflict rather than a keystroke.

Usage: python3 .claude/scripts/new-section.py <section-name> [--no-js]
"""

import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import textwrap
from collections import Counter
from string import Template

CONTRACT_CHECK = ".claude/scripts/check-section-contract.py"
MERGE_SCRIPT = ".claude/scripts/merge-locale-fragments.py"
REFERENCE = ".claude/skills/scaffold-section/reference-section.liquid"
RULE = ".claude/rules/sections.md"
SIDEBAR = "docs/.vitepress/config.mts"

# Theme Check's ValidSchemaName fails a schema `name` longer than this. It is a
# hard limit, the error does not say so, and it is easy to hit with a
# descriptive name. It applies to `name` only — the longer wording goes in the
# preset name, which is what a merchant actually reads in the theme editor.
MAX_SCHEMA_NAME = 25

# The padding boilerplate's breakpoint, inherited from Dawn and shared by 31
# sections here. It is NOT the theme's layout breakpoint, and it must not be
# unified with the component breakpoint detected below: changing it in one
# section desynchronises that section's mobile padding from every other one.
PADDING_BREAKPOINT = 750

SECTION_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

# Named for a page rather than for a job. A page-prefixed name stops being
# descriptive the first time the section is reused, and on the Bites build that
# happened immediately. Warned rather than blocked: `collection-hero` may be
# genuinely about collections rather than about one page.
PAGE_PREFIXES = ("home-", "homepage-", "about-", "landing-", "pdp-", "plp-", "contact-")

# Words this theme's own docs sidebar capitalises differently from str.title().
ACRONYMS = {
    "faq": "FAQ",
    "ugc": "UGC",
    "cta": "CTA",
    "pdp": "PDP",
    "plp": "PLP",
    "seo": "SEO",
    "v2": "V2",
    "v3": "V3",
}

CONTAINER_CANDIDATES = ("page-width", "container")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
# Anchored to `@media` on purpose: `min-width` is also an ordinary property
# (`min-width: 44px` on a touch target), and counting those picks a
# breakpoint that is not one.
MEDIA_MIN_WIDTH_RE = re.compile(r"@media[^{]*?min-width:\s*(\d+)px")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


# --------------------------------------------------------------------------
# Repo facts
# --------------------------------------------------------------------------

def repo_root():
    """Resolve the repo from git rather than a hardcoded path, so this script is
    portable between the client themes forked from Base."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit("not inside a git repository — run this from the theme.")
    return pathlib.Path(out.stdout.strip())


def detect_container_class(repo):
    """Which container class this theme's sections actually use.

    Base uses `.page-width` in all 32 of its sections, but a client theme forked
    from Base often introduces its own container, and the two are frequently
    identical at 1440 — so a section built with the wrong one measures correctly
    at the width the Figma frame was drawn at, passes review, and reads as broken
    at 1920. That happened on a client build and was caught by the lead, not by
    the developer. Counting what the theme already ships is cheaper than
    remembering to check.
    """
    counts = Counter()
    for path in sorted((repo / "sections").glob("*.liquid")):
        for attr in CLASS_ATTR_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
            for token in attr.split():
                if token in CONTAINER_CANDIDATES:
                    counts[token] += 1
    if not counts:
        return CONTAINER_CANDIDATES[0]
    return counts.most_common(1)[0][0]


def detect_component_breakpoint(repo):
    """The `min-width` this theme's own section CSS settled on.

    Base's `section-*.css` is split evenly between 750px and 769px, so there is
    no single right answer to copy out of a rule file — the rule says to grep the
    theme and match it. This is that grep. Distinct from PADDING_BREAKPOINT
    above: two numbers, two jobs.
    """
    counts = Counter()
    for path in sorted((repo / "assets").glob("section-*.css")):
        counts.update(MEDIA_MIN_WIDTH_RE.findall(path.read_text(encoding="utf-8", errors="ignore")))
    if not counts:
        return PADDING_BREAKPOINT
    return int(counts.most_common(1)[0][0])


def related_sections(repo, name):
    """Existing sections sharing a word with the new name.

    Not a check — a prompt to look before adding a forty-ninth section that does
    what the thirty-second already does.
    """
    words = set(name.split("-"))
    hits = []
    for path in sorted((repo / "sections").glob("*.liquid")):
        if path.stem == name:
            continue
        if words & set(path.stem.split("-")):
            hits.append(path.stem)
    return hits


# --------------------------------------------------------------------------
# Naming
# --------------------------------------------------------------------------

def titleize(name):
    return " ".join(ACRONYMS.get(word, word.capitalize()) for word in name.split("-"))


def element_tag(name):
    """A custom element name must contain a hyphen.

    `customElements.define('testimonials', ...)` throws a SyntaxError and the
    whole module fails to evaluate, so a single-word section gets a `-section`
    suffix on its tag while keeping its own name for files and classes.
    """
    return name if "-" in name else f"{name}-section"


def class_name(tag):
    return "".join(word.capitalize() for word in tag.split("-"))


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

LIQUID = Template(
    """{% comment %} /sections/${name}.liquid {% endcomment %}

{{ 'section-${name}.css' | asset_url | stylesheet_tag }}${script_tag}

{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: ${padding_breakpoint}px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}

<${tag}
  class="${name} color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"${extra_attrs}
>
  <div class="${container}">
    {%- if section.settings.heading != blank -%}
      <h2 class="${name}__heading">{{ section.settings.heading | escape }}</h2>
    {%- endif -%}

    {%- if section.blocks.size > 0 -%}
      <div class="${name}__grid">
        {%- for block in section.blocks -%}
          <div class="${name}__item" {{ block.shopify_attributes }}>
            {%- if block.settings.image != blank -%}
              {{
                block.settings.image
                | image_url: width: 800
                | image_tag:
                  class: '${name}__image',
                  loading: 'lazy',
                  widths: '400, 600, 800',
                  sizes: '(min-width: ${component_breakpoint}px) 33vw, 100vw',
                  alt: block.settings.title
              }}
            {%- endif -%}

            {%- if block.settings.title != blank -%}
              <h3 class="${name}__title">{{ block.settings.title | escape }}</h3>
            {%- endif -%}
          </div>
        {%- endfor -%}
      </div>
    {%- endif -%}
  </div>
</${tag}>

{% schema %}
${schema}
{% endschema %}
"""
)

DISPLAY_RULE = Template(
    """.${name} {
  /* <${tag}> is a custom element, and a custom element defaults to
     display: inline. An inline box paints no background around block children
     and ignores vertical padding, so the color scheme and the section padding
     applied above would both silently do nothing. getComputedStyle() still
     reports both, which is why this reads as correct in a DOM check and wrong
     on screen. */
  display: block;
}

"""
)

CSS = Template(
    """/* sections/${name}.liquid */

${display_rule}.${name}__heading {
  margin: 0 0 2.4rem;
}

.${name}__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.4rem;
}

.${name}__item {
  min-width: 0;
}

.${name}__image {
  display: block;
  width: 100%;
  height: auto;
}

.${name}__title {
  margin: 1.2rem 0 0;
}

@media screen and (min-width: ${component_breakpoint}px) {
  .${name}__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
"""
)

JS = Template(
    """/**
 * ${title} section.
 *
 * Registered as <${tag}>. Add every listener in connectedCallback with
 * this.abortController.signal, so disconnectedCallback removes all of them in
 * one call: the theme editor re-renders a section on every settings change, and
 * a listener that outlives its element accumulates one copy per edit.
 */

export class ${cls} extends HTMLElement {
  abortController = null;

  connectedCallback() {
    this.abortController = new AbortController();
  }

  disconnectedCallback() {
    this.abortController?.abort();
    this.abortController = null;
  }
}

if (!customElements.get('${tag}')) {
  customElements.define('${tag}', ${cls});
}
"""
)

DOCS = Template(
    """# ${title} Section (`sections/${name}.liquid`)

`sections/${name}.liquid` renders TODO — one paragraph on what a merchant sees, what the section is for, and where it is used. This page was scaffolded alongside the section; rewrite this paragraph before the section ships.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-${name}.css`, inline <code v-pre>{%- style -%}</code> block for responsive padding |
| JS   | ${js_cell} |
${element_row}| Blocks | `item` (image + title) |
| Data | `section.settings` for the heading, `section.blocks` for the repeating items |

---

## Dynamic Styles

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: ${padding_breakpoint}px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- **Responsive padding**: mobile padding is 75% of the desktop value; the full value applies at ${padding_breakpoint}px and up.
- **Color scheme**: the wrapper carries the theme's `color-` scheme class, so the section inherits the merchant's chosen palette rather than hardcoded colors.

---

## Markup Structure

```liquid
${markup}
```

---

## Schema

```json
${schema}
```

### Section Settings

- **Heading**: optional section title; the element is omitted when blank.
- **Color Scheme**: theme color scheme applied to the wrapper.
- **Padding**: top and bottom spacing, 0–100px in steps of 4, default 40.

### Block Settings (Item)

- **Image**: item image, rendered lazily with a responsive `srcset`.
- **Title**: item title, also used as the image's alt text.

---

## Behavior

${behavior}

---

## Translation Keys

Schema keys, in `locales/en.default.schema.json`:

| Key | Value |
|-----|-------|
${locale_rows}

No storefront (`| t`) keys yet — every string the section renders comes from a merchant setting. Add them to `locales/en.default.json` as soon as the section renders text of its own, including `aria-label`, `alt` and visually hidden copy.

---

## Implementation Notes

1. **Scaffolded, not designed.** Generated by `.claude/scripts/new-section.py`. The heading-plus-grid markup is a starting shape; replace it, and rewrite this page as the section takes its real form.
2. **The settings contract is already satisfied.** `padding_top`, `padding_bottom`, `color_scheme` and a `presets` entry are present. Keep them — the pre-commit gate blocks a new section without them, and the merchant-facing contract is judged separately from visual fidelity.
${notes_tail}
"""
)


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

def build_schema(name, title):
    """The schema, built as data so it cannot be malformed JSON.

    A section whose `{% schema %}` does not parse blocks the commit outright, and
    the checker's own tolerance for a trailing comma exists because two Base
    sections have one. Generating from a dict removes the whole category.

    Locale keys use the section handle verbatim: `locales/en.default.schema.json`
    already keys its sections that way (`main-cart-items`, `custom-liquid`), so
    the key is one less thing to translate between when reading the file.
    """
    return {
        "name": f"t:sections.{name}.name",
        "tag": "section",
        "settings": [
            {
                "type": "text",
                "id": "heading",
                "label": f"t:sections.{name}.settings.heading.label",
            },
            {
                "type": "color_scheme",
                "id": "color_scheme",
                "label": "t:sections.all.colors.label",
                "default": "scheme-1",
            },
            {
                "type": "header",
                "content": "t:sections.all.padding.section_padding_heading",
            },
            {
                "type": "range",
                "id": "padding_top",
                "label": "t:sections.all.padding.padding_top",
                "min": 0,
                "max": 100,
                "step": 4,
                "unit": "px",
                "default": 40,
            },
            {
                "type": "range",
                "id": "padding_bottom",
                "label": "t:sections.all.padding.padding_bottom",
                "min": 0,
                "max": 100,
                "step": 4,
                "unit": "px",
                "default": 40,
            },
        ],
        "blocks": [
            {
                "type": "item",
                "name": f"t:sections.{name}.blocks.item.name",
                "limit": 6,
                "settings": [
                    {
                        "type": "image_picker",
                        "id": "image",
                        "label": f"t:sections.{name}.blocks.item.settings.image.label",
                    },
                    {
                        "type": "text",
                        "id": "title",
                        "label": f"t:sections.{name}.blocks.item.settings.title.label",
                    },
                ],
            }
        ],
        "presets": [
            {
                "name": f"t:sections.{name}.presets.name",
                "blocks": [{"type": "item"}, {"type": "item"}, {"type": "item"}],
            }
        ],
    }


def locale_fragment(name, title):
    """The keys the generated schema references, in the shape
    merge-locale-fragments.py expects."""
    return {
        "schema": {
            "sections": {
                name: {
                    "name": title,
                    "presets": {"name": title},
                    "settings": {"heading": {"label": "Heading"}},
                    "blocks": {
                        "item": {
                            "name": "Item",
                            "settings": {
                                "image": {"label": "Image"},
                                "title": {"label": "Title"},
                            },
                        }
                    },
                }
            }
        },
        "storefront": {},
    }


def flatten(node, prefix=""):
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from flatten(value, path)
        else:
            yield path, value


def render(name, with_js, container, component_breakpoint):
    """Return {relative path: contents} for every file this run would write."""
    title = titleize(name)
    tag = element_tag(name) if with_js else "div"
    cls = class_name(element_tag(name))
    schema = json.dumps(build_schema(name, title), indent=2, ensure_ascii=False)

    liquid = LIQUID.substitute(
        name=name,
        tag=tag,
        container=container,
        schema=schema,
        padding_breakpoint=PADDING_BREAKPOINT,
        component_breakpoint=component_breakpoint,
        script_tag=(
            f"\n<script src=\"{{{{ 'section-{name}.js' | asset_url }}}}\" type=\"module\"></script>"
            if with_js
            else ""
        ),
        extra_attrs='\n  data-section-id="{{ section.id }}"' if with_js else "",
    )

    css = CSS.substitute(
        name=name,
        component_breakpoint=component_breakpoint,
        display_rule=DISPLAY_RULE.substitute(name=name, tag=tag) if with_js else "",
    )

    # The docs page quotes the wrapper markup only. The asset tags and the
    # padding block appear under "Dynamic Styles" above it and the schema has its
    # own heading below it; no existing docs page prints the same file twice.
    markup = liquid.split("{%- endstyle -%}", 1)[1].split("{% schema %}")[0].strip()
    locale_rows = "\n".join(
        f"| `{key}` | {value} |"
        for key, value in flatten(locale_fragment(name, title)["schema"]["sections"], "sections")
    )

    if with_js:
        js_cell = f"`section-{name}.js` (module)"
        element_row = f"| Custom Element | `<{tag}>` defined in `section-{name}.js` |\n"
        behavior = (
            f"The section registers `<{tag}>` and holds an `AbortController` for the lifetime of the "
            "element; there is no behaviour yet. Add listeners in `connectedCallback` with that "
            "controller's signal so `disconnectedCallback` removes all of them at once — the theme "
            "editor re-renders a section on every settings change."
        )
        notes_tail = (
            f"3. **`display: block` is load-bearing.** `<{tag}>` is a custom element, which defaults to "
            "`display: inline`. An inline box paints no background around block children and ignores "
            "vertical padding, so without that rule the color scheme and the section padding both "
            "silently do nothing — while `getComputedStyle()` keeps reporting them.\n"
            "4. **Locale keys must exist before the section is opened in the theme editor.** An "
            "unresolved `t:` key renders its own key path as visible text.\n"
            "5. **VitePress mustache safety.** VitePress compiles this page as a Vue template and "
            "evaluates Liquid mustaches in inline code spans; fenced blocks are safe. Use "
            "`<code v-pre>` for anything inline, or the docs build dies.\n"
        )
    else:
        js_cell = "None — the section has no behaviour"
        element_row = ""
        behavior = "Purely presentational; there is no JavaScript."
        notes_tail = (
            "3. **Locale keys must exist before the section is opened in the theme editor.** An "
            "unresolved `t:` key renders its own key path as visible text.\n"
            "4. **VitePress mustache safety.** VitePress compiles this page as a Vue template and "
            "evaluates Liquid mustaches in inline code spans; fenced blocks are safe. Use "
            "`<code v-pre>` for anything inline, or the docs build dies.\n"
        )

    docs = DOCS.substitute(
        name=name,
        title=title,
        markup=markup,
        schema=schema,
        js_cell=js_cell,
        element_row=element_row,
        behavior=behavior,
        notes_tail=notes_tail,
        locale_rows=locale_rows,
        padding_breakpoint=PADDING_BREAKPOINT,
    )

    files = {
        f"sections/{name}.liquid": liquid,
        f"assets/section-{name}.css": css,
    }
    if with_js:
        files[f"assets/section-{name}.js"] = JS.substitute(
            title=title, tag=element_tag(name), cls=cls
        )
    files[f"docs/sections/{name}.md"] = docs
    return files


# --------------------------------------------------------------------------
# Verification — run before anything is written
# --------------------------------------------------------------------------

def contract_problems(repo, path, src):
    """Run the pre-commit contract check's own `check()` over the generated file.

    Imported rather than reimplemented, so this scaffolder cannot drift from the
    gate it is supposed to satisfy: if the contract gains a requirement, this
    script starts failing on its own output the same day.

    Returns None when the checker cannot be loaded. A missing checker is a
    warning, not a refusal — a scaffolder that will not run because a sibling
    script was renamed is worse than one that writes a compliant file unverified.
    """
    checker = repo / CONTRACT_CHECK
    if not checker.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_section_contract", checker)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        problems, _ = module.check(path, src)
        return problems
    except Exception:
        return None


def docs_interpolation_problems(markdown):
    """Lines carrying a Liquid mustache outside a fenced block.

    Mirrors `.claude/scripts/check-docs-interpolation.py`, which reads staged git
    content and so cannot be pointed at a string. VitePress compiles every docs
    page as a Vue template and evaluates mustaches in inline spans; that broke
    the docs build for four months without anyone noticing, because the deploy
    workflow only runs on pushes that touch docs/**.
    """
    problems, in_fence = [], False
    for number, line in enumerate(markdown.split("\n"), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "{{" in line and "v-pre" not in line:
            problems.append(f"{number}: {line.strip()[:88]}")
    return problems


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def refuse(headline, body):
    """Print a blocking message in the pre-commit hook's format and return 1.

    Same shape as check-section-contract.py's output on purpose: a refusal from
    the scaffolder and a refusal from the gate are the same event arriving at
    different times, and they should not look like two different tools.
    """
    print()
    print("=" * 74)
    print(f"  {headline}")
    print("=" * 74)
    print()
    for line in body:
        if not line:
            print()
        elif line.startswith(" ") or len(line) <= 70:
            print(f"  {line}")
        else:
            for wrapped in textwrap.wrap(line, 70):
                print(f"  {wrapped}")
    print()
    return 1


def validate(name):
    """Return an error string, or None."""
    if name.startswith("main-"):
        return (
            f'"{name}" uses the reserved `main-` prefix. That is for template main '
            "sections only (product, cart, search, customers/*). Name a new section "
            "by what it does."
        )
    if not SECTION_NAME_RE.match(name):
        return (
            f'"{name}" is not a section name. Lowercase letters and digits, '
            "hyphen-separated, starting with a letter: `selling-points`, `hero-v2`."
        )
    title = titleize(name)
    if len(title) > MAX_SCHEMA_NAME:
        return (
            f'the schema name "{title}" is {len(title)} characters; Theme Check\'s '
            f"ValidSchemaName fails above {MAX_SCHEMA_NAME} and the error does not say so.\n"
            "Shorten the section name. The longer wording belongs in the preset name, "
            "which is what the merchant actually reads in the theme editor."
        )
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    unknown = [f for f in flags if f != "--no-js"]

    if len(args) != 1 or unknown:
        print("usage: new-section.py <section-name> [--no-js]")
        print()
        print("  <section-name>  lowercase, hyphenated, named by function not by page")
        print("  --no-js         the section has no behaviour; skip the JS file")
        if unknown:
            print()
            print(f"  unknown option(s): {' '.join(unknown)}")
        return 2

    name = args[0]
    with_js = "--no-js" not in flags

    error = validate(name)
    if error:
        return refuse("NOT CREATED — the name is not usable", error.split("\n"))

    repo = repo_root()
    container = detect_container_class(repo)
    component_breakpoint = detect_component_breakpoint(repo)
    files = render(name, with_js, container, component_breakpoint)

    existing = [path for path in files if (repo / path).exists()]
    if existing:
        return refuse(
            f"NOT CREATED — {len(existing)} file(s) already exist",
            [
                "Nothing was written. A scaffolder that overwrites is a scaffolder",
                "that eats work, so this refuses rather than merges:",
                "",
                *[f"  {path}" for path in existing],
                "",
                "Pick another name, or delete these deliberately and run again.",
            ],
        )

    section_path = f"sections/{name}.liquid"
    problems = contract_problems(repo, section_path, files[section_path])
    if problems:
        return refuse(
            "NOT CREATED — the generated section fails the contract check",
            [
                "This is a bug in this script, not in your input. It generated a",
                f"section that {CONTRACT_CHECK} would block at commit time:",
                "",
                *[f"  - {problem}" for problem in problems],
                "",
                f"Fix the templates here, or start from {REFERENCE}.",
            ],
        )

    docs_path = f"docs/sections/{name}.md"
    docs_problems = docs_interpolation_problems(files[docs_path])
    if docs_problems:
        return refuse(
            "NOT CREATED — the generated docs page would break the docs build",
            [
                "This is a bug in this script. VitePress evaluates Liquid mustaches",
                "outside fenced blocks as Vue expressions:",
                "",
                *[f"  {problem}" for problem in docs_problems],
                "",
                "Fix: wrap the inline span as <code v-pre>...</code>.",
            ],
        )

    for path, contents in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")

    report(repo, name, files, with_js, container, component_breakpoint, problems is None)
    return 0


def report(repo, name, files, with_js, container, component_breakpoint, unverified):
    title = titleize(name)
    tag = element_tag(name)
    width = max(len(path) for path in files)

    print()
    print(f"Created {len(files)} file(s):")
    for path, contents in files.items():
        print(f"  {path.ljust(width)}  {len(contents.splitlines())} lines")
    print()
    print(f"  container class     .{container} (detected from this theme's sections)")
    print(f"  CSS breakpoint      {component_breakpoint}px (detected from assets/section-*.css)")
    print(f"  padding breakpoint  {PADDING_BREAKPOINT}px (fixed — the Dawn boilerplate, shared theme-wide)")
    if with_js:
        print(f"  custom element      <{tag}>")
    print()
    if unverified:
        print(f"  Contract check SKIPPED — could not load {CONTRACT_CHECK}.")
        print("  The pre-commit hook will still run it. Check it is where it should be.")
    else:
        print(f"  Contract check PASSED ({CONTRACT_CHECK}).")

    if name.startswith(PAGE_PREFIXES):
        print()
        print(f"  Note: \"{name}\" reads as a page name. Sections are named by function —")
        print("  a page-prefixed name stops being descriptive the first time the section")
        print(f"  is reused. See {RULE}.")

    related = related_sections(repo, name)
    if related:
        print()
        print("  Note: these existing sections share a word with this one. Worth a look")
        print("  before building a second one that does the same job:")
        print(f"    {', '.join(related)}")

    fragment = locale_fragment(name, title)
    print()
    print("-" * 74)
    print("  LOCALE KEYS — the section is not finished without these")
    print("-" * 74)
    print()
    print("  Every schema string above is a `t:` key. A key that does not resolve")
    print("  renders its own key path as visible text in the theme editor, so this")
    print("  is not a tidying step.")
    print()
    print("  locales/en.default.schema.json is not written by this script: it carries an")
    print("  auto-generated header, the Shopify admin language editor rewrites it, and")
    print("  concurrent writers corrupt it. Save this fragment as")
    print(f"  <fragment-dir>/{name}.json and merge it:")
    print()
    for line in json.dumps(fragment, indent=2, ensure_ascii=False).split("\n"):
        print(f"    {line}")
    print()
    print(f"    python3 {MERGE_SCRIPT} <fragment-dir>")
    print()
    print('  Working alone, the same keys go under "sections" in')
    print("  locales/en.default.schema.json by hand. Add `| t` keys to")
    print("  locales/en.default.json as soon as the section renders a string of its")
    print("  own — visible copy, aria-label, alt, or visually hidden text.")
    print()
    print("-" * 74)
    print("  NEXT")
    print("-" * 74)
    print()
    print("  1. Add the section to a template so it can be seen — an existing")
    print(f"     template's section order, or templates/page.{name}.json.")
    print(f"  2. Add the docs page to the sidebar in {SIDEBAR}:")
    print(f"       {{ text: '{title}', link: '/sections/{name}' }},")
    print(f"  3. npx prettier --config .prettierrc.json --write sections/{name}.liquid")
    print("  4. shopify theme check --config=.theme-check.yml")
    print()
    print(f"  The shape to build into: {REFERENCE}")
    print(f"  Why the contract exists:  {RULE}")
    print()


if __name__ == "__main__":
    sys.exit(main())
