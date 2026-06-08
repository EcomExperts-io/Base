# Architecture

A system-level map of how the Base theme fits together: how the layout, section groups,
templates, sections, snippets, and blocks relate, and how the CSS-variable system and Liquid AJAX
Cart thread through it all.

This page describes what is **actually** in the repository as of writing. File paths are real —
open them to go deeper.

---

## The Render Chain

A storefront page is assembled top-down:

```
layout/theme.liquid
├── <head>
│   ├── {% render 'css-variables' %}      → injects the CSS custom-property system
│   ├── critical.css (preloaded)
│   ├── {% render 'meta-tags' %}
│   ├── Swiper CSS/JS (conditional — see below)
│   ├── Alpine.js + alpinejs-persist
│   ├── theme.js (type="module")
│   └── Liquid AJAX Cart initial-state JSON + import
└── <body>
    ├── {% sections 'header-group' %}     → sections/header-group.json
    ├── <main> … content_for_layout … </main>  → the page's JSON template
    └── {% sections 'footer-group' %}     → sections/footer-group.json
```

- **`layout/theme.liquid`** is the single HTML shell for every page (the `password.liquid` layout
  is the exception used for the storefront password page). It is intentionally short (~93 lines) —
  per `rules-of-engagement.mdc` it should stay ≤ ~300 lines and delegate to snippets/sections.
- **`content_for_layout`** (the Liquid object output in `<main>`) is where the matched template's sections render.
- **Section groups** (`sections/header-group.json`, `sections/footer-group.json`) are JSON files
  that compose the header and footer from sections, rendered via `{% sections 'header-group' %}`.

---

## Online Store 2.0 JSON Templates

Templates live in `templates/` and are mostly **JSON** (Online Store 2.0), with a few `.liquid`
templates for cases that need raw Liquid (e.g. `templates/gift_card.liquid`). Customer templates
live under `templates/customers/`.

A JSON template lists the **sections** (and their settings/block order) that render into
`content_for_layout` for that page type. Examples present in this repo:

- Core pages: `index.json`, `product.json`, `collection.json`, `cart.json`, `search.json`,
  `blog.json`, `article.json`, `page.json`, `list-collections.json`, `404.json`
- Many alternate page templates: `page.featured-collections.json`, `page.hero.json`,
  `page.shop-by-category.json`, `page.brand-story.json`, etc. (these let merchants assign a
  purpose-built layout to a page in the theme editor)

Because templates are data (JSON), the sections they reference are the unit of reuse — see below.

---

## Sections → Snippets

- **Sections** (`sections/*.liquid`) are the composable building blocks a merchant adds, orders,
  and configures in the theme editor. Each carries an inline `{% schema %}` (this repo has **no
  `schemas/` folder** and no build step — schemas are written directly in the `.liquid` file).
- Sections render reusable UI by calling **snippets**: `{% render 'component-<name>' %}`. Snippets
  live in `snippets/` and are prefixed `component-` (e.g. `component-product-card.liquid`).
- Naming is mirrored across asset types: a section's CSS/JS use the `section-` prefix
  (`assets/section-<name>.{css,js}`); a snippet's use the `component-` prefix
  (`assets/component-<name>.{css,js}`). See `naming-conventions.mdc`.

---

## Blocks: Theme Blocks vs. Section Blocks

There are two distinct "block" concepts:

1. **Theme blocks** — standalone files in `blocks/` (this repo ships `blocks/group.liquid` and
   `blocks/text.liquid`). They are flat (no `section-`/`component-` prefix), carry their own
   `{% schema %}` and `presets`, render `block.shopify_attributes` on the root element, and use inline
   `{% stylesheet %}` for deduplicated CSS. They can be nested into any section/block that opens a
   `{% content_for 'blocks' %}` region.
2. **Section blocks** — blocks declared inside a single section's `{% schema %}` `"blocks"` array.
   They only exist within that section.

### `{% content_for 'blocks' %}` and nested composition

A section (or a theme block like `blocks/group.liquid`) declares a region with
`{% content_for 'blocks' %}`. The theme editor then lets a merchant drop theme blocks (and `@theme`
/`@app` blocks) into that region, and they render in place. This is what enables **nested
composition** — e.g. a `group` block containing `text` blocks — without bespoke Liquid for each
combination. Reference templates for this pattern live in
`.cursor/rules/examples/block-example-group.liquid` and `block-example-text.liquid`.

> The closing quote in `{% content_for 'blocks' %}` is mandatory — a missing quote is a known
> historical typo (see the `pr-review` skill / Pass A repairs).

---

## The CSS Custom-Property System

`snippets/css-variables.liquid` (rendered in `<head>` via `{% render 'css-variables' %}`) generates
the theme's design tokens at runtime from theme settings:

- Loops `settings.color_schemes` and emits one block per scheme:
  `:root, .color-<scheme.id> { --color-background: r,g,b; --color-foreground: r,g,b; … }`. Colors
  are emitted as **RGB triplets** so they can be consumed with opacity, e.g.
  `rgb(var(--color-background))` and `rgba(var(--color-foreground), 0.75)`.
- Emits typography/layout tokens on `:root` (`--font-body-*`, `--font-heading-*`, `--page-width`,
  `--page-margin`) and `@font-face` rules for the body/heading fonts.

Sections opt into a scheme by adding a `color-<scheme>` class (from `section.settings.color_scheme`) to their wrapper,
which re-points the `--color-*` variables for everything inside. See `design-system.md` for the
full token catalogue and `snippets/css-variables.md` for a line-by-line breakdown.

> Note: some rule files refer to this file as `theme-styles-variables.liquid`; the real file in
> this repo is `snippets/css-variables.liquid`. Treat `css-variables.liquid` as authoritative.

---

## Liquid AJAX Cart Integration

Cart state is shared across the whole page without custom fetch code for mutations:

- **Bootstrap** — `layout/theme.liquid` emits the initial cart as JSON in a
  `data-ajax-cart-initial-state` script tag and imports `assets/liquid-ajax-cart-v2.1.1.js` as a
  module.
- **Auto-updating regions** — markup marked `data-ajax-cart-section` (e.g. in the cart section and
  cart drawer) is re-rendered automatically after any cart mutation.
- **Bindings** — `data-ajax-cart-bind="item_count"` keeps elements like the header cart count in
  sync.
- **Events** — after a request completes, Liquid AJAX Cart fires `liquid-ajax-cart:request-end`.
  `assets/component-product-info.js` listens for it, and on a successful add dispatches its own
  `item-added-to-cart` event; the Alpine `cartDrawer` store opens the drawer in response.

See `integrations.md` for the attribute-level reference and `javascript-patterns.md` for how the
JS and Alpine layers communicate.

---

## Where AI Tooling Lives

- `.cursor/rules/*.mdc` — glob-scoped coding standards (Cursor)
- `.cursor/references/*.md` — long-form CSS/JS references behind the slim rules
- `.cursor/skills/<name>/SKILL.md` and `.claude/skills/<name>/SKILL.md` — invokable workflows
- `AGENTS.md` / `CLAUDE.md` — cross-agent project backbone

See `ai-tooling.md` for the full map.
