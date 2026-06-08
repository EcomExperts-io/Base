# Base Theme — Agent Context

Shared backbone for any AI agent (Cursor, Claude Code, Codex, Gemini, etc.) working in this repo.
This file states the **non-negotiables** and points to deeper layers — it does **not** duplicate
full rule bodies. The `.cursor/rules/*.mdc` files add depth and are glob-activated in Cursor.

## What This Is

Shopify theme (Online Store 2.0). Liquid + custom web components + Alpine.js 3.14 +
Liquid AJAX Cart 2.1.1 + Swiper 7.4.1. VitePress docs site in `docs/`.

This theme ships a **single language: English**. There are no `es.json`/`fr.json`/`de.json` locale
files — add new keys to `locales/en.default.json` (and schema keys to
`locales/en.default.schema.json`) only.

## File Structure

```
sections/ — sections/*.liquid (no main- prefix; main- is reserved for template sections)
snippets/ — snippets/component-*.liquid
assets/   — section-*.{css,js}, component-*.{css,js}
blocks/   — blocks/*.liquid (theme-level blocks, flat, no prefix)
locales/  — en.default.json + en.default.schema.json (English only)
.cursor/  — AI tooling (Cursor rules, skills, references, prompts)
.claude/  — mirror of skills for Claude Code
docs/     — VitePress documentation site
```

**There is no `schemas/` folder and no `npm run build:schemas` step.** Schemas are written inline
in each section/block `.liquid` file inside a `{% schema %}` tag.

## Core Standards (Mandatory for all agents)

1. **Custom elements:** all component/section JS extends `HTMLElement` with
   `connectedCallback`/`disconnectedCallback` and an `if (!customElements.get(...))` guard.
2. **Naming:** sections use the `section-` prefix for CSS/JS; snippets use the `component-` prefix.
   File names match across `.liquid`/`.css`/`.js`.
3. **CSS:** BEM class names, `var(--color-*)` tokens (never hardcode hex colors), no ID selectors,
   no undocumented `!important`, target `0 1 0` specificity.
4. **Schemas:** inline `{% schema %}` in each `.liquid` file; all labels use `t:` keys.
5. **Snippets:** `{% doc %}` with `@param` entries required on all `component-` snippets; give every
   parameter a `| default:` value.
6. **No `DOMContentLoaded`, no jQuery, no hardcoded hex colors.** Load section/component scripts with
   `type="module"`, not `defer`.
7. **`layout/theme.liquid` stays ≤ ~300 lines** — delegate to snippets/sections.

## Skills Available

Invoke in Cursor with a slash command; Claude Code treats these as named workflows (same content
in `.claude/skills/`):

- `/scaffold-section` — scaffold a standards-compliant section
- `/scaffold-block` — scaffold a standards-compliant theme block
- `/scaffold-snippet` — scaffold a standards-compliant component snippet
- `/pr-review` — run the 15-item standards checklist against a diff (report only)
- `/accessibility-review` — WCAG 2.1 AA audit of a component/section (report only)

## Deeper Layers

- `.cursor/rules/*.mdc` — glob-scoped standards (CSS, JS, sections, snippets, blocks, schemas,
  localization, HTML, templates, etc.).
- `.cursor/references/css-reference.md` and `.cursor/references/javascript-reference.md` —
  long-form guides and worked examples behind the slim CSS/JS rules.
- `.cursor/skills/<name>/SKILL.md` — full skill procedures.

## Key Libraries

- **Alpine.js 3.14:** declarative state (`x-data`, `@event`, `x-show`, `x-transition`, `$persist`,
  `x-cloak`). Loaded globally.
- **Liquid AJAX Cart 2.1.1:** cart mutations via `data-ajax-cart-*` attributes and `<ajax-cart-*>`
  elements; consume the `liquid-ajax-cart:request-end` event.
- **Swiper 7.4.1:** loaded conditionally in `theme.liquid`. Any section using Swiper must confirm
  the `theme.liquid` template whitelist covers the template where the section appears.

## Docs

VitePress site lives in `docs/`. Per-section and per-snippet markdown go in `docs/sections/` and
`docs/snippets/`.
