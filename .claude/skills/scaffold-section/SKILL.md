---
name: scaffold-section
description: Generate a complete, standards-compliant new Shopify section from a description. Use when the user asks to scaffold, create, or add a new section.
---

# scaffold-section

**Purpose:** Generate a complete, standards-compliant new section from a description.

**Invocation:** `/scaffold-section <name> [description]`
Example: `/scaffold-section testimonials "Displays customer testimonials in a grid"`

## Steps

1. Confirm the section name is lowercase-hyphenated and does **not** use the `main-` prefix
   (the `main-` prefix is reserved for main template sections).
2. Create `sections/<name>.liquid` using `.cursor/rules/examples/section-example.liquid` as the
   structural template, with:
   - a `<section>` wrapper,
   - a `page-width` div,
   - a `{% style %}` block for padding variables (dynamic per-instance values only),
   - a `{% schema %}` tag,
   - schema keys using `t:` prefixes,
   - a `{% stylesheet %}` block or a `stylesheet_tag` reference to the section's CSS.
3. Create `assets/section-<name>.css` with a BEM class structure scoped to the section.
4. If JS is needed (more than ~100 lines of logic): create `assets/section-<name>.js` using the
   `customElements.define` guard pattern (`if (!customElements.get(...))`,
   `connectedCallback`/`disconnectedCallback`); load it in the Liquid file with `type="module"`.
5. Add the section to at least one demo template (e.g. `templates/page.<name>.json`).
6. Create `docs/sections/<name>.md` with the standard VitePress documentation structure (what it
   does, dependencies table, schema settings table, example usage).
7. Confirm there are **no hardcoded English strings** in schema labels — all use `t:` keys.
8. Confirm there are **no hardcoded hex colors** — all colors use `var(--color-*)` tokens.

## Notes

- This repo has **no `schemas/` folder** and **no `npm run build:schemas`** step. Schemas are
  written inline in the section `.liquid` file inside a `{% schema %}` tag.
- Section CSS/JS file naming must match: `section-<name>.{css,js}`.
