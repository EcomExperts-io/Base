---
name: scaffold-section
description: Create a new Base Theme section with the required merchant settings contract, translation keys, and matching CSS/JS files. Use when asked to scaffold, create, or add a new section.
argument-hint: <name> ["description"]
---

# scaffold-section

Creates a section that complies with Base Theme standards on the first pass.

## Before you start

Read `.claude/rules/sections.md` and `.claude/rules/schemas.md`. Then
**generate, then edit** — the script refuses a section failing the contract:

```bash
python3 .claude/scripts/new-section.py <name>
```

It writes `sections/<name>.liquid`, `assets/section-<name>.css`, the JS file
unless `--no-js`, and the docs page, then runs `check-section-contract.py` on
them. It prints the locale keys as a fragment for `merge-locale-fragments.py`
rather than editing `locales/*.json` (two agents writing that file at once
corrupt it), and leaves the template and the docs sidebar to you. Steps 1–8
are what each file must keep when you edit it.

`.claude/skills/scaffold-section/reference-section.liquid` is the shape the
script copies. **Do not use `.claude/rules/examples/section-example.liquid`**:
it predates the standard and exposes none of the required settings.

## Steps

### 1. Name it

Lowercase, hyphenated, named by **function**: `testimonials`, not
`home-testimonials`. Never the `main-` prefix (template main sections only).
Check `sections/` for an existing section that already does the job.

### 2. Create `sections/<name>.liquid`

Copy the reference file's shape:

- CSS via `{{ '...' | asset_url | stylesheet_tag }}`; JS, if any, as `type="module"`
- The `{%- style -%}` block computing `.section-{{ section.id }}-padding`:
  the mobile pair outside the media query, the desktop pair inside it
- A wrapper carrying `color-{{ section.settings.color_scheme }}` and
  `section-{{ section.id }}-padding`
- A `page-width` inner wrapper, unless deliberately full-bleed
- `{{ block.shopify_attributes }}` on every block-rendered element; `| escape`
  on every text setting rendered into markup

### 3. Schema — the required settings

Non-negotiable, in this order:

| id | type | label |
|---|---|---|
| `color_scheme` | `color_scheme` | `t:sections.all.colors.label` |
| — | `header` | `t:sections.all.padding.section_padding_heading` |
| `padding_top` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_top` |
| `padding_bottom` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_bottom` |
| `padding_top_mobile` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_top_mobile` |
| `padding_bottom_mobile` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_bottom_mobile` |

Plus a `presets` array, or the merchant cannot add the section.

The four padding settings have **no exceptions**; mobile is its own value.
`color_scheme` may be omitted only when the design fixes the surface, with a
Liquid comment saying so:

```liquid
{%- comment -%}
  No color_scheme setting: this section's background is a fixed brand surface
  in the design (Figma node 1234:5678).
{%- endcomment -%}
```

A Figma frame shows one spacing value because it can only show one; add them anyway.

### 4. Every label is a translation key

No bare English in schema `label`, `content`, `info`, preset and block `name`,
or in markup `aria-label`, `alt`, `title` and visible text.

- Schema strings → `t:` prefix, keys in `locales/en.default.schema.json`
- Markup strings → `| t` filter, keys in `locales/en.default.json`

**Add the keys in the same change** — an unresolved `t:` key renders its path
in the theme editor. The six `sections.all.*` keys in the table exist; reuse them.

### 5. Create `assets/section-<name>.css`

- BEM, scoped to the section: `.testimonials__card--featured`
- Mobile-first `min-width` queries; logical properties; no `!important`
  without a comment saying why
- Instance values as inline CSS custom properties, not per-instance classes
- No hardcoded hex — `var(--color-*)` tokens
- **A class on a custom element tag needs an explicit `display`**; the default
  `inline` drops background and vertical padding on screen.

### 6. Create `assets/section-<name>.js` — only if needed

Only if the section has behaviour:

```js
if (!customElements.get('example-name')) {
  customElements.define('example-name', class ExampleName extends HTMLElement {
    connectedCallback() { /* wire up */ }
    disconnectedCallback() { /* remove every listener added above */ }
  });
}
```

Alpine for ephemeral UI state, a custom element for fetching, URL sync or
cross-region updates — not both. A shared behaviour file goes through the
decision test in `.claude/rules/naming-conventions.md`.

### 7. Add it to a template

At least one, so it can be seen: `templates/page.<name>.json` or an existing template.

### 8. Document it

`docs/sections/<name>.md`, like the existing pages: purpose, dependencies, settings, example.

## Self-check before you report done

State each result; do not assert compliance:

- [ ] `padding_top`, `padding_bottom`, `padding_top_mobile`,
      `padding_bottom_mobile` all present in the schema, each a `range`
- [ ] `color_scheme` present, or a Liquid comment explains why not
- [ ] `presets` array present
- [ ] Zero bare-English strings — grep for `"label": "[A-Z]` and `aria-label="[A-Z]`
- [ ] Every new locale key added to the locale file
- [ ] Section named by function, not by page
- [ ] CSS via `stylesheet_tag`, JS via `type="module"`
- [ ] `{% schema %}` is valid JSON
- [ ] Media queries are `min-width` only

The gate checks the mechanical subset; passing it is not passing this list.
