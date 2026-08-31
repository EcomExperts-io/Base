---
name: scaffold-section
description: Create a new Base Theme section with the required merchant settings contract, translation keys, and matching CSS/JS files. Use when asked to scaffold, create, or add a new section.
---

# scaffold-section

Creates a new section that complies with Base Theme standards on the first pass,
rather than one that has to be corrected in review.

**Invocation:** `/scaffold-section <name> ["description"]`
Example: `/scaffold-section testimonials "Customer quotes in a responsive grid"`

## Before you start

Read `.claude/rules/sections.md` and `.claude/rules/schemas.md`. This skill
tells you what to produce; those state the requirements and why they exist.

Use `.claude/skills/scaffold-section/reference-section.liquid` as the structural
template. **Do not use `.claude/rules/examples/section-example.liquid`** — it
predates the current standard, teaches `{% stylesheet %}` and
`{% content_for 'blocks' %}`, and exposes none of the required settings.

## Steps

### 1. Name it

Lowercase, hyphenated, named by **function** — not by the page it first appears
on. `testimonials`, not `home-testimonials`. A page-prefixed name stops being
descriptive the first time the section is reused.

Never use the `main-` prefix; that is reserved for template main sections.

Check `sections/` for an existing section that already does this job before
creating a new one.

### 2. Create `sections/<name>.liquid`

Copy the reference file's shape. Every section must have:

- CSS loaded with `{{ '...' | asset_url | stylesheet_tag }}`
- JS, if any, as `<script src="..." type="module"></script>`
- The `{%- style -%}` block computing `.section-{{ section.id }}-padding`, with
  mobile at 0.75× the desktop value
- A wrapper carrying `color-{{ section.settings.color_scheme }}` and
  `section-{{ section.id }}-padding`
- A `page-width` inner wrapper, unless the design is deliberately full-bleed
- `{{ block.shopify_attributes }}` on every block-rendered element
- `| escape` on every text setting rendered into markup

### 3. Schema — the required settings

Non-negotiable, in this order:

| id | type | label |
|---|---|---|
| `color_scheme` | `color_scheme` | `t:sections.all.colors.label` |
| — | `header` | `t:sections.all.padding.section_padding_heading` |
| `padding_top` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_top` |
| `padding_bottom` | `range` 0–100 step 4, default 40 | `t:sections.all.padding.padding_bottom` |

Plus a `presets` array — without one the merchant cannot add the section at all.

`padding_top` and `padding_bottom` have **no exceptions**. `color_scheme` may be
omitted only if the design fixes the surface, and only with a Liquid comment
saying so:

```liquid
{%- comment -%}
  No color_scheme setting: this section's background is a fixed brand surface
  in the design (Figma node 1234:5678).
{%- endcomment -%}
```

If you are building from a Figma frame, expect the design to give you no reason
to add these. Add them anyway — the frame shows one spacing value because a
frame can only show one, not because the merchant shouldn't be able to change it.

### 4. Every label is a translation key

No bare English anywhere: schema `label`, `content`, `info`, preset `name`,
block `name`, and in the markup `aria-label`, `alt`, `title`, and all visible
text.

- Schema strings → `t:` prefix, keys in `locales/en.default.schema.json`
- Markup strings → `| t` filter, keys in `locales/en.default.json`

**Add the keys to the locale file in the same change.** A `t:` key that doesn't
resolve renders the key path as visible text in the theme editor.

These four already exist and should be reused rather than duplicated:
`sections.all.colors.label`, `sections.all.padding.section_padding_heading`,
`sections.all.padding.padding_top`, `sections.all.padding.padding_bottom`.

### 5. Create `assets/section-<name>.css`

- BEM, scoped to the section: `.testimonials__card--featured`
- Mobile-first `min-width` media queries. Never `max-width`.
- No `!important` without a comment explaining why
- Logical properties (`padding-block-start`, `margin-inline`)
- Instance values as CSS custom properties set inline from settings, not
  generated per-instance classes
- No hardcoded hex — use `var(--color-*)` tokens
- **If a class sits on a custom element tag, set `display` explicitly.** Custom
  elements default to `display: inline`, which silently drops background and
  vertical padding while `getComputedStyle` still reports both.

### 6. Create `assets/section-<name>.js` — only if needed

Skip this entirely if the section has no behaviour. If it does:

```js
if (!customElements.get('example-name')) {
  customElements.define('example-name', class ExampleName extends HTMLElement {
    connectedCallback() { /* wire up */ }
    disconnectedCallback() { /* remove every listener added above */ }
  });
}
```

No `DOMContentLoaded`. No jQuery. Use Alpine for ephemeral UI state (drawer
open, accordion expand) and a custom element for data fetching, URL sync, or
cross-region DOM updates — not both in one section.

Before writing a shared behaviour file, apply the decision test in
`.claude/rules/naming-conventions.md`: same behaviour differing only in
configuration → one `component-*`; genuinely different configuration → separate
`section-*` files.

### 7. Add it to a template

At minimum one, so it can be seen: `templates/page.<name>.json` or an existing
template's section order.

### 8. Document it

`docs/sections/<name>.md`, matching the existing VitePress pages: what it does,
dependencies table, schema settings table, example usage.

## Self-check before you report done

Run through this and state the result — do not just assert compliance:

- [ ] `color_scheme`, `padding_top`, `padding_bottom` all present in the schema
      (or a Liquid comment explains the missing `color_scheme`)
- [ ] `presets` array present
- [ ] Zero bare-English strings — grep your own output for `"label": "[A-Z]`
      and `aria-label="[A-Z]`
- [ ] Every new locale key actually added to the locale file
- [ ] Section named by function, not by page
- [ ] CSS via `stylesheet_tag`, JS via `type="module"`
- [ ] `{% schema %}` is valid JSON
- [ ] Media queries are `min-width` only

The pre-commit gate checks the mechanical subset of this. Passing the gate is
not the same as passing this list.
